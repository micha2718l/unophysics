from pathlib import Path
import json
import collections

Server = collections.namedtuple('Server',
    ['address', 'username', 'password'])

__all__ = ['server_mongo_uno', 'server_ftp_uno', 'server_ftp_ull', 'server_api_uno']

try:
    with open(Path.home().glob('unophysics.cred') as f:
        creds = json.load(f)
except Exception as e:
    print(f'WARNING -- unophysics.cred file not available\n\t{str(e)}')
    creds = {}

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

server_api_uno = Server(
    address = creds.get('server_ftp_ull', {}).get('address', ''),
    username = creds.get('server_ftp_ull', {}).get('username', ''),
    password = creds.get('server_ftp_ull', {}).get('password', ''),
    )
