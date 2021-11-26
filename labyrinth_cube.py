from typing import List
from solid import *
from solid.utils import *

from labyrinth_level import LabyrinthLevel


class LabyrinthCube():

    def __init__(self, levels: List[LabyrinthLevel], spacing: float):
        self.levels = levels
        self.spacing = spacing

    def getCubeSolid(self):
        solidCube = union()(
            [translate([0, 0, i*self.spacing])(self.levels[i].getSolidLevel())
                for i in range(len(self.levels))]
        )

        return solidCube


if __name__ == "__main__":

    import numpy as np

    isRoom = np.ones((4, 4), dtype=bool)
    roomConnection = np.zeros((4, 4, 3), dtype=bool)

    isRoom[0, 0] = False
    roomConnection[1, 1, 1] = True
    roomConnection[2, 1, 0] = True
    roomConnection[2, 2, 2] = True

    roomConnection[0, 1, 1] = True
    roomConnection[0, 2, 1] = True
    roomConnection[1, 0, 0] = True
    roomConnection[2, 0, 0] = True

    levelData = LabyrinthLevel(2, 8, roomConnection, isRoom)
    level = levelData.getSolidLevel()

    lcube = LabyrinthCube([levelData, levelData, levelData, levelData], 20)

    scad_render_to_file(lcube.getCubeSolid(), "auto3dlab.scad")
