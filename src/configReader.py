"""
    https://github.com/vike256/Unibot
    For license see LICENSE

    Consider donating: https://github.com/vike256#donations

    ./src/configReader.py
    This class is used to read the config.
"""
from configparser import ConfigParser
import numpy as np
import os


class ConfigReader:
    def __init__(self):
        self.parser = ConfigParser()

        # Communication
        self.com_type = None
        self.encrypt = None
        self.ip = None
        self.port = None
        self.com_port = None

        # Screen
        self.detection_type = None
        self.upper_color = None
        self.lower_color = None
        self.fov = None
        self.fps = None
        self.auto_detect_resolution = None
        self.resolution_x = None
        self.resolution_y = None

        # Aim
        self.offset = None
        self.smooth = None
        self.speed = None
        self.x_multiplier = None
        self.head_height = None

        # Recoil
        self.recoil_mode = None
        self.recoil_x = None
        self.recoil_y = None
        self.max_offset = None
        self.recoil_recover = None

        # Trigger
        self.trigger_delay = None
        self.trigger_randomization = None

        # Rapid fire
        self.target_cps = None

        # Key binds
        self.key_reload_config = None
        self.key_toggle_aim = None
        self.key_toggle_recoil = None
        self.key_exit = None
        self.key_trigger = None
        self.key_rapid_fire = None
        self.aim_keys = []

        # Debug
        self.debug = None
        self.display_mode = None

        # Get config path and read it
        self.path = os.path.join(os.path.dirname(__file__), '../config.ini')
        self.parser.read(self.path)
        self.read_config()

    def read_config(self):
        # Get communication settings
        value = self.parser.get('communication', 'type').lower()
        com_type_list = ['none', 'driver', 'serial', 'socket']
        if value in com_type_list:
            self.com_type = value
        else:
            print('ERROR: Invalid com_type value')
            exit(1)

        value = self.parser.get('communication', 'encrypt').lower()
        if value == 'true':
            self.encrypt = True
        else:
            self.encrypt = False
        
        match self.com_type:
            case 'socket':
                self.ip = self.parser.get('communication', 'ip')
                self.port = int(self.parser.get('communication', 'port'))
            case 'serial':
                self.com_port = self.parser.get('communication', 'com_port')

        # Get screen settings
        value = self.parser.get('screen', 'detection_type').lower()
        detection_type_list = ['pixel', 'shape']
        if value in detection_type_list:
            self.detection_type = value
        else:
            print('ERROR: Invalid detection_type value')
            exit(1)

        upper_color = self.parser.get('screen', 'upper_color').split(',')
        lower_color = self.parser.get('screen', 'lower_color').split(',')
        for i in range(0, 3):
            upper_color[i] = int(upper_color[i].strip())
        for i in range(0, 3):
            lower_color[i] = int(lower_color[i].strip())
        self.upper_color = np.array(upper_color)
        self.lower_color = np.array(lower_color)

        self.fov = int(self.parser.get('screen', 'fov'))
        fps_value = int(self.parser.get('screen', 'fps'))
        self.fps = int(np.floor(1000 / fps_value + 1))

        value = self.parser.get('screen', 'auto_detect_resolution').lower()
        if value == 'true':
            self.auto_detect_resolution = True
        else:
            self.auto_detect_resolution = False

        self.resolution_x = int(self.parser.get('screen', 'resolution_x'))
        self.resolution_y = int(self.parser.get('screen', 'resolution_y'))

        # Get aim settings
        self.offset = int(self.parser.get('aim', 'offset'))

        value = float(self.parser.get('aim', 'smooth'))
        if 0 <= value < 1:
            self.smooth = 1 - value
        else:
            print('ERROR: Invalid smooth value')
            exit(1)

        self.speed = float(self.parser.get('aim', 'speed'))
        self.x_multiplier = float(self.parser.get('aim', 'x_multiplier'))

        value = float(self.parser.get('aim', 'head_height'))
        if 0 <= value <= 1:
            self.head_height = value
        else:
            print('ERROR: Invalid head_height value')
            exit(1)

        # Get recoil settings
        value = self.parser.get('recoil', 'mode').lower()
        recoil_mode_list = ['move', 'offset']
        if value in recoil_mode_list:
            self.recoil_mode = value
        else:
            print('ERROR: Invalid recoil_mode value')
            exit(1)

        match self.recoil_mode:
            case 'move':
                self.recoil_x = float(self.parser.get('recoil', 'recoil_x'))
                self.recoil_y = float(self.parser.get('recoil', 'recoil_y'))
            case 'offset':
                self.recoil_y = float(self.parser.get('recoil', 'recoil_y'))
                self.max_offset = int(self.parser.get('recoil', 'max_offset'))
                self.recoil_recover = float(self.parser.get('recoil', 'recover'))

        # Get trigger settings
        self.trigger_delay = int(self.parser.get('trigger', 'trigger_delay'))
        self.trigger_randomization = int(self.parser.get('trigger', 'trigger_randomization'))

        # Get rapid fire settings
        self.target_cps = int(self.parser.get('rapid_fire', 'target_cps'))

        # Get keybind settings
        self.key_reload_config = read_hex(self.parser.get('key_binds', 'key_reload_config'))
        self.key_toggle_aim = read_hex(self.parser.get('key_binds', 'key_toggle_aim'))
        self.key_toggle_recoil = read_hex(self.parser.get('key_binds', 'key_toggle_recoil'))
        self.key_exit = read_hex(self.parser.get('key_binds', 'key_exit'))
        self.key_trigger = read_hex(self.parser.get('key_binds', 'key_trigger'))
        self.key_rapid_fire = read_hex(self.parser.get('key_binds', 'key_rapid_fire'))
        aim_keys_str = self.parser.get('key_binds', 'aim_keys')
        if not aim_keys_str == 'off':
            aim_keys_str = aim_keys_str.split(',')
            for key in aim_keys_str:
                self.aim_keys.append(read_hex(key))
        else:
            self.aim_keys = ['off']

        # Get debug settings
        value = self.parser.get('debug', 'enabled').lower()
        if value == 'true':
            self.debug = True
            value = self.parser.get('debug', 'display_mode').lower()
            display_mode_list = ['game', 'mask']
            if value in display_mode_list:
                self.display_mode = value
            else:
                print('ERROR: Invalid display_mode value')
                exit(1)
        else:
            self.debug = False


def read_hex(string):
    return int(string, 16)
