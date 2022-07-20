#!/usr/bin/env python3
#
#    Copyright (C) 2019 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>

# Inspired by Nikos Fotoulis public domain code and flyte/upnpclient

# Useful actions:
# GetExternalIPAddress
# GetDefaultConnectionService
# GetStatusInfo
# GetNATRSIPStatus
# GetTotalBytesReceived / GetTotalBytesSent
# GetGenericPortMappingEntry 0..x
# Browse 0 BrowseDirectChildren '*'

# Useful subscriptions
# SUBSCRIBE /evt/IPConn HTTP/1.1
# Host: 10.10.10.1:50628
# Callback: <http://10.10.10.100:4200/ServiceProxy5>
# NT: upnp:event

"""upnp - Find and use devices via UPnP"""

__all__ = [
    'Action',
    'Device',
    'Service',
    'SEARCH_TARGET',
    'SOAPCall',
    'UpnpError',
    'UpnpValueError',
    'UpnpAttributeError',
    'cli',
    'discover',
]


import argparse
import collections
import enum
import logging
import os.path
import platform
import re
import socket
import sys
import typing as t
import urllib.parse

# noinspection PyPep8Naming
import lxml.etree as ET
import requests

__title__ = 'upnptool'
__version__ = '2022.07'

# For most of these constants, see ref/UPnP-arch-DeviceArchitecture-v2.0-20200417-1.pdf
SSDP_MAX_MX:        int = 5  # Max reply delay, per 2.0 spec. NOT a timeout!
SSDP_BUFFSIZE:      int = 8192
SSDP_ADDR:          str = '239.255.255.250'
SSDP_PORT:          int = 1900
SSDP_TTL:           int = 2  # Spec: should default to 2 and should be configurable

SSDP_TIMEOUT:       int = 3  # Not related to spec, and not a total timeout
SSDP_SOURCE_PORT:   int = 4201  # Not in spec. 0 for random or fixed for firewalls

"""
# REF: UDA2/1.3.2
USER-AGENT
Allowed. Specified by UPnP vendor. String. Field value shall begin with the following “product tokens” (defined
by HTTP/1.1). The first product token identifes the operating system in the form OS name/OS version, the
second token represents the UPnP version and shall be UPnP/2.0, and the third token identifes the product
using the form product name/product version. For example, “USER-AGENT: unix/5.1 UPnP/2.0 MyProduct/1.0”.
"""
SSDP_USER_AGENT:    str = ' '.join((
    '/'.join((__title__, __version__)),
    "UPnP/2.0",
    # Linux/5.4.0-120-generic
    '/'.join(map(platform.uname().__getitem__, (0, 2))),
))


log = logging.getLogger(__name__)


# noinspection PyPep8Naming
class SEARCH_TARGET(str, enum.Enum):
    """Commonly-used device and service types for UPnP discovery"""
    ALL = 'ssdp:all'
    ROOT = 'upnp:rootdevice'
    GATEWAY = 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'
    BASIC = 'urn:schemas-upnp-org:device:Basic:1'
    MEDIA_SERVER = 'urn:schemas-upnp-org:device:MediaServer:1'
    WAN_CONNECTION = 'urn:schemas-upnp-org:service:WANIPConnection:1'


class DIRECTION(str, enum.Enum):
    IN = 'in'
    OUT = 'out'


# Exceptions
class UpnpError(Exception):
    pass


class UpnpValueError(UpnpError, ValueError):
    pass


class UpnpAttributeError(UpnpError, AttributeError):
    pass


