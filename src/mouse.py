"""
    https://github.com/vike256/Unibot
    For license see LICENSE

    Consider donating: https://github.com/vike256#donations

    ./src/mouse.py
    This class is used to do mouse input.
"""
import time
import numpy as np
import win32api
import win32con
import interception
import serial
import socket
import threading


class Mouse:
    def __init__(self, config):
        self.com_type = config.com_type
        self.click_thread = threading.Thread(target=self.send_click)
        self.last_click_time = time.time()
        self.target_cps = config.target_cps
        
        match self.com_type:
            case 'socket':
                self.symbols = '-,0123456789'
                self.code = 'UNIBOTCYPHER'
                self.encrypt = config.encrypt
                self.ip = config.ip
                self.port = config.port
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(f'Connecting to {self.ip}:{self.port}...')
                try:
                    self.client.connect((self.ip, self.port))
                except TimeoutError as e:
                    print(f'ERROR: Could not connect. {e}')
                    self.close_socket()
                    exit(1)
            case 'serial':
                self.symbols = '-,0123456789'
                self.code = 'UNIBOTCYPHER'
                self.encrypt = config.encrypt
                self.com_port = config.com_port
                self.board = serial.Serial(self.com_port, 115200)
            case 'driver':
                interception.auto_capture_devices(mouse=True)
            case 'none':
                pass

    def __del__(self):
        self.close_socket()

    def close_socket(self):
        if self.com_type == 'socket':
            if self.client is not None:
                self.client.close()

    def encrypt_command(self, command):
        if self.encrypt:
            encrypted_command = ""
            for char in command:
                if char in self.symbols:
                    index = self.symbols.index(char)
                    encrypted_command += self.code[index]
                else:
                    encrypted_command += char  # Keep non-symbol characters unchanged
            return encrypted_command
        else:
            return command

    def move(self, x, y):
        x = int(np.floor(x + 0.5))
        y = int(np.floor(y + 0.5))

        if x != 0 or y != 0:
            match self.com_type:
                case 'socket':
                    command = self.encrypt_command(f'M{x},{y}\r')
                    self.client.sendall(command.encode())
                    print(f'Sent: {command}\nReceived: {self.get_response()}')
                case 'serial':
                    command = self.encrypt_command(f'M{x},{y}\r')
                    self.board.write(command.encode())
                    print(f'Sent: {command}\nReceived: {self.get_response()}')
                case 'driver':
                    interception.move_relative(x, y)
                    print(f'M({x}, {y})')
                case 'none':
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
                    print(f'M({x}, {y})')

    def click(self):
        if (
                not self.click_thread.is_alive() and
                time.time() - self.last_click_time >= 1 / self.target_cps
        ):
            self.click_thread = threading.Thread(target=self.send_click)
            self.click_thread.start()

    def send_click(self):
        self.last_click_time = time.time()
        match self.com_type:
            case 'socket':
                self.client.sendall('C\r'.encode())
                print(f'Sent: Click\nReceived: {self.get_response()}')
            case 'serial':
                self.board.write('C\r'.encode())
                print(f'Sent: Click\nReceived: {self.get_response()}')
            case 'driver':
                random_delay = (np.random.randint(40) + 40) / 1000
                interception.mouse_down('left')
                time.sleep(random_delay)
                interception.mouse_up('left')
                print(f'C({random_delay * 1000:g})')
            case 'none':
                random_delay = (np.random.randint(40) + 40) / 1000
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(random_delay)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print(f'C({random_delay * 1000:g})')
        time.sleep((np.random.randint(10) + 25) / 1000)  # Sleep to avoid sending another click instantly after mouseup

    def get_response(self):  # Waits for a response before sending a new instruction
        match self.com_type:
            case 'socket':
                return f'Socket: {self.client.recv(4).decode()}'
            case 'serial':
                while True:
                    receive = self.board.readline().decode('utf-8').strip()
                    if len(receive) > 0:
                        return f'Serial: {receive}'
