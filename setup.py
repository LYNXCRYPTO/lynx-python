from gettext import install
from setuptools import setup, find_packages

deps = {
    'lynx': [
        "eth-typing>=3.1.0,<4.0.0",
        "eth-utils>=2.0.0,<3.0.0",
        "rlp>=3,<4",
        "hdwallet>=1.16.0,<2.1.1",
    ],
    # The eth-extra sections is for libraries that the evm does not
    # explicitly need to function and hence should not depend on.
    # Installing these libraries may make the evm perform better than
    # using the default fallbacks though.
    'lynx-extra': [
        "blake2b-py>=0.1.4,<0.2",
    ],
    'test': [
        "factory-boy==2.11.1",
        "hypothesis>=5,<6",
        "pexpect>=4.6, <5",
        "pytest>=6.2.4,<7",
        "pytest-asyncio>=0.10.0,<0.11",
        "pytest-cov==2.5.1",
        "pytest-timeout>=1.4.2,<2",
        "pytest-watch>=4.1.0,<5",
        "pytest-xdist==2.3.0",
    ],
    'lint': [
        "flake8==3.8.2",
        "flake8-bugbear==20.1.4",
        "mypy==0.910",
        "types-setuptools"
    ],
    'benchmark': [
        "termcolor>=1.1.0,<2.0.0",
        "web3>=4.1.0,<5.0.0",
    ],
    'doc': [
        "py-evm>=0.2.0-alpha.14",
        # We need to have pysha for autodoc to be able to extract API docs
        "pysha3>=1.0.0,<2.0.0",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "wheel",
        "setuptools>=36.2.0",
    ],
}

deps['dev'] = (
    deps['dev'] +
    deps['lynx'] +
    deps['test'] +
    deps['doc'] +
    deps['lint']
)

install_requires = deps['lynx']

setup(
    name='Lynx Python',
    version='0.0.1',
    description='A Python implementation of the Lynx Virtual Machine',
    author='Lynx Foundation',
    author_email='jordan@protocoding.com',
    url='https://github.com/LYNXCRYPTO/lynx-python',
    keywords='lynx blockchain lvm',
    include_package_data=True,
    py_modules=['lynx'],
    install_requires=install_requires,
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