class XMLElement:
    """Wrapper for a common XML API using either LXML, ET or Minidom"""
    # Note: XML sucks! It's an incredibly complex format, and lxml is *very* picky
    # - Serialized XML is always bytes, not str, per the spec
    # - When converted to str (unicode), there's no <?xml ..?> declaration
    # - pretty_print=True only works if parsed with remove_blank_text=True
    # - Dealing with namespaces, many approaches:
    #     e.find('{fully.qualified.namespace}tag')
    #     e.find('{*}tag'), using a literal *
    #     e.find('X:tag', namespaces=e.nsmap), X being (usually) a single lowercase letter
    @classmethod
    def fromstring(cls, data: t.Union[str, bytes]):
        try:
            return cls(ET.fromstring(data, parser=ET.XMLParser(remove_blank_text=True)))
        except ET.XMLSyntaxError as e:
            raise UpnpValueError(e)

    @classmethod
    def fromurl(cls, url: str):
        log.debug("Parsing %s", url)
        # lxml.etree.parse() chokes on URLs if server sets Content-Type header as
        # 'text/xml; charset="utf-8"', as seen on Ubuntu's MiniDLNA rootDesc.xml
        # So for now we use requests to download and read bytes content.
        # Cannot use .text (unicode) content as response contains <?xml ...?>,
        # which lxml chokes if present on unicode strings
        # return cls(ET.parse(url))
        try:
            return cls.fromstring(requests.get(url).content)
        except requests.RequestException as e:
            raise UpnpError(e)

    @classmethod
    def prettify(cls, s):
        return cls.fromstring(s).pretty()

    def __init__(self, element):
        if hasattr(element, 'getroot'):  # ElementTree instead of Element
            element = element.getroot()
        self.e: ET.Element = element

    def findtext(self, tagpath: str) -> str:
        return self.e.findtext(tagpath, namespaces=self.e.nsmap)

    def find(self, tagpath):
        e = self.e.find(tagpath, namespaces=self.e.nsmap)
        if e is not None:
            return self.__class__(e)

    def findall(self, tagpath):
        for e in self.e.findall(tagpath, namespaces=self.e.nsmap):
            yield self.__class__(e)

    def pretty(self) -> str:
        # ET.tostring().decode() is not the same as ET.tostring(..., encoding=str)
        # The latter errors when using xml_declaration=True
        return ET.tostring(self.e, pretty_print=True,
                           xml_declaration=True, encoding='utf-8').decode()

    @property
    def text(self):
        return self.e.text

    def __repr__(self):
        return repr(self.e)

    def __str__(self):
        return str(self.e)


class SSDP:
    """Device/Service from SSDP M-Search response"""

    def __init__(self, data: str, addr: str = ""):
        self.data = data
        self.headers = util.parse_headers(data)

        loc = self.headers.get('LOCATION')
        locaddr = util.hostname(loc)
        if addr and addr != locaddr:
            log.warning("Address and Location mismatch: %s, %s", addr, loc)
        self.addr = addr or locaddr

    @property
    def info(self):
        keys = ['SERVER', 'LOCATION', 'USN']
        if not self.is_root:
            keys.append('ST')
        return {_: self.headers.get(_) for _ in keys}

    @property
    def is_root(self):
        return self.headers.get('ST') == SEARCH_TARGET.ROOT

    def __repr__(self):
        desc = ', '.join(('='.join((k.lower(), repr(v)))
                         for k, v in self.info.items()))
        return f'<{self.__class__.__name__}({desc})>'


class Device:
    """UPnP Device"""
    @classmethod
    def from_ssdp(cls, ssdp: SSDP):
        location = ssdp.headers.get('LOCATION')
        if not location:
            raise UpnpValueError(f"Empty SSDP LOCATION: {ssdp}")
        return cls(location, ssdp=ssdp)

    def __init__(self, location: str, *, ssdp: SSDP = None):
        self.location: str = location
        self.ssdp:     t.Optional[SSDP] = ssdp
        self.xmlroot:  XMLElement = XMLElement.fromurl(self.location)
        self.url_base: str = (self.xmlroot.findtext('URLBase') or
                              util.urljoin(self.location, '.'))
        util.attr_tags(self, self.xmlroot, 'device', '', tags=(
            'deviceType',        # Required
            'friendlyName',      # Required
            'manufacturer',      # Required
            'manufacturerURL',   # Allowed
            'modelDescription',  # Recommended
            'modelName',         # Required
            'modelNumber',       # Recommended
            'modelURL',          # Allowed
            'serialNumber',      # Recommended
            'UDN',               # Required
            'UPC',               # Allowed
        ))

        if self.ssdp and self.ssdp.headers.get('LOCATION') != self.location:
            log.warning("URL and Location mismatch: %s, %s",
                        self.location, self.ssdp.headers.get('LOCATION'))

        self.services: t.Dict[str, Service] = {}
        self.actions:  t.Dict[str, Action] = {}  # Maybe should be a property
        for node in self.xmlroot.findall('.//device/serviceList/service'):
            service = Service(self, node)
            if any(service.name in _ for _ in self.services):
                log.warning("Duplicated service in Device %r: %s",
                            self.udn, service.name)
            self.services[service.service_type] = service
            setattr(self, service.name, service)
            dupes = self.actions.keys() & service.actions  # 1337!
            if dupes:
                log.warning("Duplicated action(s) in Device %r: %s",
                            self.udn, dupes)
            self.actions.update(service.actions)

    @property
    def name(self):
        return self.friendly_name or self.address

    @property
    def model(self):
        desc = self.model_description
        name = self.model_name
        if name in desc:
            name = ""
        return " ".join(filter(None, (desc, name)))

    @property
    def fullname(self):
        name = self.name
        model = self.model
        if model and not model == name:
            name += f" ({model})"
        return name

    @property
    def address(self):
        return (self.ssdp and self.ssdp.addr) or util.hostname(self.location)

    def __getitem__(self, key: str) -> 'Service':
        try:
            if key in self.services:
                return self.services[key]
            if isinstance(key, SEARCH_TARGET):
                return self.services[key.value]
        except KeyError:
            return getattr(self, key)

    def __getattr__(self, key: str) -> 'Service':
        raise UpnpAttributeError(f"Device '{self.udn}' has no service '{key}'")

    def __str__(self):
        return self.fullname

    def __repr__(self):
        r = f'{self.udn!r}, {self.location!r}, {self.friendly_name!r}'
        return '<{0.__class__.__name__}({1})>'.format(self, r)


