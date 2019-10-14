__author__ = 'Piia Hartikka 013866037'

import threading
import socket
from PyCRC.CRC32 import CRC32
import time
import queue

SERVER_MESSAGE_MAX_SIZE = 60000

class ReceiverThread(threading.Thread):
    def __init__(self, socket, inbound_queue):
        self.socket = socket
        self.inbound_queue = inbound_queue
        threading.Thread.__init__(self)
        self.daemon = True
    
    def run(self):
        while True:
            data, _game_server_address = self.socket.recvfrom(SERVER_MESSAGE_MAX_SIZE)
            byte_checksum = data[0:4]
            byte_message = data[4:]
            decoded_checksum = self.decode_checksum(byte_checksum)
            calc_checksum = CRC32().calculate(byte_message)

            if calc_checksum == decoded_checksum:
                game_state = self.decode_payload(byte_message)
                self.inbound_queue.put(game_state)

    def decode_checksum(self, byte_checksum):
        return int.from_bytes(byte_checksum, 'little')

    def decode_payload(self, byte_message):
        game_state = []
        for i in range(0, len(byte_message), 8):
            x_field = byte_message[i:i+4]
            y_field = byte_message[i+4:i+8]
            game_state.append((
                int.from_bytes(x_field, 'little'),
                int.from_bytes(y_field, 'little')
            ))
        return game_state

class SenderThread(threading.Thread):
    def __init__(self, socket, game_server_address, outbound_queue):
        self.socket = socket
        self.game_server_address = game_server_address
        self.outbound_queue = outbound_queue
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            coords = self.outbound_queue.get()
            encoded_message = self.encode_message(coords)
            encoded_checksum = self.encode(CRC32().calculate(encoded_message))
            self.send(self.game_server_address, encoded_checksum + encoded_message)

    def send(self, address, message):
        self.socket.sendto(message, address)

    def encode_message(self, coords):
        x, y = coords
        return self.encode(x) + self.encode(y)

    def encode(self, int_number):
        return int_number.to_bytes(4, byteorder='little')


class Client(object):
    def __init__(self, game_server_address):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(('', 0))

        self.inbound_queue = queue.Queue()
        self.outbound_queue = queue.Queue()

        self._receiver = ReceiverThread(self._socket, self.inbound_queue)
        self._sender = SenderThread(self._socket, game_server_address, self.outbound_queue)

        self._receiver.start()
        self._sender.start()
