__author__ = 'Piia Hartikka 013866037'

import client
import game
import requests
from ftplib import FTP
import os
import pathlib

MAIN_SERVER_ADDRESS = ('localhost', 8080)
ASSET_FOLDER = 'assets'

# join game in main server and returns game configuration
def join_game():
    response = requests.post(f'http://{MAIN_SERVER_ADDRESS[0]}:{MAIN_SERVER_ADDRESS[1]}/game/join', data={})
    response.raise_for_status()
    return response.json()

def extract_address(body, address_field):
    host, port = body[address_field].split(':')
    port = int(port)
    return host, port

# downloads files in game configuration
def download_files(configuration):
    host, port = extract_address(configuration, 'file_address')
    ftp = FTP()
    ftp.connect(host=host, port=port)
    ftp.login(user='gamer', passwd='gamer_password')
    print(ftp.getwelcome())

    for filename in configuration['files']:
        print(filename, end=': ')
        filepath = f'{ASSET_FOLDER}/{filename}'
        if not pathlib.Path(filepath).exists():
            file = open(filepath, 'wb')
            ftp.retrbinary(f'RETR {filename}', file.write)
            print('downloaded')
            file.close()
        else:
            print('already exists')

    ftp.quit()

def main():
    print('Starting game client...')
    game_configuration = join_game()
    game_address = extract_address(game_configuration, 'game_address')
    print('Joined game')
    print('Downloading assets...')
    download_files(game_configuration)
    c = client.Client(game_address)
    g = game.Game(c.inbound_queue, c.outbound_queue)
    print('CLIENT GAME START')
    g.start()
    print('Game exited')

if __name__ == "__main__":
    main()