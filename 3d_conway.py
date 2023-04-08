import sys
import time
from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file_data, Point3, PointLight, Vec4, Vec3
from direct.task import Task
from direct.filter.CommonFilters import CommonFilters
from direct.stdpy import threading2
import math
import random


class GameOfLife3D(ShowBase):
    def __init__(self):
        load_prc_file_data("", """
            win-size 1600 900
            window-title 3D Conway
            show-frame-rate-meter #t
            framebuffer-srgb #t
            framebuffer-multisample 1
            multisamples 4
            cursor-hidden #t
            fullscreen #f
        """)
        
        super().__init__()
        self.size = 20  # most important variable for comp time, sets the ultimate 3D grid size
        self.grid = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        self.new_grid = []
        self.grid_step_time = 0.01
        
        self.init_grid()
        # self.init_grid_deterministic()
        self.create_geometry()
        threading2._start_new_thread(self.compute_next_grid, ())

        self.task_mgr.add(self.update, "Update")
        self.task_mgr.add(self.circle_camera, "CircleCamera")
        self.accept("escape", sys.exit)

        plight_1 = PointLight('plight_1')
        plight_1.set_color(Vec4(Vec3(2),1))
        plight_1_node = self.render.attach_new_node(plight_1)
        self.render.set_light(plight_1_node)
        plight_1_node.set_pos(self.size*2,self.size*2,25)

        scene_filters = CommonFilters(base.win, base.cam)
        scene_filters.set_bloom(size='medium')
        scene_filters.set_exposure_adjust(1.1)
        scene_filters.set_gamma_adjust(1.1)
        scene_filters.set_blur_sharpen(0.7)
        

    def init_grid(self):
        probability_alive = 0.05  # adjust this value between 0 and 1 to change the probability of a cell being alive

        # initialize the grid with given probabilities
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    self.grid[x][y][z] = 1 if random.random() < probability_alive else 0

        # set positions with less than two neighbors to zero
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x][y][z] == 1 and self.count_neighbors(x, y, z) <= 1:
                        self.grid[x][y][z] = 0

    def init_grid_deterministic(self):
        # add an "initial state" to the grid to prevent nondeterministic starts
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    self.grid[x][y][z] = 0

        self.grid[self.size//2][self.size//2][self.size//2] = 1
        self.grid[self.size//2 + 1][self.size//2][self.size//2] = 1
        self.grid[self.size//2 - 1][self.size//2][self.size//2] = 1
        self.grid[self.size//2][self.size//2 + 1][self.size//2] = 1
        self.grid[self.size//2][self.size//2 - 1][self.size//2] = 1
    
    def create_geometry(self):
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    cube = self.loader.load_model("1m_cube.gltf")
                    cube.flatten_strong()
                    cube.set_scale(0.49)
                    cube.set_pos(Point3(x, y, z))
                    cube.set_name(f"Cube-{x}-{y}-{z}")
                    cube.reparent_to(self.render)
                    if not self.grid[x][y][z]:
                        cube.hide()

    def compute_next_grid(self):
        while True:
            new_grid = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
            for x in range(self.size):
                for y in range(self.size):
                    for z in range(self.size):
                        neighbors = self.count_neighbors(x, y, z)
                        if self.grid[x][y][z]:
                            if 2 <= neighbors <= 3:
                                new_grid[x][y][z] = 1
                            else:
                                new_grid[x][y][z] = 0
                        else:
                            if neighbors == 3:
                                new_grid[x][y][z] = 1
                            else:
                                new_grid[x][y][z] = 0

                        cube = self.render.find(f"Cube-{x}-{y}-{z}")
                        if new_grid[x][y][z]:
                            cube.show()
                        else:
                            cube.hide()
            time.sleep(self.grid_step_time)
            self.new_grid = new_grid

    def update(self, task):
        if len(self.new_grid) > 0:
            self.grid = self.new_grid

        task.delay_time = self.grid_step_time*2  # set the update to double the grid calculation time
        return task.again

    def count_neighbors(self, x, y, z):
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    nx, ny, nz = (x + dx) % self.size, (y + dy) % self.size, (z + dz) % self.size
                    count += self.grid[nx][ny][nz]
        return count

    def circle_camera(self, task):
        radius = self.size*3
        angle = task.time * 10  # adjust the multiplier to control the speed of cam rotation
        x = radius * math.sin(math.radians(angle))
        y = radius * math.cos(math.radians(angle))
        z = self.size // 2

        center = Point3(self.size // 2, self.size // 2, self.size // 2)
        self.cam.set_pos(x, y, 15)
        self.cam.look_at(center)

        return task.cont


GameOfLife3D().run()
