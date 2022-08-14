import tkinter as tk


def newFile():
    pass


def openFile():
    pass


class Application():
    def __init__(self, width, height, numx, numy):
        self.root = tk.Tk()
        self.platform = self.root.tk.call('tk', 'windowingsystem')
        self.root.option_add('*tearOff', False)

        self.menubar = tk.Menu(self.root)

        self.menu_file = tk.Menu(self.menubar)
        self.menu_file.add_command(label="New", command=newFile)
        self.menu_file.add_command(label="Open", command=openFile)
        self.menu_file.add_command(
            label="Close", command=lambda: self.root.destroy())

        self.menu_edit = tk.Menu(self.menubar)

        self.menubar.add_cascade(menu=self.menu_file, label="File")
        self.menubar.add_cascade(menu=self.menu_edit, label="Edit")
        self.root['menu'] = self.menubar

        self.full_frame = tk.Frame(self.root)
        self.full_frame.grid(column=0, row=0)

        self.config_content = tk.Frame(
            self.full_frame, borderwidth=5)
        algos = ["None"]
        variable = tk.StringVar()
        variable.set(algos[0])
        self.dropdown_algo = tk.OptionMenu(
            self.config_content, variable, *algos)
        self.button_redesign = tk.Button(self.config_content, text="Redesign")
        self.button_start = tk.Button(
            self.config_content, text="Start", command=self.start_algorithm)
        self.label_update = tk.Label(self.config_content, text="Updates = 0")
        self.config_content.grid(column=0, row=0, columnspan=5)
        self.dropdown_algo.grid(column=0, row=0)
        self.button_redesign.grid(column=1, row=0)
        self.button_start.grid(column=2, row=0)
        self.label_update.grid(column=3, row=0)
        self.updates = 0

        self.canvas = tk.Canvas(
            self.full_frame, width=width+2, height=height+2, background='gray75')
        self.canvas.grid(column=0, row=1, columnspan=5, rowspan=5)

        COL_SIZE = int(width / numx)
        ROW_SIZE = int(height / numy)
        COL_OFFSET = 2
        ROW_OFFSET = 2

        self.rect_ids = []

        for x in range(numx):
            for y in range(numy):
                id = self.canvas.create_rectangle(
                    (x * COL_SIZE) + COL_OFFSET,
                    (y * ROW_SIZE) + ROW_OFFSET,
                    ((x+1) * COL_SIZE) + COL_OFFSET,
                    ((y+1) * ROW_SIZE) + ROW_OFFSET,
                    fill='red')
                self.rect_ids.append(id)

    def __exit__(self, exc_type, exc_value, traceback):
        # process join / close
        pass

    def __enter__(self):
        return self

    def update_grid(self, updates):
        self.updates = self.updates + 1
        self.label_update.config(text="Updates = {}".format(self.updates))
        for id, color in updates:
            self.canvas.itemconfigure(self.rect_ids[id], fill=color)

    def start_algorithm(self):
        # self.algo = Process(algo, args[self.root, numx, numy])
        # self.algo.start()
        # # algo with report update with -> app.update_grid(updates)
        pass

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    with Application(width=500, height=400, numx=100, numy=100) as app:
        app.run()
