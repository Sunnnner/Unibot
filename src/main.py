"""
    https://github.com/vike256/Unibot
    For license see LICENSE

    Consider donating: https://github.com/vike256#donations

    ./src/main.py
    This is the main loop of the program.
"""
import time
import numpy as np

from cheats import Cheats
from mouse import Mouse
from screen import Screen
from utils import Utils


def main():
    # Program loop
    while True:
        # Track delta time
        start_time = time.time()

        utils = Utils()
        config = utils.config
        cheats = Cheats(config)
        mouse = Mouse(config)
        screen = Screen(config)

        print('Unibot ON')

        # Cheat loop
        while True:
            delta_time = (time.time() - start_time) * 1000
            start_time = time.time()
            
            reload_config = utils.check_key_binds()
            if reload_config:
                break

            if utils.get_aim_state() or utils.get_trigger_state():
                # Get target position and check if there is a target in the center of the screen
                target, trigger = screen.get_target(cheats.recoil_offset)

                # Shoot if target in the center of the screen
                if utils.get_trigger_state() and trigger:
                    if config.trigger_delay != 0:
                        delay_before_click = (np.random.randint(config.trigger_randomization) + config.trigger_delay) / 1000
                    else:
                        delay_before_click = 0
                    mouse.click(delay_before_click)
                else:
                    # Calculate movement based on target position
                    cheats.calculate_aim(utils.get_aim_state(), target)

            if utils.get_rapid_fire_state():
                mouse.click()

            # Apply recoil
            cheats.apply_recoil(utils.recoil_state, delta_time)

            # Move the mouse based on the previous calculations
            mouse.move(cheats.move_x, cheats.move_y)

            # Do not loop above the set refresh rate
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
