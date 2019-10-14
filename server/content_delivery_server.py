from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import argparse


def main(args):
    authorizer = DummyAuthorizer()
    # list+retrieve permissions
    authorizer.add_user(args.user, args.password, args.directory, perm='lr')

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "content_delivery_server is ready"

    address = ('', args.port)
    server = FTPServer(address, handler)

    server.max_cons = 256
    server.max_cons_per_ip = 5

    server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Port that the content delivery server api will listen")
    parser.add_argument("user", help="Ftp username")
    parser.add_argument("password", help="Ftp user password")
    parser.add_argument("directory", help="Directory that contains the files for the ftp server")
    args = parser.parse_args()
    main(args)