import pygame
from pygame.locals import *
import random as rd
import sys

from structures import Ball, Cannon, Experiment, Platform, \
    VisibilityBorder, PredictedPath, InformationBox
from utils import convert_to_screen_coords, convert_to_rad, ball_trajectory, \
    capture_image, get_ball_center, predict_path, get_destination

FPS = 240  # frame per second

RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

WIDTH = 600
HEIGHT = 400

left_vision_border = int(WIDTH/3)
right_vision_border = int(WIDTH/3)*2

ball_start_x, ball_start_y = (0, int(HEIGHT*0.75))
ball_start_h = abs(ball_start_y - HEIGHT)

CIRCLE_RENDERER = pygame.draw.circle
LINE_RENDERER = pygame.draw.line
RECT_RENDERER = pygame.draw.rect
ARRAY_RENDERER = pygame.surfarray

DEFAULT_RADIUS = 10
DEFAULT_ALPHA_INITIAL = 15
DEFAULT_RND_OFFSET = 0
DEFAULT_SPEED = 120
G = 9.8

platform_steps = WIDTH
screenshot_steps = 2
time_steps = WIDTH

TITLE = "Catch the ball experiment"

pygame.font.init()
screen_font = pygame.font.SysFont('Arial', 15)
screen_font_result = pygame.font.SysFont('Arial', 25)

def main(ball_radius=DEFAULT_RADIUS, alpha_initial=DEFAULT_ALPHA_INITIAL, \
                        alpha_rnd_offset=DEFAULT_RND_OFFSET, speed=DEFAULT_SPEED, g=G):

    clock = pygame.time.Clock()

    canvas = pygame.display.set_mode((WIDTH, HEIGHT))
    # clipped screen for opencv: only part between borders
    canvas_clipped = pygame.Surface(
        (right_vision_border-left_vision_border, HEIGHT))

    pygame.display.set_caption(TITLE)
    canvas.fill(WHITE)

    # offset to convert coordinats from clipped screen to normal screen
    offset_coords = (left_vision_border, 0)

    # ball's alpha angle
    alpha = convert_to_rad(alpha_initial + alpha_rnd_offset)

    information_text = f'Speed: {speed}, alpha: {int(alpha_initial + alpha_rnd_offset)}, h: {ball_start_x}'
    information_text_x_position = int(WIDTH*0.01)
    information_text_y_position = int(HEIGHT*0.01)

    result_text_positive = "Catched! To repeat press any button."
    result_text_negative = "Losed! To repeat press any button."
    result_text_x_position = information_text_x_position
    result_text_y_position = information_text_y_position*4

    ball_for_experiment = Ball(
        radius=ball_radius, x_start=ball_start_x, y_start=ball_start_y, color=RED, renderer=CIRCLE_RENDERER)

    cannon_for_experiment = Cannon(
        x_position=ball_start_x, y_position=ball_start_y, thickness=ball_radius/4, \
            length=ball_radius*2, color=BLUE, renderer=RECT_RENDERER)

    platform_for_experiment = Platform(
        L=ball_radius*2, x_start=WIDTH-5, y_start=int(HEIGHT/2), color=BLACK, renderer=RECT_RENDERER)

    firstVisibilityBorder = VisibilityBorder(
        position=left_vision_border, start=0, end=HEIGHT, color=BLACK, renderer=LINE_RENDERER)

    secondVisibilityBorder = VisibilityBorder(
        position=right_vision_border, start=0, end=HEIGHT, color=BLACK, renderer=LINE_RENDERER)

    predictedPath = PredictedPath(
        color=GREEN, size=2, draw_border=right_vision_border, renderer=CIRCLE_RENDERER)

    informationBox = InformationBox(
        font=screen_font, text=information_text, x_pos=information_text_x_position, \
            y_pos=information_text_y_position, color=BLACK)

    informationBoxPositive = InformationBox(
        font=screen_font_result, text=result_text_positive, x_pos=result_text_x_position, \
            y_pos=result_text_y_position, color=GREEN)

    informationBoxNegative = InformationBox(
        font=screen_font_result, text=result_text_negative, x_pos=result_text_x_position, \
            y_pos=result_text_y_position, color=RED)

    experiment = Experiment(
        items=(informationBox, ball_for_experiment, platform_for_experiment, \
            firstVisibilityBorder, secondVisibilityBorder, predictedPath, cannon_for_experiment), \
            canvas=canvas, background_color=WHITE)

    experiment.render()
    pygame.display.update()

    # ball trajectory to fly
    ball_x_trajectory, ball_y_trajectory = ball_trajectory(
        speed=speed, alpha=alpha, start_h=ball_start_h, time_steps=time_steps, g=g, width=WIDTH)

    current_time = 0
    ball_visible_path = []  # list to store detected ball's trajectory

    while True:
        while current_time < time_steps-1:
            # if ball in the middle of screen
            if ball_for_experiment.is_visible(left_border=firstVisibilityBorder.position,
                                              right_border=secondVisibilityBorder.position):

                if current_time % screenshot_steps == 0:
                    canvas_clipped.fill((WHITE))
                    # take only the part of screen between two borders
                    canvas_clipped.blit(canvas, (-firstVisibilityBorder.position, 0))
                    image = capture_image(canvas=canvas_clipped, renderer = ARRAY_RENDERER)

                    ball_сenter = get_ball_center(
                        image=image, offset_coords=offset_coords)
                    try:
                        x_ball, y_ball = ball_сenter
                    except:
                        pass
                    else:
                        ball_visible_path.append((x_ball, y_ball))

                # we need at least three points to biuld extrapolation
                if len(ball_visible_path) > 2:

                    first_point = ball_visible_path[0]
                    middle_point = ball_visible_path[len(ball_visible_path)//2]
                    last_point = ball_visible_path[-1]

                    ball_path_for_analysis = [first_point, middle_point, last_point]

                    try:
                        x_predicted, y_predicted = predict_path(
                            ball_visible_path=ball_path_for_analysis, width=WIDTH)
                    except:
                        pass
                    else:
                        predictedPath.update(x_predicted, y_predicted)
                        destination = get_destination(platform=platform_for_experiment,
                                                      predictedPath=predictedPath, height=HEIGHT, width=WIDTH, r=ball_for_experiment.R)
                        if destination is not None:
                            platform_for_experiment.destination = destination

            x_next_for_ball = ball_x_trajectory[current_time]
            y_next_for_ball = convert_to_screen_coords(
                ball_y_trajectory[current_time], HEIGHT)

            ball_for_experiment.move(x_next_for_ball, y_next_for_ball)

            platform_for_experiment.go_to_destination_point(
                steps=platform_steps, height=HEIGHT)

            experiment.render()

            if ball_for_experiment.is_catched(platform=platform_for_experiment):
                current_time = time_steps
                informationBoxPositive.render(canvas)
                pygame.display.update()
                break

            if ball_for_experiment.is_losed(width=WIDTH, height=HEIGHT):
                current_time = time_steps
                informationBoxNegative.render(canvas)
                pygame.display.update()
                break

            pygame.display.update()
            clock.tick(FPS)
            current_time += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            elif event.type == pygame.KEYDOWN:
                return 'repeat'


if __name__ == '__main__':
    result = 'repeat'

    while result == 'repeat':
        alpha_rnd_offset = rd.randint(0, 15)

        speed_rnd =  rd.randint(50, 200)
        result = main(speed=speed_rnd, alpha_rnd_offset = alpha_rnd_offset)

    sys.exit()