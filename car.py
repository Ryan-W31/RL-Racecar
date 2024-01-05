import pygame
import time
import math
from utils import rescale, rot_center
from globalVars import *

RED_CAR = rescale(pygame.image.load("images/red_car.png"), 0.03)

class AbstractCar:
    def __init__(self, max_vel, rotation_vel, pos):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = pos
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        rot_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y += vertical
        self.x += horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        print(poi)
        return poi


class PlayerCar(AbstractCar):
    IMG = RED_CAR

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


def draw(win, start_pos, background, circles, curbs, finish_line, player_car):

    win.blit(background, (0,0))

    for circle in circles:
        win.blit(circle[0], circle[1])
    for curb in curbs:
        win.blit(curb[0], curb[1])
    
    win.blit(finish_line, start_pos)

    player_car.draw(win)
    pygame.display.update()