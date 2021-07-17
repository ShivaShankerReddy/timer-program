
import concurrent.futures
import logging
from threading import Event
import time
import sys, tty, os, termios



minute = 0
sec = 0
hour = 0
interrupted = False


def identify_key_strokes():
    # https://stackoverflow.com/questions/24072790/detect-key-press-in-python
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        key_mapping = {
            127: 'backspace',
            10: 'return',
            32: 'space',
            9: 'tab',
            27: 'esc',
            65: 'up',
            66: 'down',
            67: 'right',
            68: 'left'
        }
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3:
                k = ord(b[2])
            else:
                k = ord(b)
            return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def key_strokes():
    try:
        while True:
            k = identify_key_strokes()
            if k == 'esc':
                exit()
            else:
                return k
    except (KeyboardInterrupt, SystemExit):
        os.system('stty sane')
        print('stopping.')


def timer(event):
    global sec
    global minute
    global hour
    global interrupted

    try:
        logging.info("events is on:     {}".format(event.is_set()))
        event.wait()
        while event.is_set():
            if not interrupted:
                time.sleep(1)
                logging.info("time:  {} sec ".format(sec))
                if sec > 59:
                    if minute < 59:
                        minute += 1
                        sec = 0
                    if minute > 59:
                        minute = 0
                        sec = 0
                        hour += 1
                else:
                    sec += 1

    except KeyboardInterrupt:
        return


def main(event):
    global sec
    global minute
    global hour
    global interrupted
    while True:
        input_from_key = key_strokes()
        logging.info("input from key board:   {}".format(input_from_key))
        if input_from_key == 's':
            interrupted = False
            event.set()
            logging.info("timer stopped at: {0} hour {1} minute {2} sec".format(hour, minute, sec))
        elif input_from_key == 'c':
            interrupted = False
            event.set()
            logging.info("timer stopped at: {0} hour {1} minute {2} sec".format(hour, minute, sec))
        elif input_from_key == 'r':
            sec = 0
            interrupted = True
            logging.info("timer stopped at: {0} hour {1} minute {2} sec".format(hour, minute, sec))
        elif input_from_key == 'f':
            interrupted = True
            event.wait()
            logging.info("timer stopped at: {0} hour {1} minute {2} sec".format(hour, minute, sec))



if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    event = Event()
    logging.info("press s to start  c to continue  r to reset f to stop")
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(main, event)
            executor.submit(timer, event)
