import requests
import ipaddress
import miniupnpc
from lynx.constants import EXTERNAL_IP_HOSTS

class IP:
    
    @classmethod
    def get_external_ip(cls) -> str:
        """
        Attempts to resolve local machine's external IP address. First, the node 
        attempts to resolve their IP address by receiving information from their router
        using universal plug and play (upnp). If that fails, the node should attempt to resolve
        their address from numerous third party IP providers.
        """

        ip = cls.get_ip_from_upnp()
        if ip is None:
            ip = cls.get_ip_from_third_party()
        
        if ip is None:
            raise Exception('Unable to retreive external IP address.')

        return ip


    @classmethod 
    def is_valid_ip(cls, ip: str) -> bool:
        """
        Utility function used to check if the external IP address resolved is formatted correctly.
        """

        try:
            ipaddress.ip_address(ip)
            return True
            
        except:
            return False


    @classmethod
    def get_ip_from_upnp(cls) -> str:
        """
        Attempts to resolve the local machine's external IP address from their Internet Gateway Device (IGD)
        utilizing universal plug and play (upnp).
        """
        
        try:
            u = miniupnpc.UPnP()
            u.discoverdelay = 200
            u.discover()
            u.selectigd()
            ip = u.externalipaddress()

            if not cls.is_valid_ip(ip):
                return None

            return ip

        except:
            return None


    @classmethod
    def get_ip_from_third_party(cls) -> str:
        """Attempts to connect to an Internet host like Google to determine
        the local machine's external IP address.
        """

        try:
            for host in EXTERNAL_IP_HOSTS:
                ip_request = requests.request('GET', host)

                ip = ip_request.text

                if cls.is_valid_ip(ip):
                    return ip_request.text.strip()
            
            if not cls.is_valid_ip:
                return None

            return ip_request.text.strip()
        
        except:
            return None



