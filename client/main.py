__author__ = 'Piia Hartikka 013866037'

import client
import game

GAME_SERVER_ADDRESS = ('localhost', 9000)

def main():
    c = client.Client(GAME_SERVER_ADDRESS)
    g = game.Game(c.inbound_queue, c.outbound_queue)
    g.start()

if __name__ == "__main__":
    main()