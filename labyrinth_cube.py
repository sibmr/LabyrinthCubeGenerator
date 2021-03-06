from typing import List
from solid import *
from solid.utils import *
import numpy as np

from labyrinth_level import LabyrinthLevel


class LabyrinthCube:
    def __init__(self, levels: List[LabyrinthLevel], spacing: float):
        self.levels = levels
        self.spacing = spacing

    def getRoomCorner(self):
        raise NotImplementedError()

    def getRoomCenter(self, i, j, k) -> np.ndarray:
        levelCenter = self.levels[k].get3dRoomCenter(i, j)
        zOffset = [0, 0, k * self.spacing]
        return levelCenter + zOffset

    def addAllWindows(self):
        for level in self.levels:
            level.hasWindows = True

    def getCubeSolid(self) -> OpenSCADObject:
        solidCube = union()(
            [
                translate([0, 0, i * self.spacing])(self.levels[i].getSolidLevel())
                for i in range(len(self.levels))
            ]
        )

        return solidCube

    def getPathSolid(self, indexPath) -> OpenSCADObject:
        spatialPath = []
        for location in indexPath:
            levelSpatialLocation = self.levels[location[2]].get3dRoomCenter(
                *location[:2]
            )
            zOffset = [0, 0, location[2] * self.spacing]
            cubeSpatialLocation = levelSpatialLocation + zOffset
            spatialPath.append(np.array(cubeSpatialLocation))
        extrusion = color([1,0,0])(union())
        for i in range(1, len(spatialPath)):
            p1 = spatialPath[i - 1]
            p2 = spatialPath[i]
            p1p2 = p2 - p1
            diffdim = np.argmax(np.abs(p1p2))
            size = np.ones(3) * 2
            size[diffdim] = np.linalg.norm(p1p2)
            extrusion.add(translate((p1 + p2) / 2)(cube(size, center=True)))
        return extrusion

    def createScadFile(self, name):
        scad_render_to_file(self.getCubeSolid(), f"{name}.scad")


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
