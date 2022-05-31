class Ball():
    def __init__(self, radius,
                 x_start, y_start, color, renderer):
        self.color = color
        self.R = radius
        self.coords = (x_start, y_start)
        self.renderer = renderer

    def render(self, canvas):
        self.renderer(
            canvas, self.color, self.coords, self.R)

    def is_visible(self, left_border, right_border):
        x, y = self.coords
        if x > left_border+self.R and x < right_border-self.R:
            return True
        else:
            return False

    def move(self, x_center, y_center):
        self.coords = (x_center, y_center)

    def is_catched(self, platform):
        x, y = self.coords

        platform_x, platform_y_start, *_ = platform.position
        platform_y_end = platform_y_start + platform.L

        if x+self.R >= platform_x and y >= platform_y_start and y <= platform_y_end:
            return True
        return False

    def is_losed(self, width, height):
        x, y = self.coords
        if y+self.R >= height or x-self.R >= width or y-2*self.R >= height or y+2*self.R <= 0:
            return True
        else:
            return False


class Cannon():
    def __init__(self, x_position, y_position, thickness, length, color, renderer):
        self.color = color
        self.renderer = renderer
        self.position = (x_position, y_position, thickness, length)

    def render(self, canvas):
        self.renderer(canvas, self.color, self.position)


class Platform():
    def __init__(self, L, x_start, y_start, color, renderer):
        self.L = L
        self.thickness = int(self.L/8)
        self.color = color
        self.position = (x_start, y_start, self.thickness, self.L)
        self.destination = y_start
        self.rederer = renderer

    def render(self, canvas):
        self.rederer(canvas, self.color, self.position)

    def go_to_destination_point(self, steps, height):
        _, y, *_ = self.position
        while self.destination != y and steps > 0:
            if y < self.destination:
                step = 1
            else:
                step = -1
            self.move(y + step, height)
            steps -= 1
            _, y, *_ = self.position

    def move(self, move_to_y, height):
        x, _, thickness, length = self.position
        if move_to_y >= 0 and move_to_y <= height-length:
            self.position = (x, move_to_y, thickness, length)


class Experiment():
    def __init__(self, items, canvas, background_color):
        self.canvas = canvas
        self.background = background_color
        self.items = items

    def render(self):
        self.canvas.fill(self.background)
        for item in self.items:
            item.render(self.canvas)


class VisibilityBorder():
    def __init__(self, position, start, end, color, renderer):
        self.position = position
        self.color = color
        self.begin_from_y = start
        self.end_with_y = end
        self.renderer = renderer

    def render(self, canvas):
        self.renderer(canvas, self.color,
                      (self.position, self.begin_from_y), (self.position, self.end_with_y))


class InformationBox():
    def __init__(self, font, text, x_pos, y_pos, color):
        self.font = font
        self.text = text
        self.coords = (x_pos, y_pos)
        self.color = color

    def render(self, canvas):
        text_surface = self.font.render(self.text, False, self.color)
        canvas.blit(text_surface, self.coords)


class PredictedPath():
    def __init__(self, color, size, draw_border, renderer):
        self.color = color
        self.size = size
        self.draw_from = draw_border
        self.x = None
        self.y = None
        self.renderer = renderer

    def update(self, x, y):
        self.x = x
        self.y = y

    def render(self, canvas):
        if self.x is not None:
            for i in range(len(self.x)):
                x_c = self.x[i]
                y_c = self.y[i]
                if x_c > self.draw_from:
                    self.renderer(
                        canvas, self.color, (x_c, y_c), self.size)
