FILE = "save.txt"


def get_save():
    try:
        save = open(FILE, "r")
    except FileNotFoundError:
        save = open(FILE, "w")
        save.write("1")
        save.close()
        save = open(FILE, "r")

    try:
        level = int(save.read())
        if level > 4:
            level = 4
    except BaseException:
        level = 1

    save.close()
    return level


def save(level):
    save = open(FILE, "w")
    save.write(str(level))
    save.close()
