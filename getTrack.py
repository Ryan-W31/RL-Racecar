import numpy as np
import random as rd
import pygame, math, sys, argparse
from pygame.locals import *
import scipy as sc
from scipy.spatial import ConvexHull
from scipy import interpolate

from globalVars import *


def random_points(min=MIN_POINTS, max=MAX_POINTS, margin=MARGIN, distance=MIN_DISTANCE):
    rd.seed(COOL_TRACK_SEEDS[15])
    pointCount = rd.randrange(min, max + 1, 1)
    points = []

    for point in range(pointCount):
        x = rd.randrange(margin, WIDTH - margin - 1, 1)
        y = rd.randrange(margin, HEIGHT - margin - 1, 1)
        d = list(
            filter(
                lambda x: x < distance,
                [math.sqrt((p[0] - x) ** 2 + (p[1] - y) ** 2) for p in points],
            )
        )
        if len(d) == 0:
            points.append((x, y))

    return np.array(points)


def get_points(hull, points):
    return np.array([points[hull.vertices[i]] for i in range(len(hull.vertices))])


def get_vector(dimensions):
    vector = [rd.gauss(0, 1) for i in range(dimensions)]
    magnitude = sum(v**2 for v in vector) ** 0.5
    return [v / magnitude for v in vector]


def make_track(points, difficulty=DIFFICULTY, displacement=MAX_DISPLACEMENT, margin=MARGIN):
    pos = [[0, 0] for p in range(len(points) * 2)]

    for i in range(len(points)):
        disp = math.pow(rd.random(), difficulty) * displacement
        disp_list = [disp * i for i in get_vector(2)]
        pos[i * 2] = points[i]
        pos[i * 2 + 1][0] = int((points[i][0] + points[(i + 1) % len(points)][0]) / 2 + disp_list[0])
        pos[i * 2 + 1][1] = int((points[i][1] + points[(i + 1) % len(points)][1]) / 2 + disp_list[1])

    for i in range(3):
        pos = fix_angles(pos)
        pos = push_points_apart(pos)

    final_set = []

    for point in pos:
        if point[0] < margin:
            point[0] = margin
        elif point[0] > (WIDTH - margin):
            point[0] = WIDTH - margin
        if point[1] < margin:
            point[1] = margin
        elif point[1] > HEIGHT - margin:
            point[1] = HEIGHT - margin
        final_set.append(point)
    return final_set


