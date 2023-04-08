# 3D-Conway-Game-of-Life
A game engine implementation of 3D Conway's Game of Life in Python with Panda3D.

The grid update calculation is performed in a separate thread to get the visualization closer to realtime.

You may set the grid size as large as you like, though values higher than about 25 may prove slow on desktop computers.

By default, the game starts with a probabilistic grid. To use the deterministic starting grid, call self.init_grid_deterministic() instead of self.init_grid()

There is a (currently experimental) implementation of the program which uses a compute shader. This version of the 
program requires GLSL version 430 and for NumPy to be installed. You may find this program in the 
computer_shader_experimental folder. This version allows for the visualization of significantly more complex grids.
A geometry shader for rendering the cubes is planned, to hopefully remove the rendering bottleneck.