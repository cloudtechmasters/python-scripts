# python-scripts

1. Install Required Packages
Since Python 2.7 is deprecated, you need to pin specific versions of libraries that support it.

pip install requests==2.23.0 urllib3==1.26.6 certifi==2020.12.5 idna==2.10 chardet==3.0.4 pyOpenSSL==19.1.0 ndg-httpsclient==0.5.1 pyasn1==0.4.8
Explanation of packages and versions:

requests==2.23.0: The last compatible version of requests for Python 2.7.
urllib3==1.26.6: A version that supports Python 2.7 but avoids SSL issues.
certifi==2020.12.5: Provides a trusted CA certificate bundle.
idna==2.10: Supports domain name resolution.
chardet==3.0.4: Character encoding detection.
pyOpenSSL==19.1.0: Enables TLS/SSL communication in Python.
ndg-httpsclient==0.5.1: Helps with SSL/TLS connections.
pyasn1==0.4.8: Required for cryptographic operations
