try:
    from .fonts import sFONT
except:
    from fonts import sFONT
from math import floor

COLORED = 0
UNCOLORED = 1

# Display orientation
ROTATE_0 = 0
ROTATE_90 = 1
ROTATE_180 = 2
ROTATE_270 = 3

# Color inverse. 1 or 0 = set or reset a bit if set a colored pixel
IF_INVERT_COLOR = 1


def fixX(x, paint):
    if x < 0:
        return round((paint.GetHeight() if paint.GetRotate() in [ROTATE_90, ROTATE_270] else paint.GetWidth()) + x)
    return round(x)

def fixY(y, paint):
    if y < 0:
        return round((paint.GetWidth() if paint.GetRotate() in [ROTATE_90, ROTATE_270] else paint.GetHeight()) + y)
    return round(y)


class Paint:
    """
    Initialize a paint class
    
    :param list[int] image: Default image buffer. Can be empty
    :param int width: Width of paint screen (should be multiple of 8)
    :param int height: Height of paint screen
    """
    _image = []
    _width = 0
    _height = 0
    _rotate = ROTATE_0

    def __init__(self, image, width, height):
        self._image = image
        # 1 byte = 8 pixels, so the width should be the multiple of 8
        self._width = width + 8 - (width % 8) if width % 8 else width
        self._height = height
        for i in range(len(self._image), floor(self._width / 8) * self._height):
            self._image.append(255)

    def Clear(self, colored):
        """clear the image
        
        :param int colored: Should the pixels be colored or not
        """
        for x in range(self._width):
            for y in range(self._height):
                self.DrawAbsolutePixel(x, y, colored)

    def DrawAbsolutePixel(self, x, y, colored):
        """this draws a pixel by absolute coordinates.
        this function won't be affected by the rotate parameter.

        :param int x: X Location
        :param int y: Y Location
        :param int colored: Should the pixel be colored or not
        """
        if x < 0 or x >= self._width or y < 0 or y >= self._height: return
        location = floor((x + y * self._width) / 8)
    
        if IF_INVERT_COLOR:
            if colored:
                self._image[location] |= 0x80 >> (x % 8)
            else:
                self._image[location] &= ~(0x80 >> (x % 8))
        elif colored:
            self._image[location] &= ~(0x80 >> (x % 8))
        else:
            self._image[location] |= 0x80 >> (x % 8)

    # Getters and Setters
    def GetImage(self):
        """Get the image object

        :rtype: list[int]
        """
        return self._image

    def GetWidth(self):
        """Get the width

        :rtype: int
        """
        return self._width

    def SetWidth(self, width):
        """Set the width

        :param int width: New width value. Should be multiple of 8
        """
        self._width = width + 8 - (width % 8) if width % 8 else width

    def GetHeight(self):
        """Get the height

        :rtype: int
        """
        return self._height

    def SetHeight(self, height):
        """Set the height

        :param int height: New height value
        """
        self._height = height

    def GetRotate(self):
        """Get the rotation

        :rtype: int
        """
        return self._rotate

    def SetRotate(self, rotate):
        """Set the rotation

        :param int rotate: New rotate value
        """
        self._rotate = rotate

    def DrawPixel(self, x, y, colored):
        """this draws a pixel by the coordinates

        :param int x: X Location
        :param int y: Y Location
        :param int colored: Should the pixel be colored or not
        """
        if self._rotate == ROTATE_0:
            if x < 0 or x >= self._width or y < 0 or y >= self._height:
                return
        elif self._rotate == ROTATE_90:
            if x < 0 or x >= self._height or y < 0 or y >= self._width:
                return
            point_temp = x
            x = self._width - y - 1
            y = point_temp
        elif self._rotate == ROTATE_180:
            if x < 0 or x >= self._width or y < 0 or y >= self._height:
                return
            x = self._width - x - 1
            y = self._height - y - 1
        elif self._rotate == ROTATE_270:
            if x < 0 or x >= self._height or y < 0 or y >= self._width:
                return
            point_temp = x
            x = y
            y = self._height - point_temp - 1
        else:
            return
        self.DrawAbsolutePixel(x, y, colored)

    def DrawCharAt(self, x, y, ascii_char, font, colored):
        """this draws a charactor on the frame buffer but not refresh

        :param int x: X Location
        :param int y: Y Location
        :param chr ascii_char: ASCII char
        :param sFONT font: Font for the char
        :param int colored: Should the pixels be colored or not
        """
        char_offset = floor((ord(ascii_char) - ord(' ')) * font.Height * floor(font.Width / 8 + (1 if font.Width % 8 else 0)))
        ptr = font.table[char_offset]

        for j in range(font.Height):
            for i in range(font.Width):
                if ptr & (0x80 >> (i % 8)):
                    self.DrawPixel(x + i, y + j, colored)
                if i % 8 == 7:
                    char_offset += 1
                    ptr = font.table[char_offset]
            if font.Width % 8 != 0:
                char_offset += 1
                ptr = font.table[char_offset]

    def DrawStringAt(self, x, y, text, font, colored):
        """this displays a string on the frame buffer but not refresh

        :param int x: X Location
        :param int y: Y Location
        :param str text: The whole string
        :param sFONT font: Font for the text
        :param int colored: Should the pixels be colored or not
        """
        x = fixX(x, self)
        y = fixY(y, self)

        p_text = 0
        counter = 0
        refcolumn = x

        # Send the string character by character on EPD
        while p_text < len(text):
            # Display one character on EPD
            self.DrawCharAt(refcolumn, y, text[p_text], font, colored)
            # Decrement the column position by 16
            refcolumn += font.Width
            # Point on the next character
            p_text += 1
            counter += 1

    def DrawLine(self, x0, y0, x1, y1, colored):
        """this draws a line on the frame buffer

        :param int x0: Start X Location
        :param int y0: Start Y Location
        :param int x1: End X Location
        :param int y1: End Y Location
        :param int colored: Should the pixels be colored or not
        """
        # Bresenham algorithm
        dx = x1 - x0 if x1 - x0 >= 0 else x0 - x1
        sx = 1 if x0 < x1 else -1
        dy = y1 - y0 if y1 - y0 <= 0 else y0 - y1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while (x0 != x1) and (y0 != y1):
            self.DrawPixel(x0, y0, colored)
            if 2 * err >= dy:
                err += dy;
                x0 += sx;
            if 2 * err <= dx:
                err += dx;
                y0 += sy;

    def DrawHorizontalLine(self, x, y, line_width, colored):
        """this draws a horizontal line on the frame buffer

        :param int x: X Location
        :param int y: Y Location
        :param int line_width: Line width
        :param int colored: Should the pixels be colored or not
        """
        for i in range(x, round(x + line_width)):
            self.DrawPixel(i, y, colored)

    def DrawVerticalLine(self, x, y, line_height, colored):
        """this draws a vertical line on the frame buffer

        :param int x: X Location
        :param int y: Y Location
        :param int line_height: Line height
        :param int colored: Should the pixels be colored or not
        """
        for i in range(y, round(y + line_height)):
            self.DrawPixel(x, i, colored)
        
    def DrawRectangle(self, x0, y0, x1, y1, colored):
        """this draws a rectangle

        :param int x0: Start X Location
        :param int y0: Start Y Location
        :param int x1: End X Location
        :param int y1: End Y Location
        :param int colored: Should the pixels be colored or not
        """
        x0 = fixX(x0, self)
        x1 = fixX(x1, self)
        y0 = fixY(y0, self)
        y1 = fixY(y1, self)

        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0

        self.DrawHorizontalLine(min_x, min_y, max_x - min_x + 1, colored)
        self.DrawHorizontalLine(min_x, max_y, max_x - min_x + 1, colored)
        self.DrawVerticalLine(min_x, min_y, max_y - min_y + 1, colored)
        self.DrawVerticalLine(max_x, min_y, max_y - min_y + 1, colored)

    def DrawFilledRectangle(self, x0, y0, x1, y1, colored):
        """this draws a filled rectangle

        :param int x0: Start X Location
        :param int y0: Start Y Location
        :param int x1: End X Location
        :param int y1: End Y Location
        :param int colored: Should the pixels be colored or not
        """
        x0 = fixX(x0, self)
        x1 = fixX(x1, self)
        y0 = fixY(y0, self)
        y1 = fixY(y1, self)

        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0

        for i in range(min_x, max_x + 1): # <= max_x
            self.DrawVerticalLine(i, min_y, max_y - min_y + 1, colored)

    def DrawCircle(self, x, y, radius, colored):
        """this draws a circle

        :param int x: Middle X Location
        :param int y: Middle Y Location
        :param int radius: Radius of the circle
        :param int colored: Should the pixels be colored or not
        """
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        
        x = fixX(x, self)
        y = fixY(y, self)

        while x_pos <= 0:
            self.DrawPixel(x - x_pos, y + y_pos, colored)
            self.DrawPixel(x + x_pos, y + y_pos, colored)
            self.DrawPixel(x + x_pos, y - y_pos, colored)
            self.DrawPixel(x - x_pos, y - y_pos, colored)
            e2 = err
            if e2 <= y_pos:
                y_pos += 1
                err += y_pos * 2 + 1
                if -x_pos == y_pos and e2 <= x_pos:
                    e2 = 0
            if e2 > x_pos:
                x_pos += 1
                err += x_pos * 2 + 1

    def DrawFilledCircle(self, x, y, radius, colored):
        """this draws a filled circle

        :param int x: Middle X Location
        :param int y: Middle Y Location
        :param int radius: Radius of the circle
        :param int colored: Should the pixels be colored or not
        """
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        
        x = fixX(x, self)
        y = fixY(y, self)

        while x_pos <= 0:
            self.DrawPixel(x - x_pos, y + y_pos, colored)
            self.DrawPixel(x + x_pos, y + y_pos, colored)
            self.DrawPixel(x + x_pos, y - y_pos, colored)
            self.DrawPixel(x - x_pos, y - y_pos, colored)
            self.DrawHorizontalLine(x + x_pos, y + y_pos, 2 * (-x_pos) + 1, colored)
            self.DrawHorizontalLine(x + x_pos, y - y_pos, 2 * (-x_pos) + 1, colored)
            e2 = err
            if e2 <= y_pos:
                y_pos += 1
                err += y_pos * 2 + 1
                if -x_pos == y_pos and e2 <= x_pos:
                    e2 = 0
            if e2 > x_pos:
                x_pos += 1
                err += x_pos * 2 + 1

