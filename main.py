import pygame
from globalVars import *
from getTrack import *
from car import *

def move(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()

    if not moved:
        player_car.reduce_speed()

def main(debug=True, draw_checkpoints_in_track=True):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game!")

    background_color = GRASS_GREEN
    background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(background, background_color, (0,0,WIDTH, HEIGHT))

    points = random_points()
    hull = ConvexHull(points)
    track_points = make_track(get_points(hull, points))
    corner_points = get_corners_with_curb(track_points)
    f_points = smooth_track(track_points)

    corners = get_full_corners(f_points, corner_points)
    start_pos, circles, rot_grid, curbs= draw_track(screen, GREY, f_points, corners)

    checkpoints = get_checkpoints(f_points)
    if draw_checkpoints_in_track or debug:
        for checkpoint in checkpoints:
            draw_checkpoint(screen, f_points, checkpoint, debug)
    if debug:
        draw_points(screen, WHITE, points)
        draw_convex_hull(hull, screen, points, RED)
        draw_points(screen, BLUE, track_points)
        draw_lines_from_points(screen, BLUE, track_points)    
        draw_points(screen, BLACK, f_points)

    mask_image = background.convert()
    mask_image.set_colorkey(GREY)
    mask = pygame.mask.from_surface(mask_image)

    clock = pygame.time.Clock()
    player_car = PlayerCar(4, 4, start_pos)
    running = True

    while running:
        clock.tick(FPS)

        draw(screen, start_pos, background, circles, curbs, rot_grid, player_car)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        move(player_car)
        
        if player_car.collide(mask) == None:
            player_car.bounce()

        finish_line_mask = pygame.mask.from_surface(rot_grid)
        

        # finish_poi_collide = player_car.collide(finish_line_mask, *start_pos)
        # if finish_poi_collide != None:
        #     if finish_poi_collide[1] == 0:
        #         player_car.bounce()
        #     else:
        #         print("finish")

        
    pygame.quit()

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Procedural racetrack generator")
    parser.add_argument("--debug", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Show racetrack generation steps")
    parser.add_argument("--show-checkpoints", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Show checkpoints")
    args = parser.parse_args()
    main(debug=args.debug, draw_checkpoints_in_track=args.show_checkpoints)