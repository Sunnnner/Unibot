"""
    https://github.com/vike256/Unibot
    For license see LICENSE

    ./src/main.py
    This is the main loop of the program.
"""
import time

from cheats import Cheats
from mouse import Mouse
from screen import Screen
from utils import Utils


def main():
    while True:
        start_time = time.time()

        utils = Utils()
        config = utils.config
        cheats = Cheats(config)
        mouse = Mouse(config)
        screen = Screen(config)

        print('ON')

        while True:
            delta_time = (time.time() - start_time) * 1000
            start_time = time.time()
            
            reload = utils.check_key_binds()
            if reload:
                break

            target, trigger = screen.get_target(cheats.recoil_offset)

            cheats.calculate_aim(utils.get_aim_state(), target)
            cheats.apply_recoil(utils.recoil_state, delta_time)
            if utils.get_trigger_state() and trigger:
                mouse.click()
            mouse.move(cheats.move_x, cheats.move_y)

            time_spent = (time.time() - start_time) * 1000
            if time_spent < screen.fps:
                time.sleep((screen.fps - time_spent) / 1000)

        del utils
        del cheats
        del mouse
        del screen
        print('Reloading')


if __name__ == "__main__":
    main()
