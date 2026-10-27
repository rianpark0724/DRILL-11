from math import pi

from pico2d import load_image
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP'],
            transitions=[
                {'trigger': 'sleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'start_run', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'stop_run', 'source': 'RUN', 'dest': 'IDLE'},
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
        if self.state in ('IDLE', 'RUN'):
            self.frame = (self.frame + 1) % 8
        if self.state == 'RUN':
            self.x = max(0, min(800, self.x + self.face_dir * 5))

    def draw(self):
        is_sleeping = self.state == 'SLEEP'
        angle = self.face_dir * pi / 2 if is_sleeping else 0
        draw_y = self.y - 30 if is_sleeping else self.y
        if self.state == 'RUN':
            bottom = 100 if self.face_dir == 1 else 0
        else:
            bottom = 300 if self.face_dir == 1 else 200
        self.image.clip_composite_draw(
            self.frame * 100, bottom, 100, 100, angle, '', self.x, draw_y, 100, 100
        )