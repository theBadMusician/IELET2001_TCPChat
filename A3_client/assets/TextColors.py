# To use CLI colors your terminal has to support ANSI escape code.
# Most of terminals newer CMD interfaces support it like bash, Pycharm CLI etc.
# NOTE: standard MS-DOS terminal doesn't support ANSI colors, so it is only going to show escape characters.
class TextColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DEBUG = '\x1b[0;30;47m'
    ENDDEBUG = '\x1b[0m'