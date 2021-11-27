from typing import Literal
from solid import *
import solid
from solid.utils import *
import numpy as np

from labyrinth_cube import LabyrinthCube
from labyrinth_level import LabyrinthLevel


class LabyrinthCasing():

    def __init__(self, lcube: LabyrinthCube, casingThickness: float, tolerance: float):
        self.lc: LabyrinthCube = lcube
        self.casingThickness: float = casingThickness
        self.tolerance: float = tolerance

    @property
    def cubeOffset(self):
        cubeOffsetSize = np.ones(3)*(self.casingThickness+self.tolerance)
        return cubeOffsetSize

    @property
    def labyrinthCubeSize(self):
        cubeSizeXY = self.lc.levels[0].levelSizeXY
        cubeSizeZ = self.lc.spacing*len(self.lc.levels)
        cubeSize = np.array([cubeSizeXY, cubeSizeXY, cubeSizeZ])
        return cubeSize

    @property
    def casingSize(self):
        return [*2*self.cubeOffset[:2], self.cubeOffset[2]] + self.labyrinthCubeSize

    def getRoomCenter(self, i, j, k):
        return self.lc.getRoomCenter(i,j,k) + self.cubeOffset

    def getCasingSolid(self):

        assert self.casingThickness > 0, "Casing Thickness needs to be positive"

        # assuming all levels have same measurements as level 0
        
        holeOffsetSize = np.ones(3)*(self.casingThickness)

        outCube = cube(self.casingSize, center=False)
        holeCube = cube(self.labyrinthCubeSize+np.ones(3)*2*self.tolerance, center=False)

        solidCasing = difference()([
            outCube,
            translate(holeOffsetSize)(holeCube)
        ])
        return solidCasing

    def getWindowSolid(self, i : int, j: int, k: int, dir: Literal["xp, xn, yp, yn"]):
        pathSize = self.lc.levels[0].pathThickness
        center = self.getRoomCenter(i,j,k)
        if dir=="xn":
            outside = np.array([0,center[1],center[2]])
            distToOutside = np.linalg.norm(outside-center)
            size = [distToOutside,pathSize/3,pathSize/3]
        elif dir=="xp":
            outside = np.array([self.casingSize[0],center[1],center[2]])
            distToOutside = np.linalg.norm(outside-center)
            size = [distToOutside,pathSize/3,pathSize/3]
        elif dir=="yn":
            outside = np.array([center[0],0,center[2]])
            distToOutside = np.linalg.norm(outside-center)
            size = [pathSize/3,distToOutside,pathSize/3]
        elif dir=="yp":
            outside = np.array([center[0],self.casingSize[1],center[2]])
            distToOutside = np.linalg.norm(outside-center)
            size = [pathSize/3,distToOutside,pathSize/3]
        
        wcube = translate((center+outside)/2)(
            cube(size, center=True)
            )
        return wcube
        

    def getCubeInCasingSolid(self):
        casing = self.getCasingSolid()
        lcube = translate(np.ones(3)*(self.casingThickness+self.tolerance))(
            self.lc.getCubeSolid()
        )
        return casing + lcube

    def createScadFile(self, name):
        scad_render_to_file(self.getCasingSolid(), f"{name}.scad")

if __name__ == "__main__":
    ll = LabyrinthLevel(3, 13, np.ones(
        (4, 4, 3), dtype=bool), np.ones((4, 4), dtype=bool))
    lc = LabyrinthCube([ll, ll, ll, ll], 17)
    lcc = LabyrinthCasing(lc, 3, 0.5)

    scad_render_to_file(lcc.getCubeInCasingSolid(), "auto3dlab.scad")
