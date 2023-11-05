"""
    https://github.com/vike256/Unibot
    For license see LICENSE

    Consider donating: https://github.com/vike256#donations

    ./src/utils.py
    This class is used to read the config and to check if each feature is on.
"""
import win32api
from time import sleep

from configReader import ConfigReader


class Utils:
    def __init__(self):
        self.config = ConfigReader()
        self.reload_config()

        self.delay = 0.2
        self.key_reload_config = self.config.key_reload_config
        self.key_toggle_aim = self.config.key_toggle_aim
        self.key_toggle_recoil = self.config.key_toggle_recoil
        self.key_trigger = self.config.key_trigger
        self.key_exit = self.config.key_exit
        self.aim_keys = self.config.aim_keys
        self.aim_state = False
        self.recoil_state = False

    def check_key_binds(self):  # Return a boolean based on if the config needs to be reloaded
        if win32api.GetAsyncKeyState(self.key_reload_config) < 0:
            return True

        if win32api.GetAsyncKeyState(self.key_toggle_aim) < 0:
            self.aim_state = not self.aim_state
            print("AIM: " + str(self.aim_state))
            sleep(self.delay)

        if win32api.GetAsyncKeyState(self.key_toggle_recoil) < 0:
            self.recoil_state = not self.recoil_state
            print("RECOIL: " + str(self.recoil_state))
            sleep(self.delay)
        
        if win32api.GetAsyncKeyState(self.key_exit) < 0:
            print("Exiting")
            exit(1)
        return False

    def reload_config(self):
        self.config.read_config()

    def get_aim_state(self):
        if self.aim_state:
            if self.aim_keys[0] == 'off':
                return True
            else:
                for key in self.aim_keys:
                    if win32api.GetAsyncKeyState(key) < 0:
                        return True
        return False

    def get_trigger_state(self):
        if win32api.GetAsyncKeyState(self.key_trigger) < 0:
            return True
        return False

    @staticmethod
    def print_attributes(obj):
        attributes = vars(obj)
        for attribute, value in attributes.items():
            print(f'{attribute}: {value}')
