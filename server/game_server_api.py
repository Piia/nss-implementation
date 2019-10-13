__author__ = 'Piia Hartikka 013866037'

import web
import json

class GameServerApi(web.application):
    
    def __init__(self, game_state, capacity):
        self.capacity = capacity
        self.game_state = game_state
        parent = self

        urls = (
            '/clients/(.+)', 'clients',
            '/stats', 'stats',
        )

        class clients:
            def DELETE(self, address):
                parent._delete_client(address)
                return web.NoContent()

        class stats:
            def GET(self):
                message = { 'capacity': parent.capacity, 'count': len(parent.game_state) }
                web.header('Content-Type', 'application/json')
                return json.dumps(message)
        
        super().__init__(urls, {'clients': clients, 'stats': stats})

    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('localhost', port))

    def _delete_client(self, client_address):
        host, port = client_address.split(':')
        port = int(port)
        del self.game_state[(host, port)]