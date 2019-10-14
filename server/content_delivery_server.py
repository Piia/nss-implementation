from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

FTP_PORT = 2222
FTP_USER = 'gamer'
FTP_PASSWORD = 'gamer_password'
FTP_DIRECTORY = f'{os.getcwd()}/assets'

# FROM: https://serverpilot.io/docs/how-to-run-a-simple-ftp-server

def main():
    authorizer = DummyAuthorizer()
    # list+retrieve permissions
    authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIRECTORY, perm='lr')

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "content_delivery_server is ready"

    address = ('', FTP_PORT)
    server = FTPServer(address, handler)

    server.max_cons = 256
    server.max_cons_per_ip = 5

    server.serve_forever()


if __name__ == '__main__':
    main()