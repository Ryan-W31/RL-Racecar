import pygame
from globalVars import *
from getTrack import *
from car import *


def choose_move(q_table, current_state, epsilon, num_actions):
    if np.random.rand() < epsilon:
        action = np.random.randint(num_actions)
    else:
        action = np.argmax(q_table[current_state])

    return action


def move(player_car, action):
    moved = False

    if action == 0:
        player_car.rotate(left=True)
    if action == 1:
        player_car.rotate(right=True)
    if action == 2:
        moved = True
        player_car.move_forward()

    if not moved:
        player_car.reduce_speed()
        if action == 1:
            return 0.5
        else:
            return 0

    return 1


def update(q_table, current_state, next_state, action, reward, discount_factor, learning_rate):
    q_table[current_state, action] = (1 - learning_rate) * q_table[current_state, action] + learning_rate * (
        reward + discount_factor * np.max(q_table[next_state])
    )

    return q_table


def main(debug=True, draw_checkpoints_in_track=True):
    learning_rate = 0.1
    discount_factor = 0.9
    epsilon = 0.3

    num_actions = 3
    num_states = 50

    q_table = np.zeros((num_states, num_actions))

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
    if draw_checkpoints_in_track or debug:
        for checkpoint in checkpoints_i[1:]:
            checkpoints.append(draw_checkpoint(foreground, f_points, checkpoint, debug))
    if debug:
        draw_points(screen, WHITE, points)
        draw_convex_hull(hull, screen, points, RED)
        draw_points(screen, BLUE, track_points)
        draw_lines_from_points(screen, BLUE, track_points)
        draw_points(screen, BLACK, f_points)

    rect = foreground.get_rect(center=(500, 400))
    mask = pygame.mask.from_surface(foreground)

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

    player_car = PlayerCar(2, 4, car_start_pos, car_start_angle, car_start_pos, car_start_angle)
    running = True

    sequence = 1

    episode = 0

    steps = 0

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        reward = 0
        if sequence == (N_CHECKPOINTS - 1):
            sequence = 0

        checkpoint = draw_checkpoint(foreground, f_points, checkpoints_i[sequence], debug)

        action = choose_move(q_table, sequence, epsilon, num_actions)
        steps += 1
        reward += move(player_car, action)

        checkpoint_rect = checkpoint[0].get_rect(center=checkpoint[1])
        checkpoint_mask = pygame.mask.from_surface(checkpoint[0])

        point = ((player_car.x), (player_car.y))

        pos_wall_mask1 = point[0] - rect.x, point[1] - rect.y
        pos_wall_mask2 = point[0] + rect.x, point[1] + rect.y
        wall_collide = rect.collidepoint(*point) and mask.get_at(pos_wall_mask1) and mask.get_at(pos_wall_mask2)

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

        if wall_collide == 0:
            print(f"Epsiode {episode}")
            player_car.reset()
            sequence = 1
            steps = 0
            episode += 1

        if checkpoint_collide == False and sequence != 0:
            sequence += 1
            reward += 1
        elif checkpoint_collide == False and sequence == 0:
            print("complete!")
            break

        q_table = update(q_table, sequence, sequence + 1, action, reward, discount_factor, learning_rate)

        draw(
            screen,
            start_pos,
            background,
            foreground,
            circles,
            curbs,
            rot_grid,
            player_car,
            checkpoint[0],
            checkpoint[1],
        )

    print(f"Finished on Epsiode{episode} with {steps} Steps")
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
