__author__ = 'Piia Hartikka 013866037'

import web
import json
import subprocess
import requests
import atexit

GAME_SERVER_API_PORT_RANGE_START = 10000
GAME_SERVER_RECEIVER_PORT_RANGE_START = 15000

class MainServerApi(web.application):
    def __init__(self):
        self.game_server_processes = []
        self.game_servers = []
        self.next_game_server_api_port = GAME_SERVER_API_PORT_RANGE_START
        self.next_game_server_receiver_port = GAME_SERVER_RECEIVER_PORT_RANGE_START
        atexit.register(self._stop_child_processes)
        parent = self

        urls = (
            '/game/join', 'join',
        )

        class join:
            def POST(self):
                api_port, receiver_port = parent._find_game_server()
                message = {'game_address': f'localhost:{receiver_port}'}
                web.header('Content-Type', 'application/json')
                return json.dumps(message)
        
        super().__init__(urls, {'join': join})

    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('localhost', port))

    def _start_new_game_server(self):
        api_port = self.next_game_server_api_port
        self.next_game_server_api_port += 1
        receiver_port = self.next_game_server_receiver_port
        self.next_game_server_receiver_port += 1
        self.game_server_processes.append(
            subprocess.Popen(['python3', 'game_server.py', str(api_port), str(receiver_port)])
        )
        self.game_servers.append((api_port, receiver_port))
        return api_port, receiver_port

    def _find_game_server(self):
        for game_server_api_port, game_server_receiver_port in self.game_servers:
            response = requests.get(f'http://localhost:{game_server_api_port}/stats')
            response.raise_for_status()
            body = response.json()
            if body['count'] < body['capacity']:
                return game_server_api_port, game_server_receiver_port
        
        return self._start_new_game_server()


    def _stop_child_processes(self):
        for process in self.game_server_processes:
            process.terminate()

def main():
    main_server = MainServerApi()
    main_server.run()

if __name__ == '__main__':
    main()