Welcome to this project.

This is a flying ball simulation with OpenCV and Pygame.
The main purpose is to catch the ball with the platform using the only middle part
of the screen between two borders.

I use the opencv-python module to detect the ball position on the captured screen. 
And then apply scipy.interp1d quadratic interpolation function to extrapolate
captured trajectory.

Usually, the platform can successfully catch the ball. But you can adjust some input 
parameters like the ball's speed, the ball's radius, or initial angle to make 
the task more difficult.

How to use: 
1) You need python 3. This code was developed and tested on python 3.8.5.
2) Install all needed packages using "pip install -r requirements.txt" command and have fun.