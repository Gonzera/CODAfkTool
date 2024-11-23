from asyncore import read
from time import sleep
from PIL import ImageGrab, Image
import numpy as np
import cv2 as cv
from input import move
import win32gui
import win32com.client as win32


img_path = "images/"

def resize_window():
    pass
 

def capture_screenshot():
    i = ImageGrab.grab()
    i.save("s.png")
    arr = np.array(i)
    return arr

def read_poi_image(poi: str):
    img = Image.open(f"images/{poi}.png")
    arr = np.array(img)
    return arr

def try_find_poi(poi: str, screenshot = None):
    if screenshot is None:
        screenshot = capture_screenshot()
    poi_image = read_poi_image(poi)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
    poi_image = cv.cvtColor(poi_image, cv.COLOR_RGB2BGR)

    result = cv.matchTemplate(screenshot, poi_image, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    # print(max_val)
    # print(max_loc)
    x, y = max_loc
    return x, y, max_val

if __name__ == "__main__":
    hwnd = win32gui.FindWindow(None, "Call of Duty®")
    win32gui.MoveWindow(hwnd, 2, 2, 1280, 720, False)