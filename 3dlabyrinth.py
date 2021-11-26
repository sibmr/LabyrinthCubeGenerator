import numpy as np
from solid import *
import solid
from solid.utils import *

class ConnectionDirection():
    x_positive = 0
    y_positive = 1
    z_negative = 2

class LevelData():
    def __init__(self, wallThickness, pathThickness, isRoom, isConnected):
        self.wallThickness = wallThickness
        self.pathThickness = pathThickness
        self.isRoom = isRoom
        self.isConnected = isConnected

    @property
    def gridSize(self):
        return self.isRoom.shape[0]

    @property
    def roomSize(self):
        return self.wallThickness + self.pathThickness

    @property
    def levelSizeXY(self):
        return self.gridSize*self.roomSize + self.wallThickness

    @property
    def floorThickness(self):
        return self.wallThickness

    @property
    def levelSizeZ(self):
        return self.floorThickness + self.pathThickness

    @property
    def connectionSizeX(self):
        return np.array([self.wallThickness, self.pathThickness])

    @property
    def connectionSizeY(self):
        return np.array([self.pathThickness, self.wallThickness])

    def _getRoomCorner(self, i, j):
        return np.array([i*self.roomSize, j*self.roomSize])

    def getRoomCorner(self, i, j):
        if i < self.gridSize and j < self.gridSize:
            return self._getRoomCorner(i,j)
        else:
            return None

def createLevelBase(ld : LevelData):
    base =  linear_extrude(ld.levelSizeZ)(
                square(ld.levelSizeXY)
            )
    return base

def createLevelRooms(ld : LevelData):
    rooms = []
    for i in range(ld.gridSize):
        for j in range(ld.gridSize):
            rooms.append(
            translate([i*ld.roomSize, j*ld.roomSize])(
                square(np.ones(2)*ld.pathThickness, center=False) \
                if ld.isRoom[i,j] else square([0,0])
            ))

    solidRooms = translate([ld.wallThickness, ld.wallThickness,ld.floorThickness])(
        linear_extrude(ld.pathThickness)(
            rooms
        )
    )

    return solidRooms

def createRoomConnections(ld : LevelData):
    u = union()
    cd = ConnectionDirection
    for i in range(ld.gridSize):
        for j in range(ld.gridSize):
            
            curr_room_center = ld.getRoomCorner(i,j)

            if(ld.isConnected[i,j,cd.x_positive]):
                neighbor_room_corner = ld.getRoomCorner(i+1,j)
                if neighbor_room_corner is not None:
                    between = neighbor_room_corner - [ld.wallThickness, 0]
                    u.add(
                        translate([0,0,ld.floorThickness])(
                            linear_extrude(ld.pathThickness)(
                                translate(between)(
                                    square(size=ld.connectionSizeX)
                                )
                            )
                        )
                    )
            if(ld.isConnected[i,j,cd.y_positive]):
                neighbor_room_corner = ld.getRoomCorner(i,j+1)
                if neighbor_room_corner is not None:
                    between = neighbor_room_corner - [0, ld.wallThickness]
                    u.add(
                        translate([0,0,ld.floorThickness])(
                            linear_extrude(ld.pathThickness)(
                                translate(between)(
                                    square(size=ld.connectionSizeY)
                                )
                            )
                        )
                    )
            if(ld.isConnected[i,j,cd.z_negative]):
                u.add(
                    linear_extrude(ld.floorThickness)(
                        translate(curr_room_center)(
                            square(size=[ld.pathThickness, ld.pathThickness])
                        )
                    )
                )
    solidConnections = translate([ld.wallThickness, ld.wallThickness])(u)

    return solidConnections



def createLevel(levelData : LevelData):
    

    base = createLevelBase(levelData)
    rooms = createLevelRooms(levelData)
    connections = createRoomConnections(levelData)

    level = difference()([
        base,
        union()([
            rooms,
            connections
        ])
    ])

    return level

if __name__ == "__main__":

    isRoom = np.ones((4,4), dtype=bool)
    roomConnection = np.ones((4,4,3), dtype=bool)

    isRoom[0,0] = False
    roomConnection[1,1,1] = 0

    levelData = LevelData(2,8,isRoom,roomConnection)
    level = createLevel(levelData)

    scad_render_to_file(level, "auto3dlab.scad")