class Service:
    def __init__(self, device: Device, service: XMLElement):
        self.device:  Device = device
        util.attr_tags(self, service, '', device.url_base, tags=(
            'serviceType',  # Required
            'serviceId',    # Required
            'controlURL',   # Required
            'eventSubURL',  # Required
            'SCPDURL',      # Required
        ))
        self.xmlroot = XMLElement.fromurl(
            util.urljoin(self.device.url_base, self.scpdurl))
        self.actions: t.Dict[str, Action] = {}
        for node in self.xmlroot.findall('actionList/action'):
            action = Action(self, node)
            self.actions[action.name] = action
            setattr(self, action.name, action)

    @property
    def name(self) -> str:
        return self.service_type.split(':')[-2]

    def __getitem__(self, key: str) -> 'Action':
        try:
            return self.actions[key]
        except KeyError:
            return getattr(self, key)

    def __getattr__(self, key: str) -> 'Action':
        raise UpnpAttributeError(
            f"Service '{self.name}' has no action '{key}'")

    def __str__(self):
        return self.name

    def __repr__(self):
        attrs = {
            'service_type':  'type',
            'scpdurl':       'SCPD',
            'control_url':   'CTRL',
            'event_sub_url': 'EVT',
        }
        r = util.formatdict(
            {attrs[k]: v for k, v in vars(self).items() if k in attrs})
        return f'<{self.__class__.__name__}({r})>'


# noinspection PyUnr esolvedReferences
class Action:
    def __init__(self, service: Service = None, action: XMLElement = None):
        self.service = service
        self.name = action.findtext('name')

        self.inputs = []
        self.outputs = []
        for arg in action.findall('argumentList/argument'):
            argname = arg.findtext('name')
            if arg.findtext('direction') == 'in':
                self.inputs.append(argname)
            else:
                self.outputs.append(argname)

    def call(self, *args, **kwargs) -> 'util.NamedTuple':
        if len(args) > len(self.inputs):
            raise UpnpValueError("{}() takes {} arguments but {} were given".format(
                self.name, len(self.inputs), len(args)))
        kw = {_[0]: _[1] for _ in zip(self.inputs, args)}
        kw.update(kwargs)
        xml_root = SOAPCall(self.service.control_url, self.service.service_type,
                            self.name, **kw)
        out = {k: xml_root.e .findtext(f'.//{k}') for k in self.outputs}
        return util.NamedTuple(self.name, self.outputs)(**out)

    def __call__(self, *args, **kwargs) -> 'util.NamedTuple':
        return self.call(*args, **kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return (f"<{self.__class__.__name__} {self.name}({', '.join(self.inputs)})"
                f" -> [{', '.join(self.outputs)}]>")


# noinspection PyPep8Naming
class util:
    """A bunch of utility functions and helpers, cos' I'm too lazy for a new module"""
    _re_snake_case = re.compile(
        r'((?<=[a-z\d])[A-Z]|(?!^)[A-Z](?=[a-z]))')  # (?!^)([A-Z]+)

    @classmethod
    def snake_case(cls, camelCase: str) -> str:
        return re.sub(cls._re_snake_case, r'_\1', camelCase).lower()

    @classmethod
    def attr_tags(cls, obj, node: XMLElement,
                  tagpath: str = "", baseurl: str = "", tags: tuple = ()) -> None:
        """Magic method to set attributes from XML tag(name)s
        Tag names must be leafs, not paths, with optional <tagpath> prefix.
        Automatically convert names from camelCaseURL to camel_case_url.
        URLs, judged by URL-ending tag name, are joined with <baseurl>
        """
        if tagpath:
            tagpath += '/'
        for tag in tags:
            attr = cls.snake_case(tag)
            value = node.findtext(tagpath+tag) or ""
            if value and baseurl and attr.endswith('url'):
                value = cls.urljoin(baseurl, value)
            setattr(obj, attr, value)

    @staticmethod
    def formatdict(d: dict, itemsep=', ', pairsep='=', valuefunc=repr) -> str:
        return itemsep.join((pairsep.join((k, valuefunc(v))) for k, v in d.items()))

    @staticmethod
    def parse_headers(data: str) -> dict:
        headers = {}
        for line in data.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip().upper()] = v.strip()
        return headers

    @staticmethod
    def hostname(url: str) -> str:
        return urllib.parse.urlparse(url).hostname

    @staticmethod
    def urljoin(base: str, url: str) -> str:
        return urllib.parse.urljoin(base, url)

    @staticmethod
    def clamp(value: int, lbound: int = None, ubound: int = None) -> int:
        if lbound is not None:
            value = max(value, lbound)
        if ubound is not None:
            value = min(value, ubound)
        return value

    @staticmethod
    def get_network_ip():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # Changed from s.connect(('<broadcast>', 0)) to s.connect(('0.0.0.0', 6969))
            s.connect(('', 6969))
            return s.getsockname()[0]

    @staticmethod
    def NamedTuple(*a, **kw):
        """Named Tuple that also allows instance dict-like access foo['bar']"""
        # Change *a to "Hello"
        NT = collections.namedtuple("Hello", **kw)
        NT._getindex = NT.__getitem__
        NT.__getitem__ = lambda self, x: \
            self._getindex(x) if isinstance(x, int) else getattr(self, x)
        return NT


