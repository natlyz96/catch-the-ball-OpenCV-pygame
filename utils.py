import cv2
import numpy as np
from scipy.interpolate import interp1d

def convert_to_rad(deg):
    return np.deg2rad(deg)


def convert_to_screen_coords(y, height):
    return y*(-1)+height


def ball_trajectory(speed, alpha, start_h, time_steps, g, width):
    vx = speed*np.cos(alpha)
    vy = speed*np.sin(alpha)

    t_flight = width*1.2/vx

    t = np.linspace(0, t_flight, time_steps)
    x = vx * t
    y = vy * t - 0.5*g*(t**2) + start_h

    return x, y


def get_ball_center(image, offset_coords=None):
    detector = cv2.SimpleBlobDetector_create()
    blobs = detector.detect(image)
    try:
        ball, *_ = blobs
    except:
        return None
    else:
        if offset_coords is None:
            return ball.pt
        else:
            offset_x, offset_y = offset_coords
            x_pred, y_pred = ball.pt
            return (x_pred+offset_x, y_pred+offset_y)


def capture_image(canvas, renderer):
    frame = renderer.array3d(canvas)
    frame = cv2.transpose(frame)
    frame = cv2.cvtColor((frame), cv2.COLOR_RGB2BGR)
    return frame


def get_extrapolation_for_points(x, y, width, kind='quadratic'):

    f_res = interp1d(x, y, kind=kind, fill_value='extrapolate')
    x_first, *_ = x
    x_res = np.linspace(x_first, width)
    y_res = f_res(x_res)
    return (x_res, y_res)


def predict_path(ball_visible_path, width):
    x_ball_coords = []
    y_ball_coords = []

    for el in ball_visible_path:
        x, y = el
        x_ball_coords.append(x)
        y_ball_coords.append(y)
    try:
        x_res, y_res = get_extrapolation_for_points(x=np.array(
            x_ball_coords, dtype=np.float64), y=np.array(y_ball_coords, dtype=np.float64), width=width)
    except:
        return None
    else:
        return (x_res, y_res)


def get_destination(platform, predictedPath, height, width, r):
    x_res = predictedPath.x
    y_res = predictedPath.y

    if x_res is not None:
        try:
            touch_the_ground, *_ = x_res[y_res >= height]
            return height - platform.L
        except:
            ball_cross_the_border_y, * \
                _ = y_res[x_res >= width - platform.thickness]
            return ball_cross_the_border_y - r
    else:
        return None