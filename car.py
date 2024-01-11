import pygame
import time
import math
from globalVars import *

x = 200
y = 400


class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, checkpoint_num, pos, angle, car_start_pos, car_start_angle):
        super().__init__()
        self.car = pygame.image.load("images/red_car_resize.png")
        self.image = self.car

        self.start_pos = car_start_pos
        self.start_angle = car_start_angle
        self.rotation_speed = 4
        self.pos = pos
        self.angle = angle

        self.checkpoint_num = checkpoint_num
        self.speed = pygame.math.Vector2(0.8, 0)
        self.rect = self.image.get_rect(center=pos)

        self.radars = []
        self.drawing_radars = []

        self.is_alive = True

    # def draw(self, screen):
    #     rot_center(screen)
    #     self.draw_radar(screen)

    # def draw_without_radar(self, screen):
    #     rot_center(screen)

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.rect.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.is_alive = True
        for point in self.corners:
            print("Color", game_map.get_at((int(point[0]), int(point[1]))))
            if game_map.get_at((int(point[0]), int(point[1]))) == pygame.Color(0, 0, 0, 0):
                self.is_alive = False
                break

    def checkpoint_collision(self,checkpoint_rect, checkpoint_mask):
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

        self.draw_radar(screen)

        dist = int(math.sqrt(math.pow(x_center - self.rect.center[0], 2) + math.pow(y_center - self.rect.center[1], 2)))
        self.radars.append([(x_center, y_center), dist])

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_speed
            self.speed.rotate_ip(-self.rotation_speed)
        elif right:
            self.angle -= self.rotation_speed
            self.speed.rotate_ip(self.rotation_speed)

        self.image = pygame.transform.rotozoom(self.car, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        self.rect.center += self.speed * 6

    def update(self, game_map, screen):
        #self.pos[1] += math.cos(math.radians(self.angle)) * self.speed

        self.move()


        #self.pos[0] += math.sin(math.radians(self.angle)) * self.speed

        # length = 40
        # print(self.rect.)
        # right = [
        #     self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length,
        #     self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length,
        # ]
        # left = [
        #     self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length,
        #     self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length,
        # ]
        # left_bottom = [
        #     self.rect.center[0] + math.cos(math.radians(self.angle + 210)) * length,
        #     self.rect.center[1] - math.sin(math.radians(self.angle + 210)) * length,
        # ]
        # right_bottom = [
        #     self.rect.center[0] + math.cos(math.radians(self.angle + 330)) * length,
        #     self.rect.center[1] - math.sin(math.radians(self.angle + 330)) * length,
        # ]
        self.corners = [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]
        print(self.corners)
        self.check_collision(game_map)
        self.radars.clear()

        for d in range(-180, 0, 45):
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
