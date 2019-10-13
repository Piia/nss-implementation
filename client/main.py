__author__ = 'Piia Hartikka 013866037'

import client
import game
import requests

MAIN_SERVER_ADDRESS = ('localhost', 8080)

def join_game():
    response = requests.post(f'http://{MAIN_SERVER_ADDRESS[0]}:{MAIN_SERVER_ADDRESS[1]}/game/join', data={})
    response.raise_for_status()
    body = response.json()
    host, port = body['game_address'].split(':')
    port = int(port)
    return host, port

def main():
    game_address = join_game()
    c = client.Client(game_address)
    g = game.Game(c.inbound_queue, c.outbound_queue)
    g.start()

if __name__ == "__main__":
    main()