__author__ = 'Piia Hartikka 013866037'

import game_server

RECEIVER_ADDRESS = ('localhost', 9000)
BROADCASTER_ADDRESS = ('localhost', 9001)
API_ADDRESS = ('127.0.0.1', 9102)
CAPACITY = 3

def main():
    g = game_server.GameServer(RECEIVER_ADDRESS, BROADCASTER_ADDRESS, API_ADDRESS, CAPACITY)
    g.start()

if __name__ == "__main__":
    main()