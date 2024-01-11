import pygame
from globalVars import *
from getTrack import *
from car import *
import pandas as pd
import time
import random as rn


def choose_move(q_table, current_state, epsilon, actions):
    if np.random.uniform(0, 1) < epsilon:
        action = np.random.choice(actions)
    else:
        bools = q_table.loc[current_state, :] == np.max(q_table.loc[current_state, :])
        actions_tie = bools[bools].index.values

        if len(actions_tie) > 1:
            action = np.random.choice(actions_tie)
        else:
            action = actions_tie[0]

    return action


def move(player_car, action):
    if action == "left":
        player_car.rotate(left=True)
    elif action == "right":
        player_car.rotate(right=True)


def update(q_table, current_state, next_state, action, reward, discount_factor, learning_rate):
    # if next_state == 0:
    target = reward + discount_factor * np.max(q_table.loc[next_state, :]) - q_table.loc[current_state, action]
    # else:
    #     target = reward

    q_table.loc[current_state, action] = q_table.loc[current_state, action] + learning_rate * target

    return q_table


def main(debug=True, draw_checkpoints_in_track=True):
    learning_rate = 0.9
    discount_factor = 0.9
    epsilon = 1
    decay = 0.005

    actions = ["left", "right", "straight"]
    num_states = 50

    q_table = pd.DataFrame(index=range(num_states), columns=actions, dtype=float)
    q_table = q_table.fillna(0)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game!")

    background_color = GRASS_GREEN
    background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(background, background_color, (0, 0, WIDTH, HEIGHT))

    points = random_points()
    hull = ConvexHull(points)
    track_points = make_track(get_points(hull, points))
    corner_points = get_corners_with_curb(track_points)
    f_points = smooth_track(track_points)

    corners = get_full_corners(f_points, corner_points)

    foreground = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    start_pos, circles, rot_grid, angle, curbs = draw_track(foreground, GREY, f_points, corners)

    checkpoints_i = get_checkpoints(f_points)
    checkpoints = []
    # if draw_checkpoints_in_track or debug:
    #     for checkpoint in checkpoints_i[1:]:
    #         checkpoints.append(draw_checkpoint(foreground, f_points, checkpoint, debug))
    if debug:
        draw_points(screen, WHITE, points)
        draw_convex_hull(hull, screen, points, RED)
        draw_points(screen, BLUE, track_points)
        draw_lines_from_points(screen, BLUE, track_points)
        draw_points(screen, BLACK, f_points)

    # rect = foreground.get_rect(center=(500, 400))
    mask = foreground.convert_alpha()

    clock = pygame.time.Clock()

    if -angle > 0:
        car_start_angle = -angle
    else:
        car_start_angle = -angle + 360

    car_start_pos = ()

    if car_start_angle >= 0 and car_start_angle < 90:
        car_start_pos = (start_pos[0], start_pos[1])
    elif car_start_angle >= 90 and car_start_angle < 180:
        car_start_pos = (start_pos[0], start_pos[1])
    elif car_start_angle >= 180 and car_start_angle < 270:
        car_start_pos = (start_pos[0] + 25, start_pos[1] + 30)
    elif car_start_angle >= 270 and car_start_angle < 360:
        car_start_pos = (start_pos[0] + 30, start_pos[1] - 25)

    car_start_pos_arr = [car_start_pos[0], car_start_pos[1]]
    print(car_start_pos_arr)
    player_car = PlayerCar(3, car_start_pos_arr, car_start_angle, car_start_pos, car_start_angle)
    running = True

    sequence = 1

    episode = 0

    steps = 0

    reward = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        screen.blit(background, (0, 0))
        screen.blit(foreground, (0, 0))

        if sequence == (N_CHECKPOINTS - 1):
            sequence = 0

        checkpoint = draw_checkpoint(mask, f_points, checkpoints_i[sequence], debug)
        checkpoint_rect = checkpoint[0].get_rect(center=checkpoint[1])
        checkpoint_mask = pygame.mask.from_surface(checkpoint[0])

        screen.blit(checkpoint[0], checkpoint[1])
        # screen.blit(mask, (0, 0))
        # print(mask.get_at((900, 200)))

        action = choose_move(q_table, sequence, epsilon, actions)
        steps += 1
        move(player_car, action)

        if player_car.check_alive():
            reward += 1
            player_car.update(mask)

            if player_car.checkpoint_collision(mask, checkpoint_rect, checkpoint_mask):
                reward += 5
                sequence += 1

            player_car.draw(screen)
        else:
            player_car.reset()
            sequence = 1
            reward -= 20
            print("Episode: ", episode, "Reward: ", reward)
            episode += 1
            time.sleep(0.5)

            epsilon = epsilon * decay
            epsilon = max(epsilon, 0.1)
            reward = 0

        q_table = update(q_table, sequence, sequence + 1, action, reward, discount_factor, learning_rate)
        pygame.display.update()

    print(f"Finished on Epsiode {episode} with {steps} Steps")
    print(q_table)
    pygame.quit()


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procedural racetrack generator")
    parser.add_argument(
        "--debug",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Show racetrack generation steps",
    )
    parser.add_argument(
        "--show-checkpoints",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Show checkpoints",
    )
    args = parser.parse_args()
    main(debug=args.debug, draw_checkpoints_in_track=args.show_checkpoints)
