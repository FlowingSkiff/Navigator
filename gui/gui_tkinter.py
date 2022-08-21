import tkinter as tk
import tkinter.ttk as ttk
import multiprocessing as mp
from typing import List
from utils import *


def newFile() -> None:
    pass


def openFile() -> None:
    pass


class BuilderFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, algorithms, command=None):
        tk.Frame.__init__(self, parent)
        if command is None:
            command = self.grid_remove
        self.label_num_x = tk.Label(self, text="Number of X Cells: ")
        self.label_num_y = tk.Label(self, text="Number of Y Cells: ")
        self.num_x = tk.StringVar(value="100")
        self.num_y = tk.StringVar(value="100")
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

    def get_state(self) -> list:
        return [int(self.num_x.get()), int(self.num_y.get()), self.list_algos.get()]

    def __validate(self, value_if_allowed: str) -> bool:
        return value_if_allowed.isdigit() or value_if_allowed == ""


class GridCanvas(tk.Canvas):
    def __init__(self, parent, width, height, numx, numy, theme=Themes().default, **kwargs):
        tk.Canvas.__init__(self, parent, width=width,
                           height=height, background=theme.background, **kwargs)
        self.config(highlightthickness=0)
        self.bind("<Configure>", self.__on_resize)
        self.bind("<Button-1>", self.__on_grid_item_click)
        self.theme = theme
        self.rect_ids = []
        self.width = width
        self.height = height
        self.__build_grid(numx, numy)

    def __on_resize(self, event) -> None:
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        self.scale("all", 0, 0, wscale, hscale)

    def __build_grid(self, numx, numy) -> None:
        COL_SIZE = int(self.width / numx)
        ROW_SIZE = int(self.height / numy)
        self.width = COL_SIZE * numx
        self.height = ROW_SIZE * numy
        self.config(width=self.width, height=self.height)
        if COL_SIZE == 0 or ROW_SIZE == 0:
            raise ValueError(
                "COL_SIZE or ROW_SIZE is too large for grid dimensions.")
        for x in range(numx):
            for y in range(numy):
                id = self.create_rectangle(
                    (x * COL_SIZE),
                    (y * ROW_SIZE),
                    ((x+1) * COL_SIZE),
                    ((y+1) * ROW_SIZE),
                    fill=self.theme.empty,
                    tags=("empty"))
                self.rect_ids.append(id)

    def __on_grid_item_click(self, event) -> None:
        item = self.find_closest(event.x, event.y)
        if "empty" in self.gettags(item):
            self.itemconfig(item, fill=self.theme.wall, tags=("wall",))
        elif "wall" in self.gettags(item):
            self.itemconfig(item, fill=self.theme.empty, tags=("empty",))
        else:
            print("Error in toggle")

    def get_walls(self) -> List[int]:
        list = []
        for item in self.find_withtag("wall"):
            list.append(int(item))
        return list

    def update_item(self, id, color) -> None:
        self.itemconfig(id, fill=color)


class Application():
    def __init__(self, numx, numy, algorithms=[]):
        self.root = tk.Tk()
        self.platform = self.root.tk.call('tk', 'windowingsystem')
        self.root.option_add('*tearOff', False)
        self.themes = Themes()
        self.activetheme = self.themes.default
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
        self.full_frame.grid_propagate(True)
        self.full_frame.grid(column=0, row=0)
        self.builder = BuilderFrame(
            self.full_frame, algorithms, command=self.__on_build_button)
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

    def __start_algorithm(self, numx, numy, algorithm) -> None:
        with self.algo_should_exit.get_lock():
            self.algo_should_exit.value = 0
        self.algo_process = mp.Process(target=algorithm, args=(numx, numy,
                                                               self.data_queue, self.algo_should_exit))
        self.algo_process.start()

    def __kill_algorithm(self) -> None:
        with self.algo_should_exit.get_lock():
            self.algo_should_exit.value = 1
        self.algo_process.join()
        self.algo_process = None

    def run(self) -> None:
        self.root.after(100, self.__update)
        self.root.mainloop()

    def __toggle_algorithm(self, numx: int = 0, numy: int = 0, algorithm=None) -> None:
        if self.algo_process is None:
            if not (numx == 0 or numy == 0 or algorithm is None):
                self.__start_algorithm(numx, numy, algorithm)
        else:
            self.__kill_algorithm()

    def __update_canvas(self, id, color) -> None:
        self.canvas_grid.update_item(id, color)

    def __update(self) -> None:
        if self.algo_process is not None:
            with self.algo_should_exit.get_lock():
                if self.algo_should_exit.value == 1:
                    self.__kill_algorithm()
        while not self.data_queue.empty():
            id, color = self.data_queue.get()
            self.__update_canvas(id, color)
        self.root.after(ms=100, func=self.__update)

    def __build_canvas(self, numx, numy, width=500, height=400) -> None:
        self.config_content = tk.Frame(
            self.full_frame, borderwidth=5)
        self.config_content.grid(column=0, row=0)
        self.button_start = tk.Button(
            self.config_content, text="Start", command=self.__on_start_button)
        self.label_update = tk.Label(self.config_content, text="Updates = 0")
        self.updates = 0
        self.canvas_grid = GridCanvas(
            self.config_content, width, height, numx, numy)
        self.label_update.grid(column=0, row=0)
        self.button_start.grid(column=1, row=0)
        self.canvas_grid.grid(row=1, columnspan=2)
        self.config_content.grid_propagate(True)

    def __on_build_button(self) -> None:
        self.builder.grid_remove()
        x, y, algo = self.builder.get_state()
        self.__build_canvas(x, y)

    def __on_start_button(self) -> None:
        x, y, algo = self.builder.get_state()
        walls = self.canvas_grid.get_walls()
        # self.__toggle_algorithm(x, y, algo, walls)


if __name__ == '__main__':
    with Application(width=500, height=400, numx=100, numy=100) as app:
        app.run()
