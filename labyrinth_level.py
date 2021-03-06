from typing import Literal
import numpy as np
from solid import *
from solid.utils import *


class ConnectionDirection:
    x_positive = 0
    y_positive = 1
    z_negative = 2


class LabyrinthLevel:
    def __init__(
        self, wallThickness, pathThickness, isConnected, isRoom, hasWindows=False
    ):
        self.wallThickness = wallThickness
        self.pathThickness = pathThickness
        self.isConnected = isConnected
        self.isRoom = isRoom
        self.hasWindows = hasWindows
        self.eps = 0.00001

    @property
    def gridSize(self) -> int:
        return self.isRoom.shape[0]

    @property
    def roomSize(self) -> float:
        return self.wallThickness + self.pathThickness

    @property
    def levelSizeXY(self) -> float:
        # length of all rooms in a row and outer wall thickness
        return self.gridSize * self.roomSize + self.wallThickness

    @property
    def floorThickness(self) -> float:
        return self.wallThickness

    @property
    def levelSizeZ(self) -> float:
        return self.floorThickness + self.pathThickness

    @property
    def connectionSizeX(self) -> np.ndarray:
        return np.array([self.wallThickness + 2 * self.eps, self.pathThickness])

    @property
    def connectionSizeY(self) -> np.ndarray:
        return np.array([self.pathThickness, self.wallThickness + 2 * self.eps])

    def _getRoomCorner(self, i: int, j: int) -> np.ndarray:
        return np.array([i * self.roomSize, j * self.roomSize])

    def getRoomCorner(self, i: int, j: int) -> Optional[np.ndarray]:
        if i < self.gridSize and j < self.gridSize:
            return self._getRoomCorner(i, j)
        else:
            return None

    def get3DRoomCorner(self, i: int, j: int) -> Optional[np.ndarray]:
        if i < self.gridSize and j < self.gridSize:
            flatRoomCorner = np.array([*self._getRoomCorner(i, j), 0])
            spatialOffset = [
                self.wallThickness,
                self.wallThickness,
                self.floorThickness,
            ]
            return flatRoomCorner + spatialOffset
        else:
            return None

    def get3dRoomCenter(self, i: int, j: int) -> Optional[np.ndarray]:
        roomCorner = self.get3DRoomCorner(i, j)
        if roomCorner is not None:
            centerOffset = np.ones(3) * (self.pathThickness / 2)
            return roomCorner + centerOffset
        else:
            return None

    def createLevelBase(self) -> OpenSCADObject:
        base = linear_extrude(self.levelSizeZ)(square(self.levelSizeXY))
        return base

    def createLevelRooms(self) -> OpenSCADObject:
        rooms = []
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                rooms.append(
                    translate([i * self.roomSize, j * self.roomSize])(
                        square(np.ones(2) * self.pathThickness, center=False)
                        if self.isRoom[i, j]
                        else square([0, 0])
                    )
                )

        solidRooms = translate(
            [self.wallThickness, self.wallThickness, self.floorThickness]
        )(linear_extrude(self.pathThickness)(rooms))

        return solidRooms

    def getWindowSolid(
        self, i: int, j: int, dir: Literal["xp, xn, yp, yn"]
    ) -> OpenSCADObject:
        pathSize = self.pathThickness
        center = self.get3dRoomCenter(i, j)
        levelMaxXY = self.levelSizeXY
        if dir == "xn":
            outside = np.array([0, center[1], center[2]])
            distToOutside = np.linalg.norm(outside - center)
            size = [distToOutside, pathSize / 3, pathSize / 3]
            rotation = np.array([45, 0, 0])
        elif dir == "xp":
            outside = np.array([levelMaxXY, center[1], center[2]])
            distToOutside = np.linalg.norm(outside - center)
            size = [distToOutside, pathSize / 3, pathSize / 3]
            rotation = np.array([45, 0, 0])
        elif dir == "yn":
            outside = np.array([center[0], 0, center[2]])
            distToOutside = np.linalg.norm(outside - center)
            size = [pathSize / 3, distToOutside, pathSize / 3]
            rotation = np.array([0, 45, 0])
        elif dir == "yp":
            outside = np.array([center[0], levelMaxXY, center[2]])
            distToOutside = np.linalg.norm(outside - center)
            size = [pathSize / 3, distToOutside, pathSize / 3]
            rotation = np.array([0, 45, 0])

        wcube = translate((center + outside) / 2)(
            rotate(a=rotation)(cube(size, center=True))
        )
        return wcube

    def getAllWindows(self) -> OpenSCADObject:
        windows = []
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                if i == 0:
                    windows.append(self.getWindowSolid(i, j, "xn"))
                if j == 0:
                    windows.append(self.getWindowSolid(i, j, "yn"))
                if i == self.gridSize - 1:
                    windows.append(self.getWindowSolid(i, j, "xp"))
                if j == self.gridSize - 1:
                    windows.append(self.getWindowSolid(i, j, "yp"))
        return union()(windows)

    def getXYConnection(self, i, j, type: Literal["X", "Y"]) -> OpenSCADObject:
        if type == "X":
            neighbor_room_corner = self.getRoomCorner(i + 1, j)
            offset = [self.wallThickness + self.eps, 0]
            size = self.connectionSizeX
        elif type == "Y":
            neighbor_room_corner = self.getRoomCorner(i, j + 1)
            offset = [0, self.wallThickness + self.eps]
            size = self.connectionSizeY
        else:
            Exception(f"Unknown type {type}")

        if neighbor_room_corner is not None:
            between = neighbor_room_corner - offset
            return translate([0, 0, self.floorThickness])(
                linear_extrude(self.pathThickness)(
                    translate(between)(square(size=size))
                )
            )
        return OpenSCADObject("empty", {})

    def createRoomConnections(self) -> OpenSCADObject:
        u = union()
        cd = ConnectionDirection
        for i in range(self.gridSize):
            for j in range(self.gridSize):

                curr_room_center = self.getRoomCorner(i, j)

                if self.isConnected[i, j, cd.x_positive]:
                    u.add(self.getXYConnection(i, j, "X"))
                if self.isConnected[i, j, cd.y_positive]:
                    u.add(self.getXYConnection(i, j, "Y"))
                if self.isConnected[i, j, cd.z_negative]:
                    u.add(
                        linear_extrude(self.floorThickness)(
                            translate(curr_room_center)(
                                square(size=[self.pathThickness, self.pathThickness])
                            )
                        )
                    )
        solidConnections = translate([self.wallThickness, self.wallThickness])(u)

        return solidConnections

    def getSolidLevel(self) -> OpenSCADObject:

        base = self.createLevelBase()
        rooms = self.createLevelRooms()
        connections = self.createRoomConnections()

        windows = OpenSCADObject("empty", {})
        if self.hasWindows:
            windows = self.getAllWindows()

        level = difference()([base, union()([rooms, connections, windows])])

        return level

    def createScadFile(self, name):
        scad_render_to_file(self.getSolidLevel(), f"{name}.scad")


if __name__ == "__main__":

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

    scad_render_to_file(level, "auto3dlab.scad")
