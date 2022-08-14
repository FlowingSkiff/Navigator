import tkinter as tk
import multiprocessing as mp
from src.gui.itemcommunication import *


def newFile():
    pass


def openFile():
    pass


def compute_target(queue, should_exit):
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
            self.config_content, text="Start", command=self.__toggle_algorithm)
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

        self.algo_process = None
        self.data_queue = mp.Queue()
        self.algo_should_exit = mp.Value('i', 0)

    def __exit__(self, exc_type, exc_value, traceback):
        # process join / close
        if self.algo_process is not None:
            with self.algo_should_exit.get_lock():
                self.algo_should_exit.value = 1
            self.algo_process.join()

    def __enter__(self):
        return self

    def __start_algorithm(self):
        with self.should_exit.get_lock():
            self.should_exit.value = 0
        self.algo_process = mp.Process(target=compute_target, args=(
            self.data_queue, self.algo_should_exit))
        self.algo_process.start()

    def __kill_algorithm(self):
        with self.algo_should_exit.get_lock():
            self.algo_should_exit.value = 1
        self.algo_process.join()
        self.algo_process = None

    def run(self):
        self.root.after(100, self.__update)
        self.root.mainloop()

    def __toggle_algorithm(self):
        if self.algo_process is None:
            self.__start_algorithm()
        else:
            self.__kill_algorithm()

    def __update_canvas(self, item: GridItem):
        if item.id is not None:
            self.canvas.itemconfig(item.id, item.color)
        pass

    def __update(self):
        if self.algo_process is not None:
            with self.algo_should_exit.get_lock():
                if self.algo_should_exit.value == 1:
                    self.__kill_algorithm()
        while not self.data_queue.empty():
            self.__update_canvas(self.data_queue.get())
        self.root.after(100, self.__update)


if __name__ == '__main__':
    with Application(width=500, height=400, numx=100, numy=100) as app:
        app.run()
