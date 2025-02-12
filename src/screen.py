"""
    https://github.com/vike256/Unibot
    For license see LICENSE

    Consider donating: https://github.com/vike256#donations

    ./src/screen.py
    This class is used to:
        - Capture a screenshot,
            detect any targets in the screenshot,
            and then return coordinates of the closest target.
        - Check if a target is in the center of the screen. If true then click.
"""
import cv2
import numpy as np
import dxcam
from mss import mss
from pyautogui import size


class Screen:
    def __init__(self, config):
        self.capture_method = config.capture_method

        if self.capture_method == 'dxcam':
            self.cam = dxcam.create(output_color="BGR")
        else:
            self.cam = mss()

        self.offset = config.offset

        if config.auto_detect_resolution:
            screen_size = size()
            self.screen = (screen_size.width, screen_size.height)
        else:
            self.screen = (config.resolution_x, config.resolution_y)

        self.screen_center = (self.screen[0] // 2, self.screen[1] // 2)
        self.screen_region = (
            0,
            0,
            self.screen[0],
            self.screen[1]
        )
        self.fov = config.fov
        self.fov_center = (self.fov // 2, self.fov // 2)
        self.fov_region = (
            self.screen_center[0] - self.fov // 2,
            self.screen_center[1] - self.fov // 2 - self.offset,
            self.screen_center[0] + self.fov // 2,
            self.screen_center[1] + self.fov // 2 - self.offset
        )
        self.detection_type = config.detection_type
        self.upper_color = config.upper_color
        self.lower_color = config.lower_color
        self.fps = config.fps
        self.aim_height = config.aim_height
        self.debug = config.debug
        self.mask = None
        self.thresh = None
        self.target = None
        self.closest_contour = None
        self.img = None

        # Setup debug display
        if self.debug:
            self.display_mode = config.display_mode
            self.window_name = 'Unibot Display'
            self.window_resolution = (
                self.screen[0] // 2,
                self.screen[1] // 2
            )
            cv2.namedWindow(self.window_name)

    def __del__(self):
        del self.cam

    def screenshot(self, region):
        while True:
            image = self.cam.grab(region)
            if image is not None:
                return np.array(image)

    def get_target(self, recoil_offset):
        recoil_offset = int(recoil_offset)
        self.target = None
        trigger = False
        self.closest_contour = None

        self.img = self.screenshot(self.get_region(self.fov_region, recoil_offset))
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        if self.detection_type == 'pixel':
            lit_pixels = np.where(self.mask == 255)
            if len(lit_pixels[0]) > 0:
                min_distance = float('inf')

                for x, y in zip(lit_pixels[1], lit_pixels[0]):
                    x -= self.fov_center[0]
                    y -= self.fov_center[1]
                    distance = np.sqrt(x**2 + y**2)

                    if distance < min_distance:
                        min_distance = distance
                        self.target = (x, y)
                        if min_distance == 0:
                            trigger = True
                            break

        elif self.detection_type == 'shape':
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(self.mask, kernel, iterations=5)
            self.thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            if len(contours) != 0:
                min_distance = float('inf')
                for contour in contours:
                    rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)
                    x = rect_x + rect_w // 2 - self.fov_center[0]
                    y = int(rect_y + rect_h * (1 - self.aim_height)) - self.fov_center[0]
                    distance = np.sqrt(x**2 + y**2)
                    if distance < min_distance:
                        min_distance = distance
                        self.closest_contour = contour
                        self.target = (x, y)

                value = 8
                if (
                    # Check if crosshair is inside the closest target
                    cv2.pointPolygonTest(
                        self.closest_contour, (self.fov_center[0], self.fov_center[1]), False) >= 0 and

                    # Eliminate a lot of false positives by also checking pixels near the crosshair.
                    cv2.pointPolygonTest(
                        self.closest_contour, (self.fov_center[0] + value, self.fov_center[1]), False) >= 0 and
                    cv2.pointPolygonTest(
                        self.closest_contour, (self.fov_center[0] - value, self.fov_center[1]), False) >= 0 and
                    cv2.pointPolygonTest(
                        self.closest_contour, (self.fov_center[0], self.fov_center[1] + value), False) >= 0 and
                    cv2.pointPolygonTest(
                        self.closest_contour, (self.fov_center[0], self.fov_center[1] - value), False) >= 0
                ):
                    trigger = True

        if self.debug:
            self.debug_display(recoil_offset)

        return self.target, trigger

    @staticmethod
    def get_region(region, recoil_offset):
        region = (
            region[0],
            region[1] - recoil_offset,
            region[2],
            region[3] - recoil_offset
        )
        return region

    def debug_display(self, recoil_offset):
        if self.display_mode == 'game':
            debug_img = self.img
        else:
            if self.detection_type == 'pixel':
                debug_img = self.mask
                debug_img = cv2.cvtColor(debug_img, cv2.COLOR_GRAY2BGR)
            else:
                debug_img = self.thresh
                debug_img = cv2.cvtColor(debug_img, cv2.COLOR_GRAY2BGR)

        full_img = self.screenshot(self.screen_region)

        # Draw line to the closest target
        if self.target is not None:
            debug_img = cv2.line(
                debug_img,
                self.fov_center,
                (self.target[0] + self.fov_center[0], self.target[1] + self.fov_center[1]),
                (0, 255, 0),
                2
            )

        if self.detection_type == 'pixel':
            # Draw FOV circle
            debug_img = cv2.circle(
                debug_img,
                self.fov_center,
                self.fov // 2,
                (0, 255, 0),
                1
            )
        elif self.detection_type == 'shape':
            # Draw rectangle around closest target
            if self.closest_contour is not None:
                x, y, w, h = cv2.boundingRect(self.closest_contour)
                debug_img = cv2.rectangle(
                    debug_img,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    2
                )
            # Draw FOV
            debug_img = cv2.rectangle(
                debug_img,
                (0, 0),
                (self.fov, self.fov),
                (0, 255, 0),
                2
            )

        offset_x = (self.screen[0] - self.fov) // 2
        offset_y = (self.screen[1] - self.fov) // 2 - self.offset - recoil_offset
        full_img[offset_y:offset_y+debug_img.shape[0], offset_x:offset_x+debug_img.shape[1]] = debug_img
        # Draw a rectangle crosshair
        full_img = cv2.rectangle(
            full_img,
            (self.screen_center[0] - 5, self.screen_center[1] - 5),
            (self.screen_center[0] + 5, self.screen_center[1] + 5),
            (255, 255, 255),
            1
        )
        full_img = cv2.resize(full_img, self.window_resolution)
        cv2.imshow(self.window_name, full_img)
        cv2.waitKey(1)
