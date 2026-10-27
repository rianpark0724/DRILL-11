import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import boy as boy_module
import main as game


class AutoRunTests(unittest.TestCase):
    def setUp(self):
        self.clock = patch('time.monotonic', return_value=100.0).start()
        patch('boy.load_image', return_value=Mock()).start()
        patch('grass.load_image', return_value=Mock()).start()
        patch('boy.get_canvas_width', return_value=800).start()
        self.addCleanup(patch.stopall)
        game.reset_world()
        game.running = True
        self.boy = game.boy

    def event(self, key, event_type=None):
        event = SimpleNamespace(type=event_type or game.SDL_KEYDOWN, key=key)
        with patch.object(game, 'get_events', return_value=[event]):
            game.handle_events()

    def test_entry_speed_size_and_ground_alignment(self):
        self.boy.face_dir = -1
        self.event(game.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.boy.update()
        self.assertEqual(self.boy.x, 390)
        self.assertEqual((self.boy.speed, self.boy.size), (10, 150))
        self.boy.draw()
        args = self.boy.image.clip_composite_draw.call_args.args
        self.assertEqual(args[1], 0)
        self.assertEqual(args[7] - args[9] / 2, self.boy.y - 50)

    def test_both_boundaries_preserve_timer(self):
        self.event(game.SDLK_a)
        for x, direction, expected in [(1, -1, (75, 1)), (799, 1, (725, -1))]:
            self.boy.x, self.boy.face_dir = x, direction
            self.boy.update()
            self.assertEqual((self.boy.x, self.boy.face_dir), expected)
            self.assertEqual(self.boy.auto_run.started_at, 100)

    def test_timeout_and_fresh_sleep_deadline(self):
        self.event(game.SDLK_a)
        self.clock.return_value = 104.999
        game.update_world()
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.clock.return_value = 105
        game.update_world()
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual((self.boy.speed, self.boy.size), (5, 100))
        self.assertIsNone(self.boy.auto_run.started_at)
        self.clock.return_value = 109.999
        game.update_world()
        self.assertEqual(self.boy.state, 'IDLE')
        self.clock.return_value = 110
        game.update_world()
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_direction_cancel_and_key_priority(self):
        for key, direction in [(game.SDLK_LEFT, -1), (game.SDLK_RIGHT, 1)]:
            game.reset_world()
            self.event(game.SDLK_a)
            self.clock.return_value += 5
            self.event(key)
            game.update_world()
            self.assertEqual(game.boy.state, 'RUN')
            self.assertEqual(game.boy.face_dir, direction)
            self.assertEqual((game.boy.speed, game.boy.size), (5, 100))
            self.event(key, game.SDL_KEYUP)
            self.assertEqual(game.boy.state, 'IDLE')
        self.event(game.SDLK_LEFT)
        self.event(game.SDLK_RIGHT)
        self.assertEqual(game.boy.face_dir, 1)
        self.event(game.SDLK_RIGHT, game.SDL_KEYUP)
        self.assertEqual(game.boy.face_dir, -1)

    def test_ignored_inputs_do_not_restart_or_cancel(self):
        self.event(game.SDLK_a)
        self.clock.return_value = 103
        self.event(game.SDLK_a)
        self.event(game.SDLK_SPACE)
        game.pressed_directions = [game.SDLK_LEFT, game.SDLK_RIGHT]
        self.event(game.SDLK_RIGHT, game.SDL_KEYUP)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.assertEqual(self.boy.auto_run.started_at, 100)
        self.clock.return_value = 105
        game.update_world()
        self.assertEqual(self.boy.state, 'IDLE')

    def test_existing_sleep_wake_and_exit(self):
        self.event(game.SDLK_LEFT)
        self.event(game.SDLK_a)
        self.assertEqual(self.boy.state, 'RUN')
        self.event(game.SDLK_LEFT, game.SDL_KEYUP)
        self.clock.return_value = 105
        game.update_world()
        self.event(game.SDLK_a)
        self.assertEqual(self.boy.state, 'SLEEP')
        self.event(game.SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')
        self.boy.sleep()
        self.event(game.SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'RUN')
        self.event(game.SDLK_ESCAPE)
        self.assertFalse(game.running)
        game.running = True
        self.event(0, game.SDL_QUIT)
        self.assertFalse(game.running)


if __name__ == '__main__':
    unittest.main()
