import tkinter as tk
import tkinter.ttk as ttk
import multiprocessing as mp
from .itemcommunication import *


def newFile():
    pass


def openFile():
    pass


def compute_target(queue, should_exit):
    pass


class BuilderFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, algorithms, command=None):
        tk.Frame.__init__(self, parent)
        if command is None:
            command = self.grid_remove
        self.label_num_x = tk.Label(self, text="Number of X Cells: ")
        self.label_num_y = tk.Label(self, text="Number of Y Cells: ")
        self.num_x = tk.StringVar(value="0")
        self.num_y = tk.StringVar(value="0")
        vcmd = (self.register(self.__validate), '%S')
        self.entry_num_x = tk.Entry(
            self, textvariable=self.num_x, validatecommand=vcmd, validate="key")
        self.entry_num_y = tk.Entry(
            self, textvariable=self.num_y, validatecommand=vcmd, validate="key")
        self.algo = tk.StringVar()
        self.list_algos = ttk.Combobox(
            self, values=algorithms)
        self.button_accept = tk.Button(
            self, text="Submit", command=command)

        self.label_num_x.grid(column=0, row=0)
        self.entry_num_x.grid(column=1, row=0)
        self.label_num_y.grid(column=0, row=1)
        self.entry_num_y.grid(column=1, row=1)
        self.list_algos.grid(column=0, row=2, columnspan=2)
        self.button_accept.grid(column=0, row=3, columnspan=2)

    def get_state(self):
        return [int(self.num_x.get()), int(self.num_y.get()), self.list_algos.get()]

    def __validate(self, value_if_allowed: str):
        return value_if_allowed.isdigit() or value_if_allowed == ""


class GridCanvas(tk.Canvas):
    def __init__(self, parent, width, height, numx, numy):
        tk.Canvas.__init__(self, parent, width=width+2,
                           height=height+2, background='gray75')

        COL_SIZE = int(width / numx)
        ROW_SIZE = int(height / numy)
        COL_OFFSET = 2
        ROW_OFFSET = 2

        self.rect_ids = []

        for x in range(numx):
            for y in range(numy):
                id = self.create_rectangle(
                    (x * COL_SIZE) + COL_OFFSET,
                    (y * ROW_SIZE) + ROW_OFFSET,
                    ((x+1) * COL_SIZE) + COL_OFFSET,
                    ((y+1) * ROW_SIZE) + ROW_OFFSET,
                    fill='red')
                self.rect_ids.append(id)

    def __build_grid(self, x, y):
        pass

    def __update(self, id, color):
        pass


class Application():
    def __init__(self, width, height, numx, numy, algorithms=[]):
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
        self.builder = BuilderFrame(
            self.full_frame, algorithms, command=self.__start_button)
        self.builder.grid(column=0, row=0)

        self.config_content = None
        self.label_update = None
        self.canvas_grid = None

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
        with self.algo_should_exit.get_lock():
            self.algo_should_exit.value = 0
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

    def __toggle_algorithm(self, numx: int = 0, numy: int = 0, algorithm=None):
        if self.algo_process is None:
            if not (numx == 0 or numy == 0 or algorithm is None):
                self.__start_algorithm(numx, numy, algorithm)
        else:
            self.__kill_algorithm()

    def __update_canvas(self, item: GridItem):
        self.canvas.itemconfig(item.id, item.color)

    def __update(self):
        if self.algo_process is not None:
            with self.algo_should_exit.get_lock():
                if self.algo_should_exit.value == 1:
                    self.__kill_algorithm()
        while not self.data_queue.empty():
            self.__update_canvas(self.data_queue.get())
        self.root.after(100, self.__update)

    def __build_canvas(self, numx, numy, width=500, height=400):
        self.config_content = tk.Frame(
            self.full_frame, borderwidth=5)

        self.label_update = tk.Label(self.config_content, text="Updates = 0")
        self.updates = 0
        self.canvas_grid = GridCanvas(
            self.config_content, width, height, numx, numy)
        self.config_content.grid(row=1)
        self.label_update.grid(row=0)
        self.canvas_grid.grid(row=1)

    def __start_button(self):
        self.builder.grid_remove()
        x, y, algo = self.builder.get_state()
        self.__build_canvas(x, y)
        self.__toggle_algorithm(x, y, algo)


if __name__ == '__main__':
    with Application(width=500, height=400, numx=100, numy=100) as app:
        app.run()
