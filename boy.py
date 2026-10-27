from math import pi
import time

from pico2d import load_image, get_canvas_width
from transitions import Machine


class AutoRun:
    DURATION = 5.0
    SPEED_MULTIPLIER = 2
    SCALE = 1.5

    def __init__(self, boy):
        self.boy = boy
        self.started_at = None

    def enter(self):
        self.started_at = time.monotonic()
        self.boy.speed = self.boy.RUN_SPEED * self.SPEED_MULTIPLIER
        self.boy.size = self.boy.BASE_SIZE * self.SCALE

    def exit(self):
        self.started_at = None
        self.boy.speed = self.boy.RUN_SPEED
        self.boy.size = self.boy.BASE_SIZE

    def update(self):
        boy = self.boy
        if time.monotonic() - self.started_at >= self.DURATION:
            boy.finish_auto_run()
            return
        half_width = boy.size / 2
        left, right = half_width, get_canvas_width() - half_width
        boy.x += boy.face_dir * boy.speed
        if boy.x <= left:
            boy.x, boy.face_dir = left, 1
        elif boy.x >= right:
            boy.x, boy.face_dir = right, -1


class Boy:
    RUN_SPEED = 5
    BASE_SIZE = 100

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.speed = self.RUN_SPEED
        self.size = self.BASE_SIZE
        self.auto_run = AutoRun(self)
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP', {
                'name': 'AUTORUN',
                'on_enter': self.auto_run.enter,
                'on_exit': self.auto_run.exit,
            }],
            transitions=[
                {'trigger': 'sleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'start_run', 'source': ['IDLE', 'SLEEP', 'AUTORUN'], 'dest': 'RUN'},
                {'trigger': 'stop_run', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'start_auto_run', 'source': 'IDLE', 'dest': 'AUTORUN'},
                {'trigger': 'finish_auto_run', 'source': 'AUTORUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )

    def start_running(self, direction):
        self.face_dir = direction
        if self.state != 'RUN':
            self.start_run()

    def stop_running(self):
        if self.state == 'RUN':
            self.stop_run()

    def update(self):
        if self.state in ('IDLE', 'RUN', 'AUTORUN'):
            self.frame = (self.frame + 1) % 8
        if self.state == 'RUN':
            self.x = max(0, min(get_canvas_width(), self.x + self.face_dir * self.speed))
        elif self.state == 'AUTORUN':
            self.auto_run.update()

    def draw(self):
        is_sleeping = self.state == 'SLEEP'
        angle = self.face_dir * pi / 2 if is_sleeping else 0
        draw_y = self.y - 30 if is_sleeping else self.y
        draw_y += (self.size - self.BASE_SIZE) / 2
        if self.state in ('RUN', 'AUTORUN'):
            bottom = 100 if self.face_dir == 1 else 0
        else:
            bottom = 300 if self.face_dir == 1 else 200
        self.image.clip_composite_draw(
            self.frame * 100, bottom, 100, 100, angle, '', self.x, draw_y, self.size, self.size
        )
