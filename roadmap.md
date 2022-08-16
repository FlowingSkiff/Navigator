# Project Roadmap

## GUI API

## Pathfinding API

The pathfinding API should take in two arguments, a multiprocessing.Queue for updating the GUI, and a multiprocessing.Value(int) for exiting conditions. The queue should accept a cell ID and a color. The cell ID should be calculated in row major order, i.e. id = x * numy + y where x and y are zero indexed.

![equation](https://latex.codecogs.com/png.image?id=x\times%20num_y+y)

## INTEROP

Pathfinding algorithm will update the GUI by using the multiprocessing library. After the initial loading of the map, updates will be pushed into a multiprocessing.Queue which will periodically be checked for new items in the GUI updater. The GUI can kill the pathfinding algorithm by setting a shared multiprocessing.Value(int), where value=1 should exit and value=0 should continue. The GUI api will take a method, not an object, so if the algorithm requires state, it should be wrapped inside a run function.
