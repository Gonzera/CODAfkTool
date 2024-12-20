from enum import Enum
from input import C, E, SPACE, click, move, holdKey, W, A, S, D, Q, X, pressKey, releaseKey
from image import capture_screenshot, try_find_poi
import threading
import random
import sys
import time
import logging
import win32gui
import win32api


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
file_handler = logging.FileHandler("afk.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(file_handler)


class State(Enum):
    AFK_KICK = ["afk_kick"]
    FIND_MATCH_ALT = ["find_match_alt"]
    FIND_MATCH = ["find_match"]
    IN_QUEUE = ["in_q"]
    IN_GAME = ["in_game"]
    # IN_GAME_WZ = "in_game_wz"
    LOADOUT_SELECTION = ["loadout"]

current_state: State | None = State.IN_GAME

def handle_state_change():
    global current_state
    if current_state == State.IN_GAME:
        threading.Thread(target=afk_keyboard_movement, name="afk_keyboard").start()
    if current_state == State.FIND_MATCH:
        find_match_sequence()
    if current_state == State.IN_QUEUE:
        logger.debug("in q")
    if current_state == State.LOADOUT_SELECTION:
        select_loadout()
    if current_state == State.AFK_KICK:
        handle_afk_kick() 
    if current_state == State.FIND_MATCH_ALT:
        fix_find_match()

def fix_find_match():
    tries = 0
    while tries < 10:
        x, y, c = try_find_poi("find_match_alt")
        if c > 0.8:
            logger.debug(f"Found find match alt button at {x} {y} with confidence of {c}")
            click(x, y - 180)
            # time.sleep(0.5)
            click(x, y - 180)
            break
        else:
            logger.warning("Failed to find exit_afk_button")
            tries += 1


def handle_afk_kick():
    logger.info("We got kicked :(")
    tries = 0
    while tries < 10:
        x, y, c = try_find_poi("exit_afk_kick")
        if c > 0.8:
            logger.debug(f"Found kick exit button at {x} {y} with confidence of {c}")
            click(x + 3, y + 3)
            break
        else:
            logger.warning("Failed to find exit_afk_button")
            tries += 1


def find_match_sequence():
    tries = 0
    logger.info("Starting menu sequence")
    while tries < 10:
        # logger.info("Starting menu sequence")
        x, y, c = try_find_poi("find_match")
        if c > 0.8:
            logger.debug(f"Found find_match at {x} {y}")
            click(x, y)
            time.sleep(2)
            x, y, c = try_find_poi("playlist")
            logger.debug(f"Found playlist at {x} {y}")
            click(x + 5, y + 5)
            break
        else:
            tries += 1
        

def select_loadout():
    tries = 0
    while tries < 10:
        x, y, c = try_find_poi("loadout")
        if c > 0.8:
            click(x + 10, y + 10)
            logger.debug(f"Found loadout at {x} {y}")
            break
        else:
            logger.warning(f"Failed to find loadout confidence level: {c}")
            tries += 1

def use_equipments():
    keys = [Q, Q, E]
    key = random.choice(keys)
    pressKey(key)
    time.sleep(0.5)
    releaseKey(key)

def special_movement():
    keys = [SPACE, C]
    key = random.choice(keys)
    pressKey(key)
    time.sleep(0.3)
    releaseKey(key)

def afk_keyboard_movement():
    logger.debug("Start keyboard movement")
    keys = [W, A, S, D]
    while current_state == State.IN_GAME:
        duration_sec = random.randint(5, 15)
        dice = random.randint(0, 10)
        use_equipments()
        if dice <= 6:
            special_movement()
        key = random.choice(keys)
        holdKey(key, duration_sec)
        time.sleep((duration_sec / 2 ) + 0.5)
    logger.debug("Ending keyboard movement")
    
    
def set_window_to_foreground():
    hwnd = win32gui.FindWindow(None, "Call of Duty®")
    assert hwnd != 0, "Failed to find call of poopy window"
    # win32gui.SetForegroundWindow(hwnd)

def set_state():
    global current_state
    while True:
        set_window_to_foreground()
        screenshot = capture_screenshot()
        for s in State:
            for v in s.value:
                x, y, confidence = try_find_poi(v, screenshot=screenshot)
                if confidence > 0.8:
                    if current_state != s:
                        current_state = s
                        handle_state_change()
                        logger.info(f"State changed: {s}")
        time.sleep(1)
    

if __name__ == "__main__":
    logger.info("Starting eval state thread")
    eval_state_thread = threading.Thread(target=set_state)
    eval_state_thread.start()
