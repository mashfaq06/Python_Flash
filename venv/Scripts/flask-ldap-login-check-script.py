#!C:\Users\Shahista\PycharmProjects\NetworkingFrontEnd\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'flask-ldap-login==0.3.0','console_scripts','flask-ldap-login-check'
__requires__ = 'flask-ldap-login==0.3.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('flask-ldap-login==0.3.0', 'console_scripts', 'flask-ldap-login-check')()
    )
