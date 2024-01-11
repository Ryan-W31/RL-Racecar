import pygame
from globalVars import *
from getTrack import *
from build_track import *
from car import *
import time
import neat

current_gen = 0
laps = 0
nets = []


def run_sim(genomes, config):
    player_cars = []
    gens = []

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game!")

    (
        background,
        foreground,
        mask,
        f_points,
        car_start_pos_arr,
        car_start_pos,
        car_start_angle,
        checkpoints_i,
    ) = build_track()

    clock = pygame.time.Clock()

    for i, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        player_cars.append(pygame.sprite.GroupSingle(PlayerCar(1, car_start_pos_arr, car_start_angle, car_start_pos, car_start_angle)))
        gens.append(g)

    running = True

    global current_gen
    current_gen += 1

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        for i, player_car in enumerate(player_cars):
            output = nets[i].activate(player_car.sprite.get_data())
            choice = output.index(max(output))

            if choice == 0:
                player_car.sprite.rotate(left=True)
            elif choice == 1:
                player_car.sprite.rotate(right=True)

        alive = 0

        screen.blit(background, (0, 0))
        screen.blit(foreground, (0, 0))

        for i, player_car in enumerate(player_cars):
            if player_car.sprite.checkpoint_num == (N_CHECKPOINTS - 1):
                player_car.sprite.checkpoint_num = 0

            checkpoint = draw_checkpoint(f_points, checkpoints_i[player_car.sprite.checkpoint_num])
            checkpoint_rect = checkpoint[0].get_rect(center=checkpoint[1])
            checkpoint_mask = pygame.mask.from_surface(checkpoint[0])

            screen.blit(checkpoint[0], checkpoint[1])

            if player_car.sprite.check_alive():
                alive += 1
                player_car.update(mask, screen)
                gens[i].fitness += 0.1
                player_car.draw(screen)

                # print(i, player_car.center)

                if player_car.sprite.checkpoint_collision(checkpoint_rect, checkpoint_mask):
                    gens[i].fitness += 10
                    player_car.sprite.checkpoint_num += 1
            else:
                gens[i].fitness -= 2
                player_car.sprite.checkpoint_num = 1
                player_cars.pop(i)
                nets.pop(i)
                gens.pop(i)

        if alive == 0:
            running = False
            time.sleep(0.3)
            break

        print("Generation: ", current_gen, "Alive: ", alive)
        pygame.display.update()
