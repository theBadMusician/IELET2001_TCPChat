from .TextColors import TextColors

def DEBUG_PRINT(printText):
    print(TextColors.DEBUG + str(printText) + TextColors.ENDDEBUG)


def OKGREEN_PRINT(printText):
    print(TextColors.OKGREEN + str(printText) + TextColors.ENDC)


def OKBLUE_PRINT(printText):
    print(TextColors.OKBLUE + str(printText) + TextColors.ENDC)


def FAIL_PRINT(printText):
    print(TextColors.FAIL + str(printText) + TextColors.ENDC)


def WARNING_PRINT(printText):
    print(TextColors.WARNING + str(printText) + TextColors.ENDC)


def BOLD_PRINT(printText):
    print(TextColors.BOLD + str(printText) + TextColors.ENDC)

def UNDERLINE_PRINT(printText):
    print(TextColors.UNDERLINE + str(printText) + TextColors.ENDC)
