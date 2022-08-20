

class ColorTheme():
    def __init__(self, wall, empty, checked, active, best, background):
        self.wall = wall
        self.empty = empty
        self.checked = checked
        self.active = active
        self.best = best
        self.background = background


class Themes():
    def __init__(self):
        self.default = ColorTheme(wall="black", empty="honeydew",
                                  checked="gold1", active="agua", best="purple1", background="gray75")


if __name__ == "__main":
    pass
