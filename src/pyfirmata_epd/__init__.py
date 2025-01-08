"""pyFirmata ePaper Display library

This module allows you to control what's on the ePaper display

Supports both pyfirmata and pyfirmata2 libraries!
"""

__all__ = ['epd', 'epdpaint', 'fonts']
__version__ = '0.0.1'
__author__ = 'Miniontoby'

from .epd import *
from .epdpaint import *
from .fonts import *