def push_points_apart(points, distance=DISTANCE_BETWEEN_POINTS):
    distance2 = distance * distance
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            p_distance = math.sqrt((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2)
            if p_distance < distance:
                dx = points[j][0] - points[i][0]
                dy = points[j][1] - points[i][1]
                dl = math.sqrt(dx * dx + dy * dy)
                dx /= dl
                dy /= dl
                dif = distance - dl
                dx *= dif
                dy *= dif
                points[j][0] = int(points[j][0] + dx)
                points[j][1] = int(points[j][1] + dy)
                points[i][0] = int(points[i][0] - dx)
                points[i][1] = int(points[i][1] - dy)
    return points


def fix_angles(points, max_angle=MAX_ANGLE):
    for i in range(len(points)):
        if i > 0:
            prev_point = i - 1
        else:
            prev_point = len(points) - 1
        next_point = (i + 1) % len(points)
        px = points[i][0] - points[prev_point][0]
        py = points[i][1] - points[prev_point][1]
        pl = math.sqrt(px * px + py * py)
        px /= pl
        py /= pl
        nx = -(points[i][0] - points[next_point][0])
        ny = -(points[i][1] - points[next_point][1])
        nl = math.sqrt(nx * nx + ny * ny)
        nx /= nl
        ny /= nl
        a = math.atan2(px * ny - py * nx, px * nx + py * ny)
        if abs(math.degrees(a)) <= max_angle:
            continue
        diff = math.radians(max_angle * math.copysign(1, a)) - a
        c = math.cos(diff)
        s = math.sin(diff)
        new_x = (nx * c - ny * s) * nl
        new_y = (nx * s + ny * c) * nl
        points[next_point][0] = int(points[i][0] + new_x)
        points[next_point][1] = int(points[i][1] + new_y)
    return points


def get_corners_with_curb(points, min_curb_angle=MIN_CURB_ANGLE, max_curb_angle=MAX_CURB_ANGLE):
    require_curb = []
    for i in range(len(points)):
        if i > 0:
            prev_point = i - 1
        else:
            prev_point = len(points) - 1
        next_point = (i + 1) % len(points)
        px = points[prev_point][0] - points[i][0]
        py = points[prev_point][1] - points[i][1]
        pl = math.sqrt(px * px + py * py)
        px /= pl
        py /= pl
        nx = points[next_point][0] - points[i][0]
        ny = points[next_point][1] - points[i][1]
        nl = math.sqrt(nx * nx + ny * ny)
        nx /= nl
        ny /= nl
        a = math.atan(px * ny - py * nx)
        if min_curb_angle <= abs(math.degrees(a)) <= max_curb_angle:
            require_curb.append(points[i])
    return require_curb


def smooth_track(track_points):
    x = np.array([p[0] for p in track_points])
    y = np.array([p[1] for p in track_points])

    x = np.r_[x, x[0]]
    y = np.r_[y, y[0]]

    tck, u = interpolate.splprep([x, y], s=0, per=True)

    xi, yi = interpolate.splev(np.linspace(0, 1, SPLINE_POINTS), tck)
    return [(int(xi[i]), int(yi[i])) for i in range(len(xi))]


def get_full_corners(track_points, corners):
    offset = FULL_CORNER_NUM_POINTS
    corners_in_track = get_corners_from_kp(track_points, corners)
    f_corners = []
    for corner in corners_in_track:
        i = track_points.index(corner)
        tmp_track_points = track_points + track_points + track_points
        f_corner = tmp_track_points[i + len(track_points) - 1 - offset : i + len(track_points) - 1 + offset]
        f_corners.append(f_corner)
    return f_corners


def get_corners_from_kp(complete_track, corner_kps):
    return [find_closest_point(complete_track, corner) for corner in corner_kps]


def find_closest_point(points, keypoint):
    min_dist = None
    closest_point = None
    for p in points:
        dist = math.hypot(p[0] - keypoint[0], p[1] - keypoint[1])
        if min_dist is None or dist < min_dist:
            min_dist = dist
            closest_point = p
    return closest_point


def get_checkpoints(track_points, n_checkpoints=N_CHECKPOINTS):
    checkpoint_step = len(track_points) // n_checkpoints
    checkpoints = []
    for i in range(N_CHECKPOINTS):
        index = i * checkpoint_step
        checkpoints.append(track_points[index])
    return checkpoints


def draw_points(surface, color, points):
    for p in points:
        draw_single_point(surface, color, p)


def draw_convex_hull(hull, surface, points, color):
    for i in range(len(hull.vertices) - 1):
        draw_single_line(surface, color, points[hull.vertices[i]], points[hull.vertices[i + 1]])
        if i == len(hull.vertices) - 2:
            draw_single_line(surface, color, points[hull.vertices[0]], points[hull.vertices[-1]])


def draw_lines_from_points(surface, color, points):
    for i in range(len(points) - 1):
        draw_single_line(surface, color, points[i], points[i + 1])
        if i == len(points) - 2:
            draw_single_line(surface, color, points[0], points[-1])


def draw_single_point(surface, color, pos, radius=2):
    pygame.draw.circle(surface, color, pos, radius)


def draw_single_line(surface, color, init, end):
    pygame.draw.line(surface, color, init, end)


def draw_track(surface, color, points, corners):
    radius = TRACK_WIDTH // 2
    draw_corner_curbs(surface, corners, radius)
    chunk_dimensions = (radius * 2, radius * 2)

    for point in points:
        blit_pos = (point[0] - radius, point[1] - radius)
        track_chunk = pygame.Surface(chunk_dimensions, pygame.SRCALPHA)
        pygame.draw.circle(track_chunk, color, (radius, radius), radius)
        surface.blit(track_chunk, blit_pos)

    starting_grid = draw_starting_grid(radius * 2)

    offset = TRACK_ANGLE_OFFSET
    vec_p = [points[offset][1] - points[0][1], -(points[offset][0] - points[0][0])]
    n_vec_p = [
        vec_p[0] / math.hypot(vec_p[0], vec_p[1]),
        vec_p[1] / math.hypot(vec_p[0], vec_p[1]),
    ]

    angle = math.degrees(math.atan2(n_vec_p[1], n_vec_p[0]))
    rot_grid = pygame.transform.rotate(starting_grid, -angle)
    start_pos = (
        points[0][0] - math.copysign(1, n_vec_p[0]) * n_vec_p[0] * radius,
        points[0][1] - math.copysign(1, n_vec_p[1]) * n_vec_p[1] * radius,
    )
    surface.blit(rot_grid, start_pos)
    return start_pos, angle


def draw_starting_grid(track_width):
    tile_height = FINISH_LINE_HEIGHT
    tile_width = FINISH_LINE_WIDTH
    grid_tile = pygame.image.load(FINISH_LINE)
    starting_grid = pygame.Surface((track_width, tile_height), pygame.SRCALPHA)
    for i in range(track_width // tile_height):
        position = (i * tile_width, 0)
        starting_grid.blit(grid_tile, position)
    return starting_grid


def draw_checkpoint(points, checkpoint):
    margin = CHECKPOINT_MARGIN
    radius = TRACK_WIDTH // 2 + margin
    offset = CHECKPOINT_ANGLE_OFFSET
    check_index = points.index(checkpoint)
    vec_p = [
        points[check_index + offset][1] - points[check_index][1],
        -(points[check_index + offset][0] - points[check_index][0]),
    ]
    n_vec_p = [
        vec_p[0] / math.hypot(vec_p[0], vec_p[1]),
        vec_p[1] / math.hypot(vec_p[0], vec_p[1]),
    ]
    angle = math.degrees(math.atan2(n_vec_p[1], n_vec_p[0]))
    checkpoint = draw_rectangle((radius * 3, 10), (0, 0, 255, 100), line_thickness=5, fill=True)
    rot_checkpoint = pygame.transform.rotate(checkpoint, -angle)
    check_pos = (
        points[check_index][0] - math.copysign(1, n_vec_p[0]) * n_vec_p[0] * radius,
        points[check_index][1] - math.copysign(1, n_vec_p[1]) * n_vec_p[1] * radius,
    )
    return (rot_checkpoint, check_pos)


def draw_rectangle(dimensions, color, line_thickness=1, fill=True):
    filled = line_thickness
    if fill:
        filled = 0
    rect_surf = pygame.Surface(dimensions, pygame.SRCALPHA)
    pygame.draw.rect(rect_surf, color, (0, 0, dimensions[0], dimensions[1]), filled)
    return rect_surf


def draw_corner_curbs(track_surface, corners, track_width):
    step = STEP_TO_NEXT_CURB_POINT
    offset = CURB_ANGLE_OFFSET
    correction_x = CURB_X_CORRECTION
    correction_y = CURB_Y_CORRECTION
    for corner in corners:
        temp_corner = corner + corner
        last_curb = None
        for i in range(0, len(corner), step):
            vec_p = [
                temp_corner[i + offset][0] - temp_corner[i][0],
                temp_corner[i + offset][1] - temp_corner[i][1],
            ]
            n_vec_p = [
                vec_p[0] / math.hypot(vec_p[0], vec_p[1]),
                vec_p[1] / math.hypot(vec_p[0], vec_p[1]),
            ]
            vec_perp = [
                temp_corner[i + offset][1] - temp_corner[i][1],
                -(temp_corner[i + offset][0] - temp_corner[i][0]),
            ]
            n_vec_perp = [
                vec_perp[0] / math.hypot(vec_perp[0], vec_perp[1]),
                vec_perp[1] / math.hypot(vec_perp[0], vec_perp[1]),
            ]
            angle = math.degrees(math.atan2(n_vec_p[1], n_vec_p[0]))
            curb = draw_single_curb()
            rot_curb = pygame.transform.rotate(curb, -angle)
            m_x = 1
            m_y = 1
            if angle > 180:
                m_x = -1
            start_pos = (
                corner[i][0] + m_x * n_vec_perp[0] * track_width - correction_x,
                corner[i][1] + m_y * n_vec_perp[1] * track_width - correction_y,
            )
            if last_curb is None:
                last_curb = start_pos
            else:
                if math.hypot(start_pos[0] - last_curb[0], start_pos[1] - last_curb[1]) >= track_width:
                    continue
            last_curb = start_pos
            track_surface.blit(rot_curb, start_pos)


def draw_single_curb():
    tile_height = CURB_HEIGHT
    tile_width = CURB_WIDTH
    curb_tile = pygame.image.load(CURB)
    curb = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
    curb.blit(curb_tile, (0, 0))
    return curb
