import sys
import time
from direct.showbase.ShowBase import ShowBase
from panda3d.core import load_prc_file_data, NodePath, Point3, PointLight, Vec4, Vec3, Shader, Texture, LColor, ComputeNode, ShaderAttrib, PfmFile
from direct.task import Task
from direct.filter.CommonFilters import CommonFilters
# from direct.stdpy import threading2
import math
import random
import numpy as np


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
        self.size = 50  # most important variable for comp time, sets the ultimate 3D grid size
        self.grid_step_time = 0.01
        self.grid = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]

        self.init_grid()
        # RLE string converter version, needs a self.size of ~40 or more for 60P5H2V0 RLE string
        # self.init_grid_RLE_basis()
        self.create_geometry()

        self.check_tex = PfmFile()

        # create a 3D numpy array for the initial grid
        grid = np.array(self.grid, dtype=np.float32)

        # Create input and output textures
        self.input_texture = Texture("input")
        self.input_texture.setup_3d_texture(self.size, self.size, self.size, Texture.T_float, Texture.F_r32)
        self.input_texture.set_clear_color(LColor(0, 0, 0, 1))
        self.input_texture.clear_image()
        PTA_uchar = self.input_texture.modify_ram_image()
        pta_np = np.frombuffer(PTA_uchar, dtype=np.float32)
        np.copyto(pta_np, grid.ravel())

        self.output_texture = Texture("output")
        self.output_texture.setup_3d_texture(self.size, self.size, self.size, Texture.T_float, Texture.F_rgba32)
        self.output_texture.set_wrap_u(Texture.WM_clamp)
        self.output_texture.set_wrap_v(Texture.WM_clamp)
        self.output_texture.set_wrap_w(Texture.WM_clamp)
        self.output_texture.set_minfilter(Texture.FT_nearest)
        self.output_texture.set_magfilter(Texture.FT_nearest)

        # load the compute shader
        shader = Shader.load_compute(Shader.SL_GLSL, "conway_compute.glsl")
        self.compute_node_path = ComputeNode("compute")
        self.compute_node_path.add_dispatch(self.size, self.size, self.size)
        self.final_compute_shader = self.render.attach_new_node(self.compute_node_path)
        self.final_compute_shader.set_shader(shader)
        self.final_compute_shader.set_shader_input("size", self.size)
        self.final_compute_shader.set_shader_input("inputTexture", self.input_texture)
        self.final_compute_shader.set_shader_input("outputTexture", self.output_texture)

        self.task_mgr.add(self.update, "Update")
        self.task_mgr.add(self.circle_camera, "CircleCamera")
        self.accept("escape", sys.exit)

        plight_1 = PointLight('plight_1')
        plight_1.set_color(Vec4(Vec3(2), 1))
        plight_1_node = self.render.attach_new_node(plight_1)
        self.render.set_light(plight_1_node)
        plight_1_node.set_pos(self.size * 2, self.size * 2, 25)

        scene_filters = CommonFilters(base.win, base.cam)
        scene_filters.set_bloom(size='medium')
        scene_filters.set_exposure_adjust(1.1)
        scene_filters.set_gamma_adjust(1.1)
        scene_filters.set_blur_sharpen(0.7)

    def init_grid(self):
        probability_alive = 0.02  # adjust this value between 0 and 1 to change the probability of a cell being alive

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
        self.grid[self.size//2 + 1][self.size//2][self.size//2] = 0
        self.grid[self.size//2 - 1][self.size//2][self.size//2] = 1
        self.grid[self.size//2][self.size//2 + 1][self.size//2] = 1
        self.grid[self.size//2][self.size//2 - 1][self.size//2] = 1

    def rle_to_bin_list(self, rle_string):
        binary_list = []    
        rle_string = rle_string.replace("\n","")
        rows = rle_string.split('$')
      
        for row in rows:
            binary_row = []
            run_length = ''
            for char in row:
                if char.isdigit():
                    run_length += char
                else:
                    if run_length == '':
                        run_length = '1'
                    if char == 'o':
                        binary_row.extend([1]*int(run_length))
                    else:
                        binary_row.extend([0]*int(run_length))
                    run_length = ''

            binary_list.append(binary_row)

        return binary_list

    def init_grid_RLE_basis(self):
        # Start with an all-zero grid
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    self.grid[x][y][z] = 0

        # 60P5H2V0 spaceship representation
        rle_string = '''
    4bo23bo$3bobo21bobo$3bobo21bobo$b3ob2o19b2ob3o$o31bo$b3ob2o19b2ob3o$3b
ob2o19b2obo9$12bo7bo$10b2ob2o3b2ob2o$13b2o3b2o$15bobo$8bo4bobobobo4bo$
7b3o5bobo5b3o$7bo5bobobobo5bo$9bo2bo2bobo2bo2bo$9b2o3b2ob2o3b2o$7bo7bo
bo7bo$7bo6b2ob2o6bo!$'''
        spaceship_60P5H2V0_coordinates = self.rle_to_bin_list(rle_string)

        # Insert the spaceship at a specific point in the 2D slice of a 3D grid
        for i, row in enumerate(spaceship_60P5H2V0_coordinates):
            for j, cell in enumerate(row):
                self.grid[i][j][self.size//2] = cell

    def create_geometry(self):
        self.cube_model = self.loader.load_model("1m_cube.gltf")
        self.cube_model.set_scale(0.49)
        self.cube_model.set_name("CubeModel")

        self.instance_root = NodePath("InstanceRoot")
        self.instance_root.reparent_to(self.render)

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x][y][z]:
                        instance = self.instance_root.attach_new_node("Instance")
                        instance.set_pos(Point3(x, y, z))
                        self.cube_model.instance_to(instance)

    def update(self, task):
        # update the input texture with the new grid values
        new_grid = np.array(self.grid, dtype=np.float32)
        PTA_uchar = self.input_texture.modify_ram_image()
        pta_np = np.frombuffer(PTA_uchar, dtype=np.float32)
        np.copyto(pta_np, new_grid.ravel())

        # set the updated input texture as the shader input
        self.final_compute_shader.set_shader_input("inputTexture", self.input_texture)

        # run the compute shader to calculate the next grid
        compute_attrib = self.final_compute_shader.get_attrib(ShaderAttrib)
        base.graphicsEngine.dispatch_compute((self.size, self.size, self.size), compute_attrib, base.win.get_gsg())

        # extract texture data
        base.graphics_engine.extract_texture_data(self.output_texture, base.win.get_gsg())
        
        # verify texture
        # self.output_texture.store(self.check_tex)
        # self.check_tex.write('checktex.png')

        # create a numpy array from the output texture data
        output_data = memoryview(self.output_texture.get_ram_image_as('RGBA')).cast("B").cast("f")
        output_array = np.frombuffer(output_data, dtype=np.float32)
        output_array = output_array.reshape(self.size, self.size, self.size, 4)

        # update the geometry based on the new grid
        self.instance_root.remove_node()
        self.instance_root = NodePath("InstanceRoot")
        self.instance_root.reparent_to(self.render)

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if output_array[x, y, z, 0] > 0.5:
                        instance = self.instance_root.attach_new_node("Instance")
                        instance.set_pos(Point3(x, y, z))
                        self.cube_model.instance_to(instance)
                        self.grid[x][y][z] = 1
                    else:
                        self.grid[x][y][z] = 0

        task.delay_time = self.grid_step_time
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
        radius = self.size * 3
        angle = task.time * 10  # adjust the multiplier to control the speed of cam rotation
        x = radius * math.sin(math.radians(angle))
        y = radius * math.cos(math.radians(angle))
        z = self.size // 2

        center = Point3(self.size // 2, self.size // 2, self.size // 2)
        self.cam.set_pos(x, y, 15)
        self.cam.look_at(center)

        return task.cont


GameOfLife3D().run()
