import pygame
from globalVars import *
from getTrack import *


def build_track():
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
    start_pos, angle = draw_track(foreground, GREY, f_points, corners)

    checkpoints_i = get_checkpoints(f_points)

    mask = foreground.convert_alpha()

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

    return (
        background,
        foreground,
        mask,
        f_points,
        car_start_pos_arr,
        car_start_pos,
        car_start_angle,
        checkpoints_i,
    )
