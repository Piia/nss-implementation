__author__ = 'Piia Hartikka 013866037'

import pygame
from pygame.locals import *
import sys
from queue import Empty


class Game(object):
    def __init__(self, server_message_queue, command_queue):
        self.server_message_queue = server_message_queue
        self.command_queue = command_queue
        self.WINDOW_WIDTH = 400
        self.WINDOW_HEIGHT = 300

        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)

        self.BLOCK = 10
        self.x = 200
        self.y = 200

        self.game_state = []

        pygame.init()
        pygame.display.set_caption('Game client')
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), 0, 32)
        self.screen.fill(self.WHITE)
        self.clock = pygame.time.Clock()

    def start(self):
        running = True

        while running:
            self.clock.tick(60)
            self.update_game_state()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.locals.K_UP:
                        self.y -= self.BLOCK
                    elif event.key == pygame.locals.K_DOWN:
                        self.y += self.BLOCK
                    elif event.key == pygame.locals.K_RIGHT:
                        self.x += self.BLOCK
                    elif event.key == pygame.locals.K_LEFT:
                        self.x -= self.BLOCK
                    else:
                        continue
                    self.write_command()
            self.draw()
            pygame.display.update()

    def draw(self):
        self.screen.fill(self.WHITE)
        for coords in self.game_state:
            rectangle = pygame.Rect(coords, (self.BLOCK, self.BLOCK))
            pygame.draw.rect(self.screen, self.GREEN, rectangle)
        self.draw_me_like_one_of_your_french_girls()

    def draw_me_like_one_of_your_french_girls(self):
        rectangle = pygame.Rect((self.x, self.y), (self.BLOCK, self.BLOCK))
        pygame.draw.rect(self.screen, self.BLUE, rectangle)

    def update_game_state(self):
        last_game_state = None
        
        try:
            while True:
                last_game_state = self.server_message_queue.get_nowait()
        except Empty:
            pass

        if last_game_state != None:
            self.game_state = last_game_state

    def write_command(self):
        self.command_queue.put((self.x, self.y))