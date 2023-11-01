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
        self.move_x, self.move_y = (0, 0)

        if not state:
            return

        if target is not None:
            x, y = target

            x *= self.speed
            y *= self.speed / self.x_multiplier

            # Apply smoothing with the last x and y value
            x = self.previous_x + self.smooth * (x - self.previous_x)
            y = self.previous_y + self.smooth * (y - self.previous_y)

            x += self.remainder_x
            y += self.remainder_y
            self.remainder_x = x
            self.remainder_y = y
            x = int(x)
            y = int(y)
            self.remainder_x -= x
            self.remainder_y -= y

            self.previous_x, self.previous_y = (x, y)
            self.move_x, self.move_y = (x, y)

    def apply_recoil(self, state, delta_time):
        if state:
            if delta_time != 0:
                if self.recoil_mode == 'move' and win32api.GetAsyncKeyState(0x01) < 0:
                    self.move_x += self.recoil_x / delta_time
                    self.move_y += self.recoil_y / delta_time
                elif self.recoil_mode == 'offset':
                    if win32api.GetAsyncKeyState(0x01) < 0:
                        if self.recoil_offset < self.max_offset:
                            self.recoil_offset += self.recoil_y / delta_time
                            if self.recoil_offset > self.max_offset:
                                self.recoil_offset = self.max_offset
                    else:
                        if self.recoil_offset > 0:
                            self.recoil_offset -= self.recoil_recover / delta_time
                            if self.recoil_offset < 0:
                                self.recoil_offset = 0
        else:
            self.recoil_offset = 0
