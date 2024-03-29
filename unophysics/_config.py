from pathlib import Path
import json
import collections


Server = collections.namedtuple('Server',
    ['address', 'username', 'password'])

__all__ = ['server_mongo_uno', 'server_ftp_uno', 'server_ftp_ull', 'server_api_uno', 'load_credentials']

def load_credentials(cred_fn='unophysics.cred'):
    global server_mongo_uno, server_ftp_uno, server_ftp_ull, server_api_uno

    creds = {}
    paths = [(Path.home() / cred_fn), Path(cred_fn)]

    for p in paths:
        if p.exists():
            with open(p) as f:
                creds = json.load(f)
            break
    if not creds:
        print(f'WARNING --- {cred_fn} file not found')

    server_mongo_uno = Server(
        address = creds.get('server_mongo_uno', {}).get('address', ''),
        username = creds.get('server_mongo_uno', {}).get('username', ''),
        password = creds.get('server_mongo_uno', {}).get('password', ''),
        )

    server_ftp_uno = Server(
        address = creds.get('server_ftp_uno', {}).get('address', ''),
        username = creds.get('server_ftp_uno', {}).get('username', ''),
        password = creds.get('server_ftp_uno', {}).get('password', ''),
        )

    server_ftp_ull = Server(
        address = creds.get('server_ftp_ull', {}).get('address', ''),
        username = creds.get('server_ftp_ull', {}).get('username', ''),
        password = creds.get('server_ftp_ull', {}).get('password', ''),
        )

    server_api_uno = Server(
        address = creds.get('server_api_uno', {}).get('address', ''),
        username = creds.get('server_api_uno', {}).get('username', ''),
        password = creds.get('server_api_uno', {}).get('password', ''),
        )

load_credentials()
