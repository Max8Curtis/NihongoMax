class Color:
    def __init__(self):
        pass

    def get_level_color(self, level):
        if level == "N1":
            return 'ade9ff'
        elif level == "N2":
            return 'adb0ff'
        elif level == "N3":
            return 'ffadf1'
        elif level == "N4":
            return 'ffcbad'
        elif level == "N5":
            return 'd0ffad'
        else:
            return False