"""
    https://github.com/vike256/Unibot
    For license see LICENSE

    Consider donating: https://github.com/vike256#donations

    ./src/cheats.py
"""
import win32api


class Cheats:
    def __init__(self, config):
        # Aim
        self.move_x, self.move_y = (0, 0)
        self.previous_x, self.previous_y = (0, 0)
        self.remainder_x, self.remainder_y = (0, 0)
        self.smooth = config.smooth
        self.speed = config.speed
        self.x_multiplier = config.x_multiplier

        # Recoil
        self.recoil_offset = 0
        self.recoil_mode = config.recoil_mode
        self.recoil_x = config.recoil_x
        self.recoil_y = config.recoil_y
        self.max_offset = config.max_offset
        self.recoil_recover = config.recoil_recover

    def calculate_aim(self, state, target):
        # Reset move values so the aim doesn't keep drifting when no targets are on the screen
        self.move_x, self.move_y = (0, 0)

        if state and target is not None:
            x, y = target

            # Calculate x and y speed
            x *= self.speed
            y *= self.speed / self.x_multiplier

            # Apply smoothing with the previous x and y value
            x = self.previous_x + self.smooth * (x - self.previous_x)
            y = self.previous_y + self.smooth * (y - self.previous_y)

            # Add the remainder from the previous calculation
            x += self.remainder_x
            y += self.remainder_y

            # Round x and y, and calculate the new remainder
            self.remainder_x = x
            self.remainder_y = y
            x = int(x)
            y = int(y)
            self.remainder_x -= x
            self.remainder_y -= y

            # Store the calculated values for next calculation
            self.previous_x, self.previous_y = (x, y)
            # Apply x and y to the move variables
            self.move_x, self.move_y = (x, y)

    def apply_recoil(self, state, delta_time):
        if state:
            if delta_time != 0:
                # Mode move just applies configured movement to the move values
                if self.recoil_mode == 'move' and win32api.GetAsyncKeyState(0x01) < 0:
                    self.move_x += self.recoil_x / delta_time
                    self.move_y += self.recoil_y / delta_time
                # Mode offset moves the camera upward, so it aims below target
                elif self.recoil_mode == 'offset':
                    # Add recoil_y to the offset when mouse1 is down
                    if win32api.GetAsyncKeyState(0x01) < 0:
                        if self.recoil_offset < self.max_offset:
                            self.recoil_offset += self.recoil_y / delta_time
                            if self.recoil_offset > self.max_offset:
                                self.recoil_offset = self.max_offset
                    # Start resetting the offset bit by bit if mouse1 is not down
                    else:
                        if self.recoil_offset > 0:
                            self.recoil_offset -= self.recoil_recover / delta_time
                            if self.recoil_offset < 0:
                                self.recoil_offset = 0
        else:
            # Reset recoil offset if recoil is off
            self.recoil_offset = 0
