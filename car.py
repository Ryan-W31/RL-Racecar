import pygame
import time
import math
from utils import rescale, rot_center
from globalVars import *

x = 20
y = 40


class PlayerCar:
    def __init__(self, rotation_speed, pos, angle, car_start_pos, car_start_angle):
        self.car = pygame.transform.scale(pygame.image.load("images/red_car.png"), (x, y))
        self.rotated_car = self.car

        self.start_pos = car_start_pos
        self.start_angle = car_start_angle
        self.rotation_speed = rotation_speed
        self.pos = pos
        self.angle = angle
        self.speed = 0

        self.center = [self.pos[0] + x / 2, self.pos[1] + y / 2]

        self.radars = []
        self.drawing_radars = []

        self.is_alive = True

        self.distance = 0
        self.time = 0

    def draw(self, screen):
        rot_center(screen, self.car, self.pos, self.angle)
        self.draw_radar(screen)

    def drawWithoutRadar(self, screen):
        screen.blit(self.rotated_car, self.pos)

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.is_alive = True
        for point in self.corners:
            if game_map.get_at((int(point[0]), int(point[1]))) == (0, 0, 0, 0):
                self.is_alive = False
                break

    def checkpoint_collision(self, game_map, checkpoint_rect, checkpoint_mask):
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

    def check_radar(self, degree, game_map):
        length = 0
        x_center = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y_center = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while not game_map.get_at((x_center, y_center)) == (0, 0, 0, 0) and length < 250:
            length = length + 1
            x_center = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y_center = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt(math.pow(x_center - self.center[0], 2) + math.pow(y_center - self.center[1], 2)))
        self.radars.append([(x_center, y_center), dist])

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_speed
        elif right:
            self.angle -= self.rotation_speed

    def update(self, game_map):
        self.speed = 2
        self.pos[1] += math.cos(math.radians(self.angle)) * self.speed
        # self.pos[0] = max(self.pos[0], 20)
        # self.pos[0] = min(self.pos[0], TRACK_WIDTH - 120)

        # self.distance += self.speed
        # self.time += 1

        self.pos[0] += math.sin(math.radians(self.angle)) * self.speed
        # self.pos[1] = max(self.pos[1], 20)
        # self.pos[1] = min(self.pos[1], TRACK_WIDTH - 120)

        self.center = [int(self.pos[0]) + x / 2, int(self.pos[1]) + y / 2]

        length = 0.5 * x
        left_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # print(f"Pos: {self.pos}\nCenter: {self.center}\nCorners: {self.corners}")
        self.check_collision(game_map)
        self.radars.clear()

        for d in range(0, 360, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def check_alive(self):
        return self.is_alive

    def get_reward(self):
        return self.distance / (x / 2)

    def reset(self):
        self.pos = [self.start_pos[0], self.start_pos[1]]
        self.angle = self.start_angle
        self.speed = 0
        self.is_alive = True
        # pygame.display.update()

    # def collisionScreen(self, time):
    #     self.pos = [500, 670]
    #     self.is_alive = True
    #     window.blit(track, (0, 0))
    #     window.blit(finish, (600, 670))
    #     window.blit(self.rotatedCarImage, self.pos)
    #     pygame.draw.rect(window, (0,0,0), pygame.Rect(450, 150, 500, 500))
    #     pygame.draw.rect(window, (0, 255, 0), pygame.Rect(450, 150, 500, 500), 2)
    #     scoreLabel = ef.render("AI collided",1,(0,255,0))
    #     window.blit(scoreLabel, (width - scoreLabel.get_width() - 510, 250))
    #     scoreLabel = ef.render("Time elapsed:-",1,(0,255,0))
    #     window.blit(scoreLabel, (width - scoreLabel.get_width() - 510, 350))
    #     scoreLabel = ef.render(str("%.2f"%time),1,(0,255,0))
    #     window.blit(scoreLabel, (width - scoreLabel.get_width() - 510, 450))
    #     pygame.display.update()

    # for event in pygame.event.get():
    #     if event.type == pygame.KEYDOWN:
    #         pygame.quit()
    #         quit()

    def getPos(self):
        return self.pos