def discover(
        search_target: t.Union[str, SEARCH_TARGET] = SEARCH_TARGET.ALL, *,
        dest_addr: str = SSDP_ADDR,
        timeout: int = SSDP_TIMEOUT,
        ttl: int = SSDP_TTL,
        unicast: bool = False,
        source_port: int = SSDP_SOURCE_PORT,
) -> t.Iterable[Device]:
    """Send an SSDP M-SEARCH message and return received Devices
    Multicast is used by default even for unicast addresses, as some devices
    (namely old TP-Link routers) only reply to multicast on 239.255.255.250
    """
    if isinstance(search_target, SEARCH_TARGET):
        search_target = search_target.value

    if unicast and dest_addr == SSDP_ADDR:
        log.warning("unicast with the default multicast address makes no sense")

    addr = (dest_addr if unicast else SSDP_ADDR, SSDP_PORT)
    timeout = util.clamp(timeout, 1)
    mx = util.clamp(timeout, 1, SSDP_MAX_MX)

    data = re.sub(r'[\t ]*\r?\n[\t ]*', '\r\n', f"""
            M-SEARCH * HTTP/1.1
            HOST: {SSDP_ADDR}:{SSDP_PORT}
            MAN: "ssdp:discover"
            MX: {mx}
            ST: {search_target}
            USER-AGENT: {SSDP_USER_AGENT}
            CPFN.UPNP.ORG: MestreLion UPnP Library
    """.lstrip())
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        # Note: TTL has a *very* different meaning on multicast packets!
        for ttl_type in (socket.IP_TTL, socket.IP_MULTICAST_TTL):
            sock.setsockopt(socket.IPPROTO_IP, ttl_type, ttl)
        sock.settimeout(timeout)
        log.info("Discovering UPnP devices and services: %s", search_target)
        log.debug("Broadcasting discovery search to %s:\n%s", addr, data)
        if source_port:
            sock.bind((util.get_network_ip(), source_port))
        sock.sendto(bytes(data, 'ascii'), addr)

        devices = set()
        while True:
            try:
                data, (addr, port) = sock.recvfrom(SSDP_BUFFSIZE)
                data = data.decode()
            except socket.timeout:
                break

            log.debug("Incoming search response from %s:%s\n%s",
                      addr, port, data)
            ssdp = SSDP(data, addr)
            location = ssdp.headers.get('LOCATION')

            if location in devices:
                # TODO: drop this log after code is mature and skip dupes silently
                log.debug("Ignoring duplicated device: %s", ssdp)
                continue
            devices.add(location)

            # Some unrelated devices reply to discovery even when setting a
            # specific ST in M-SEARCH
            if (
                search_target != SEARCH_TARGET.ALL and
                search_target != ssdp.headers.get('ST')
            ):
                log.warning("Ignoring non-target device: %s", ssdp)
                continue

            # Skip if reply addr does not match requested one on multicast
            if not (unicast or (dest_addr in (SSDP_ADDR, ssdp.addr))):
                continue

            try:
                log.info("Discovered: %s", ssdp)
                yield Device.from_ssdp(ssdp)
            except UpnpValueError as e:
                log.debug("Error reading device from %s: %s", ssdp, e)
            except UpnpError as e:
                log.warning("Error reading device from %s: %s", ssdp, e)


