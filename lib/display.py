# Date: 06/04/2019
# Author: Mohamed
# Description: Display

import os
import typing
import platform
from colorama import init
import lib.const as const

init(autoreset=True)


class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BOLD = '\033[1m'
    RESET = '\033[0m'


class Display:

    def __init__(self) -> None:

        # consts
        # self.colors = {
        #     'red': Colors.RED,
        #     'yellow': Colors.YELLOW,
        #     'green': Colors.GREEN,
        #     'blue': Colors.BLUE,
        #     'cyan': Colors.CYAN,
        #     'white': Colors.WHITE,
        #     'black': Colors.BLACK,
        #     'reset': Colors.RESET
        # }

        self.colors = {
            'red': '',
            'yellow': '',
            'green': '',
            'blue': '',
            'cyan': '',
            'white': '',
            'black': '',
            'reset': ''
        }

        self.labels = {
            'warning': {'color': self.colors['yellow'], 'symbol': '!'},
            'info': {'color': self.colors['cyan'], 'symbol': '-'},
            'success': {'color': self.colors['green'], 'symbol': '+'},
            'danger': {'color': self.colors['red'], 'symbol': '*'},
            'primary': {'color': self.colors['blue'], 'symbol': '-'}
        }

        self.cls_cmd = 'cls' if platform.system() == 'Windows' else 'clear'

    def clear(self):
        os.system(self.cls_cmd)

    def _display(self,
                 color: str, symbol: str,
                 tag: str, divider: str, msg: str, newline_left: bool = False, newline_right: bool = False) -> None:
        '''Display to the screen.
        '''

        # msg = '{0}[{1}{2}{0}] {1}{3}{4}{5} {6}{7}'.format(
        #     self.colors['yellow'],
        #     color,
        #     symbol,
        #     tag,
        #     self.colors['white'],
        #     divider,
        #     msg,
        #     self.colors['reset']
        # )

        msg = '[{0}] {1}{2} {3}'.format(
            symbol, tag, divider, msg
        )

        if newline_left:
            msg = '\n{}'.format(msg)

        if newline_right:
            msg = '{}\n'.format(msg)

        print(msg)

    def warning(self, tag: str, div: str, msg: str, newline_left: bool = False, newline_right: bool = False) -> None:
        '''Display warning message.
        '''

        self._display(
            self.labels['warning']['color'],
            self.labels['warning']['symbol'],
            tag,
            div,
            msg,
            newline_left,
            newline_right
        )

    def info(self, tag: str, div: str, msg: str, newline_left: bool = False, newline_right: bool = False) -> None:
        '''Display informative message.
        '''

        self._display(
            self.labels['info']['color'],
            self.labels['info']['symbol'],
            tag,
            div,
            msg,
            newline_left,
            newline_right
        )

    def prompt(self, prompt) -> None:
        '''Prompt the user.
        '''

        msg = '{0}[{1}-{0}]{1} {1}{2}{3}: {4}'.format(
            self.colors['yellow'],
            self.colors['cyan'],
            prompt,
            self.colors['white'],
            Colors.RESET
        )

        print(msg, end='')

    def success(self, tag: str, div: str, msg: str, newline_left: bool = False, newline_right: bool = False) -> None:
        '''Display successful message.
        '''

        self._display(
            self.labels['success']['color'],
            self.labels['success']['symbol'],
            tag,
            div,
            msg,
            newline_left,
            newline_right
        )

    def danger(self, tag: str, div: str, msg: str, newline_left: bool = False, newline_right: bool = False) -> None:
        '''Display danger message.
        '''

        self._display(
            self.labels['danger']['color'],
            self.labels['danger']['symbol'],
            tag,
            div,
            msg,
            newline_left,
            newline_right
        )

    def primary(self, username: str, attempts: int, browsers: int, progress: float) -> None:
        '''Display primary message.
        '''

        msg = '{0}[{1}-{0}]{1} Username{2}: {3}  {4}::{5}  {1}Attempts{2}: {6:02d}  {4}::{5}  {1}Browsers{2}: {7:02d}  {4}::{5}  {1}Progress{2}: {8:0.2f}% {5}'.format(
            self.colors['yellow'],
            self.colors['blue'],
            self.colors['white'],
            username,
            self.colors['cyan'],
            Colors.RESET,
            attempts,
            browsers,
            progress,
        )

        print(msg, end='\r')

    def password_found(self, password: str) -> None:
        '''Display password.
        '''

        msg = '\n{0}[{1}+{0}]{1} Password{2}: {3}{4}{5}\n'.format(
            self.colors['yellow'],
            self.colors['green'],
            self.colors['white'],
            Colors.BOLD,
            password,
            Colors.RESET,
        )

        print(msg)

    def basic_info(self) -> None:
        '''Display basic info.'''

        msg = '{0}[{1}+{0}]{1} Author{2}: {3}{4} -{5} {1}Version{2}: {3}{6}{5}'.format(
            self.colors['yellow'],
            self.colors['green'],
            self.colors['white'],
            Colors.BOLD,
            const.AUTHOR,
            Colors.RESET,
            const.VERSION
        )

        print(msg, end='\n')
