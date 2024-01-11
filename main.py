import pygame
from globalVars import *
from getTrack import *
from car import *
from sim import *
import neat


def main():
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "./neat_config.txt",
    )
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(run_sim, 1000)

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

    car = PlayerCar(1, car_start_pos_arr, car_start_angle, car_start_pos, car_start_angle)
    value = True
    while value:
        car.reset()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                value = False
                break
    pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