# noinspection PyPep8Naming
def SOAPCall(url, service, action, **kwargs) -> XMLElement:
    # TODO: Sanitize kwargs based on input types
    # TODO: Convert output values based on output types
    xml_args = "\n".join(f"<{k}>{v}</{k}>" for k, v in kwargs.items())
    data = f"""
        <?xml version="1.0"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:{action} xmlns:u="{service}">{xml_args}</u:{action}>
        </s:Body>
        </s:Envelope>
    """.strip()
    headers = {
        'SOAPAction': f'"{service}#{action}"',
        'Content-Type': 'text/xml; charset="utf-8"',
    }
    log.info("Executing SOAP Action: %s.%s(%s) @ %s",
             service, action, util.formatdict(kwargs), url)
    log.debug(headers)
    log.debug(XMLElement.prettify(data))
    r = requests.post(url, headers=headers, data=data)
    log.debug(r.request.headers)
    log.debug(r.headers)
    xml_root = XMLElement.fromstring(r.content)
    log.debug(xml_root.pretty())

    # This is very strict. if things go wrong, replace with:
    # return xml_root.find(f'.//{{{service}}}*'), or just return xml_root
    return xml_root.find(f'{{*}}Body/{{{service}}}{action}Response')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet',
                       dest='loglevel',
                       const=logging.WARNING,
                       default=logging.INFO,
                       action="store_const",
                       help="Suppress informative messages.")

    group.add_argument('-v', '--verbose',
                       dest='loglevel',
                       const=logging.DEBUG,
                       action="store_const",
                       help="Verbose mode, output extra info.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--st',
                       dest='st',
                       default=SEARCH_TARGET.ALL.value,
                       help="Search target (ST) paramenter for SSDP discovery."
                            " [Default: %(default)r]")
    for st in SEARCH_TARGET:
        # noinspection PyUnresolvedReferences
        group.add_argument(f"--{st.name.lower().replace('_', '-')}",
                           dest='st',
                           const=st.value,
                           action="store_const",
                           help=f"Alias for --st %(const)r")

    parser.add_argument('-d', '--destination',
                        default=SSDP_ADDR,
                        help="Destination IP address for SSDP discovery."
                             " [Default: %(default)r (multicast)]")

    parser.add_argument('-u', '--unicast',
                        default=False,
                        action='store_true',
                        help="Force unicast SSDP search when using --destination"
                             " instead of filtering the multicast replies.")

    parser.add_argument('-p', '--port',
                        default=SSDP_SOURCE_PORT,
                        type=int,
                        help="SSDP source port. 0 for random."
                             " [Default: %(default)s]")

    parser.add_argument('-t', '--timeout',
                        default=3,
                        type=int,
                        help="SSDP search discovery timeout after no replies."
                             " [Default: %(default)s]")

    parser.add_argument('-f', '--full',
                        default=False,
                        action='store_true',
                        help="List Devices, Services and Actions."
                             " [Default: List Devices only]")

    parser.add_argument('-a', '--action',
                        help="SOAP action to perform.")

    parser.add_argument(nargs='*',
                        dest='args',
                        help="Arguments to SOAP Action")

    args = parser.parse_args(argv)
    args.debug = args.loglevel == logging.DEBUG

    return args


def cli(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-5.5s: %(message)s')
    log.debug(args)

    for device in discover(
        args.st,
        timeout=args.timeout,
        dest_addr=args.destination,
        unicast=args.unicast,
        source_port=args.port,
    ):
        if args.action:
            action = device.actions[args.action]
            if action.name.lower() == args.action.lower():
                log.info("Executing on %s: %s.%s(%s)",
                         device, action.service, action, args.args)
                print(action(*args.args))
                return
            continue

        print(repr(device))
        print(f"{device} [{device.manufacturer}]")
        if not args.full:
            print()
            continue

        for service in device.services.values():
            print(f"\t{service!r}")
            for action in service.actions.values():
                print(f"\t\t{action!r}")
        print()


if __name__ == "__main__":
    log = logging.getLogger(os.path.basename(__file__))
    try:
        sys.exit(cli(sys.argv[1:]))
    except UpnpError as err:
        log.error(err)
        sys.exit(1)
