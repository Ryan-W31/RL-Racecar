import pygame
import os
import math
from globalVars import *


class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, debug_flag, car_num, checkpoint_num, pos, angle, car_start_pos, car_start_angle):
        super().__init__()
        self.car = pygame.transform.scale_by(pygame.image.load(os.path.join("assets", f"car_{car_num}.png")), 0.1)
        self.image = self.car

        self.start_pos = car_start_pos
        self.start_angle = car_start_angle
        self.rotation_speed = 5
        self.pos = pos
        self.angle = angle

        self.checkpoint_num = checkpoint_num
        self.speed = 4
        self.rect = self.image.get_rect(center=pos)

        self.direction = 0

        self.radars = []
        self.drawing_radars = []

        self.is_alive = True
        self.debug_flag = debug_flag

    def draw_radar(self, screen, position):
        pygame.draw.line(screen, (0, 255, 0), self.rect.center, position, 1)
        pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.is_alive = True
        for point in self.corners:
            if game_map.get_at((int(point[0]), int(point[1]))) == pygame.Color(0, 0, 0, 0):
                self.is_alive = False
                break

    def checkpoint_collision(self, checkpoint_rect, checkpoint_mask):
        for point in self.corners:
            pos_checkpoint_mask1 = (
                point[0] - checkpoint_rect.x,
                point[1] - checkpoint_rect.y,
            )
            pos_checkpoint_mask2 = (
                point[0] + checkpoint_rect.x,
                point[1] + checkpoint_rect.y,
            )

            checkpoint_collide = (
                checkpoint_rect.collidepoint(*point)
                and checkpoint_mask.get_at(pos_checkpoint_mask1)
                and checkpoint_mask.get_at(pos_checkpoint_mask2)
            )

            checkpoint_collide = isinstance(checkpoint_collide, bool)

            if not checkpoint_collide:
                return True
        return False

    def check_radar(self, degree, game_map, screen):
        length = 0
        x_center = int(self.rect.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y_center = int(self.rect.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while not game_map.get_at((x_center, y_center)) == (0, 0, 0, 0) and length < 250:
            length = length + 1
            x_center = int(self.rect.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y_center = int(self.rect.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        if self.debug_flag:
            self.draw_radar(screen, (x_center, y_center))

        dist = int(math.sqrt(math.pow(x_center - self.rect.center[0], 2) + math.pow(y_center - self.rect.center[1], 2)))
        self.radars.append([(x_center, y_center), dist])

    def rotate(self):
        if self.direction == 1:
            self.angle += self.rotation_speed
        elif self.direction == -1:
            self.angle -= self.rotation_speed

        self.image = pygame.transform.rotate(self.car, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        self.rect.centerx += math.sin(math.radians(self.angle)) * self.speed
        self.rect.centery += math.cos(math.radians(self.angle)) * self.speed

    def update(self, game_map, screen):
        self.rotate()
        self.move()

        length = 7
        left_top = [
            self.rect.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.rect.center[1] - math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.rect.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.rect.center[1] - math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.rect.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.rect.center[1] - math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.rect.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.rect.center[1] - math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [right_top, left_top, left_bottom, right_bottom]
        self.check_collision(game_map)
        self.radars.clear()

        for d in (0, -45, -90, -135, -180):
            self.check_radar(d, game_map, screen)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1])

        return return_values

    def check_alive(self):
        return self.is_alive

    def reset(self):
        self.pos = [self.start_pos[0], self.start_pos[1]]
        self.angle = self.start_angle
        self.speed = 0
        self.is_alive = True

    def getPos(self):
        return self.pos
