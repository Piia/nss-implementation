__author__ = 'Piia Hartikka 013866037'

import threading
import socket
from PyCRC.CRC32 import CRC32
import time
import game_server_api
from datetime import datetime
import argparse

DATAGRAM_MAX_SIZE = 60000
CLIENT_MESSAGE_MAX_SIZE = 1000
CLIENT_TIMEOUT_THRESHOLD = 15
CAPACITY = 3

class ReceiverThread(threading.Thread):
    def __init__(self, address, game_state, heartbeats):
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.address)
        self.game_state = game_state
        self.heartbeats = heartbeats
        threading.Thread.__init__(self)

    def run(self):
        while True:
            data, client_address = self.socket.recvfrom(CLIENT_MESSAGE_MAX_SIZE)
            byte_checksum = data[0:4]
            byte_message = data[4:]
            decoded_checksum = self.decode_checksum(byte_checksum)
            calc_checksum = CRC32().calculate(byte_message)
            
            print(f"receiving from address {client_address}")

            self.heartbeats[client_address] = datetime.now()

            if calc_checksum == decoded_checksum:
                coords = self.decode_payload(byte_message)
                self.game_state[client_address] = coords

    def decode_checksum(self, byte_checksum):
        return int.from_bytes(byte_checksum, 'little')

    def decode_payload(self, byte_message):
        x_field = byte_message[0:4]
        y_field = byte_message[4:]
        return int.from_bytes(x_field, 'little'), int.from_bytes(y_field, 'little')

class BroadcasterThread(threading.Thread):
    def __init__(self, address, game_state, heartbeats):
        self.game_state = game_state
        self.heartbeats = heartbeats
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(address)
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(0.05)
            game_state = self.game_state.copy()
            for address in game_state.keys():
                if self.has_timed_out(address):
                    del self.game_state[address]
                    del self.heartbeats[address]
                    continue

                state = self.game_state.copy()
                del state[address]
                encoded_message = self.encode_message(state.values())
                encoded_checksum = self.encode(CRC32().calculate(encoded_message))
                self.send(address, encoded_checksum + encoded_message)

    def send(self, address, message):
        self.socket.sendto(message, address)

    def encode_message(self, coords_list):
        byte_array = b''
        for x, y in coords_list:
            byte_array += self.encode(x)
            byte_array += self.encode(y)
        return byte_array

    def encode(self, int_number):
        return int_number.to_bytes(4, byteorder='little')

    def has_timed_out(self, client_address):
        now = datetime.now()
        return (now - self.heartbeats[client_address]).total_seconds() > CLIENT_TIMEOUT_THRESHOLD

class GameServer(object):
    def __init__(self, receiver_address, broadcaster_address, api_address, capacity):
        self.api_address = api_address
        self.game_state = {}
        self.heartbeats = {}
        self.receiver = ReceiverThread(receiver_address, self.game_state, self.heartbeats)
        self.broadcaster = BroadcasterThread(broadcaster_address, self.game_state, self.heartbeats)
        self.capacity = capacity

        
    def start(self):
        self.receiver.start()
        self.broadcaster.start()
        api_server = game_server_api.GameServerApi(self.game_state, self.capacity)
        api_server.run(port = self.api_address[1])


def main(args):
    receiver_addr = ('localhost', args.receiver_port)
    broadcaster_addr = ('localhost', 0)
    api_addr = ('localhost', args.api_port)
    g = GameServer(receiver_addr, broadcaster_addr, api_addr, CAPACITY)
    g.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("api_port", type=int, help="Port that the game server api will listen")
    parser.add_argument(
        "receiver_port",
        type=int,
        help="Port that the game server uses to receive client messages")
    args = parser.parse_args()
    main(args)