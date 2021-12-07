import os
import numpy as np
from solid import *
from subprocess import run

from labyrinth_cube import LabyrinthCube


class LabyrinthMap:
    def __init__(self, lcube: LabyrinthCube):
        self.lcube: LabyrinthCube = lcube
        self.spacing = 10

    @property
    def dim_2d_size(self):
        gridSize = self.lcube.levels[0].gridSize
        dim_2d_size = int(np.sqrt(gridSize))
        return dim_2d_size

    @property
    def step_2d(self):
        levelSizeXY = self.lcube.levels[0].levelSizeXY
        step_2d = levelSizeXY + self.spacing
        return step_2d
    
    @property
    def overall_width(self):
        overall_width = self.dim_2d_size*self.step_2d-self.spacing
        return overall_width

    def get_solid_layout(self) -> OpenSCADObject:
        solid_levels = list(reversed([level.getSolidLevel() for level in self.lcube.levels]))
        
        layout = union()
        for i in range(self.dim_2d_size):
            for j in range(self.dim_2d_size):
                layout.add(
                    translate(i * np.array([self.step_2d, 0]) - j * np.array([0, self.step_2d]) + [0,(self.dim_2d_size-1)*self.step_2d])(
                        solid_levels[i + j * self.dim_2d_size]
                    )
                )
        return layout

    def render_png(self, path):
        layout = self.get_solid_layout()
        map_png_path = os.path.join(path, "map.png")
        map_scad_path = os.path.join(path, "map.scad")
        scad_render_to_file(layout, map_scad_path)
        width = 2000
        height = 2000
        
        xy_center = np.ones(2)*((self.overall_width)/self.dim_2d_size)
        cam_z = self.overall_width*2.5
        ex, ey, ez = np.array([*xy_center, cam_z], dtype=np.int)
        cx, cy, cz = np.array([*xy_center, 0], dtype=np.int)
        print(f"--camera=eye_{ex},{ey},{ez},center_{cx},{cy},{cz}",)
        run(
            [
                "openscad",
                "-o",
                map_png_path,
                "--render",
                #"--autocenter",
                #"--viewall",
                f"--imgsize={width},{height}",
                f"--camera={ex},{ey},{ez},{cx},{cy},{cz}",
                "--projection=orthogonal",
                #"--colorscheme=BeforeDawn",
                "--colorscheme=Nature",
                #"--colorscheme=DeepOcean",
                #"--colorscheme=Tomorrow",
                map_scad_path,
            ]
        )
