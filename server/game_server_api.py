__author__ = 'Piia Hartikka 013866037'

import web


class GameServerApi(web.application):
    
    def __init__(self, game_state):
        self.game_state = game_state
        parent = self

        urls = (
            '/clients/(.+)', 'clients'
        )

        class clients:
            def DELETE(self, address):
                parent._delete_client(address)
                return web.NoContent()
        
        super().__init__(urls, {'clients': clients})

    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('localhost', port))

    def _delete_client(self, client_address):
        host, port = client_address.split(':')
        port = int(port)
        del self.game_state[(host, port)]