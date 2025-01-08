from time import sleep, time
from math import floor
try:
    from pyfirmata import Board, util, STRING_DATA
except:
    try:
        from pyfirmata2 import Board, util, STRING_DATA
    except:
        print('You should install either pyfirmata or pyfirmata2!!')
MAX_DATA_BYTES, SERIAL_MESSAGE = 64, 0x60

class Epd: # E Paper Display
    _current_state = 0
    _last = False

    def __init__(self, board):
        """
        :arg board: Arduino Board
        :type board: Board
        """
        self._board = board
        self._board.add_cmd_handler(STRING_DATA, self._dataReceiver)
        
    def _dataReceiver(self, *data):
        try: msg = util.two_byte_iter_to_str(data)
        except: return
        if not msg.startswith('[epaperHandleMessage] '): return
        if self._last != False: print(time() - self._last, msg)
        else: print(msg)
        self._last = time()
        if msg == '[epaperHandleMessage] Done': self._current_state = 0

    def Reset(self):
        """Reset/Wakeup the ePaper-display. Actually runs Reset and Init on the display"""
        self._current_state = 1 # Sending...
        self._board.send_sysex(SERIAL_MESSAGE, [1]) # Reset
        self._current_state = 2 # Sended
        while self._current_state > 0: sleep(1)

    def DisplayFrame(self, black_image, red_image = None):
        """Send the image data to the ePaper-display to be shown

        :arg black_image: Black image data
        :type black_image: list[int]
        :arg red_image: Red image data (Optional)
        :type red_image: list[int]|None
        """
        self._current_state = 1 # Sending...

        self._board.send_sysex(SERIAL_MESSAGE, [4]) # Start black data
        size = floor((MAX_DATA_BYTES - 2) / 2 / 8) * 8 # 24 probably
        for b in range(0, len(black_image), size):
            msg = [6]
            for x in range(size):
                if b + x >= len(black_image): break
                msg.append(black_image[b + x] & 0x7F)
                msg.append((black_image[b + x] >> 7) & 0x7F)
            self._board.send_sysex(SERIAL_MESSAGE, msg) # DATA
        self._board.send_sysex(SERIAL_MESSAGE, [7]) # Stop data

        sleep(0.1)

        if red_image is not None:
            self._board.send_sysex(SERIAL_MESSAGE, [5]) # Start red data
            for b in range(0, len(red_image), size):
                msg = [6]
                for x in range(size):
                    if b + x >= len(red_image): break
                    msg.append(red_image[b + x] & 0x7F)
                    msg.append((red_image[b + x] >> 7) & 0x7F)
                self._board.send_sysex(SERIAL_MESSAGE, msg) # DATA
            self._board.send_sysex(SERIAL_MESSAGE, [7]) # Stop data

            sleep(0.1)

        self._board.send_sysex(SERIAL_MESSAGE, [8]) # End message data
        self._current_state = 2 # Sended
        while self._current_state > 0: sleep(1)

    def Clear(self):
        """Clear the ePaper-display screen"""
        self._current_state = 1 # Sending...
        self._board.send_sysex(SERIAL_MESSAGE, [2]) # Clear
        self._current_state = 2 # Sended
        while self._current_state > 0: sleep(1)

    def Sleep(self):
        """Put the ePaper-display into deep sleep"""
        self._current_state = 1 # Sending...
        self._board.send_sysex(SERIAL_MESSAGE, [3]) # Sleep
        self._current_state = 2 # Sended
        while self._current_state > 0: sleep(1)
