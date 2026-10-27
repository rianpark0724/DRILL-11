from pico2d import *
import sys
import random
import time

from grass import Grass
from boy import Boy

# Game object class here


def handle_events():
    global running
    global last_input_time
    global pressed_directions

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            elif event.key in (SDLK_LEFT, SDLK_RIGHT):
                last_input_time = time.monotonic()
                if event.key in pressed_directions:
                    pressed_directions.remove(event.key)
                pressed_directions.append(event.key)
                boy.start_running(-1 if event.key == SDLK_LEFT else 1)
            else:
                last_input_time = time.monotonic()
                if event.key == SDLK_SPACE and boy.state == 'SLEEP':
                    boy.wake()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            last_input_time = time.monotonic()
            if event.key in pressed_directions:
                pressed_directions.remove(event.key)
            if pressed_directions:
                direction = -1 if pressed_directions[-1] == SDLK_LEFT else 1
                boy.start_running(direction)
            else:
                boy.stop_running()


def reset_world():
    global world
    global boy
    global last_input_time
    global pressed_directions

    world = []
    last_input_time = time.monotonic()
    pressed_directions = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    if boy.state == 'IDLE' and time.monotonic() - last_input_time >= 5:
        boy.sleep()

    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True

open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
# finalization code
close_canvas()
