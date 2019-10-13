__author__ = 'Piia Hartikka 013866037'

import threading
import socket
from PyCRC.CRC32 import CRC32
import time
import game_server_api


DATAGRAM_MAX_SIZE = 60000
CLIENT_MESSAGE_MAX_SIZE = 1000

class ReceiverThread(threading.Thread):
    def __init__(self, address, game_state):
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.address)
        self.game_state = game_state
        threading.Thread.__init__(self)

    def run(self):
        while True:
            data, client_address = self.socket.recvfrom(CLIENT_MESSAGE_MAX_SIZE)
            print('receiver')
            byte_checksum = data[0:4]
            byte_message = data[4:]
            decoded_checksum = self.decode_checksum(byte_checksum)
            calc_checksum = CRC32().calculate(byte_message)
            print(calc_checksum, decoded_checksum, calc_checksum == decoded_checksum)

            if calc_checksum == decoded_checksum:
                coords = self.decode_payload(byte_message)
                self.game_state[client_address] = coords
                print('game_state', self.game_state)

    def decode_checksum(self, byte_checksum):
        return int.from_bytes(byte_checksum, 'little')

    def decode_payload(self, byte_message):
        x_field = byte_message[0:4]
        y_field = byte_message[4:]
        return int.from_bytes(x_field, 'little'), int.from_bytes(y_field, 'little')

class BroadcasterThread(threading.Thread):
    def __init__(self, address, game_state):
        self.game_state = game_state
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(address)
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(0.05)
            for address in self.game_state.keys():
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

class GameServer(object):
    def __init__(self, receiver_address, broadcaster_address, api_address):
        self.api_address = api_address
        self.game_state = {}
        self.receiver = ReceiverThread(receiver_address, self.game_state)
        self.broadcaster = BroadcasterThread(broadcaster_address, self.game_state)
        #game_server_api.set_address(api_address)

        
    def start(self):
        self.receiver.start()
        self.broadcaster.start()
        api_server =  game_server_api.GameServerApi(self.game_state)
        api_server.run(port = self.api_address[1])
        #self.receiver.join()
        #self.broadcaster.join()
