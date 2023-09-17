# 3D-Conway-Game-of-Life

## A game engine implementation of 3D Conway's Game of Life in Python with Panda3D.
- The grid update calculation is performed in a separate thread to get the visualization closer to realtime.
- You may set the grid size as large as you like, though values higher than about 25 may prove slow on desktop computers.
- By default, the game starts with a probabilistic grid. To use the deterministic starting grid, call self.init_grid_deterministic() instead of self.init_grid()

There is a (currently experimental) implementation of the program which uses a compute shader. This version of the 
program requires GLSL version 430 and for NumPy to be installed. You may find this program in the 
computer_shader_experimental folder. This version allows for the visualization of significantly more complex grids.
A geometry shader for rendering the cubes is planned, to hopefully remove the rendering bottleneck.

As of 09/17/23, RLE string inputs are supported via the self.rle_to_bin_list(rle_string) function. This provides your RLE code pattern
as a 2D slice for initializing the 3D grid. Ensure that your grid size (self.size) is larger than your minimum pattern bounds. 
The 60P5H2V0 spaceship representation string is provided by default.

## 3,632 cubes
![fccfa22595cf2227249e9537ef912505bcf9d99f](https://github.com/rayanalysis/3D-Conway-Game-of-Life/assets/3117958/953eb90d-4a5a-4810-bd36-abd4799963ef)

## 44,819 cubes
![64aa7dbc245aa4fcc787dd028c926739a6302f3b](https://github.com/rayanalysis/3D-Conway-Game-of-Life/assets/3117958/9c7eb826-f107-4e4e-a154-119cc2b0ddb9)

## 264,042 cubes
![c213732d8bd4c92d8a7635ad7d20484b13615b94](https://github.com/rayanalysis/3D-Conway-Game-of-Life/assets/3117958/5449fcdc-5cf3-4378-af2a-be9cbc81decd)

## Screenshot from compute_shader_experimental (3d_conway_compute_shader.py) showing the 60P5H2V0 spaceship representation initial configuration
![RLE_basis_09_17_23](https://github.com/rayanalysis/3D-Conway-Game-of-Life/assets/3117958/f2b0c604-ac1f-4984-9e65-32808a94e22d)
