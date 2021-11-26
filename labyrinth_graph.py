from typing import List
import numpy as np
from numpy.core.fromnumeric import _prod_dispatcher
from solid import scad_render_to_file
from numpy.random import default_rng

from labyrinth_level import LabyrinthLevel
from labyrinth_cube import LabyrinthCube

class LGraphNode():

    def __init__(self, location, connections):
        self.location: np.ndarray = np.array(location, dtype=int)
        self._connections: np.ndarray = connections

    def __eq__(self, other) -> bool:
        if(type(other) is LGraphNode):
            return np.all(self.location == other.location)
        else:
            raise TypeError(
                f"Other has type {type(other)}, only LGraphNode is supported")

    @property
    def isValid(self):
        overLowerBound = np.all(self.location >= np.zeros(3))
        underUpperBound = np.all(self.location < self._connections.shape[:3])
        return overLowerBound and underUpperBound

    @property
    def closeNodes(self) -> List["LGraphNode"]:
        nodes = []
        for i in range(6):
            offset = np.zeros(3)
            offset[i%3] = 1 if i<3 else -1
            closeNode = LGraphNode(self.location + offset, self._connections)
            if(closeNode.isValid):
                nodes.append(closeNode)
        return nodes

    @property
    def linkedNeighbors(self) -> List["LGraphNode"]:
        neighbors = []
        for i, isNeighbor in enumerate(self._connections[tuple(self.location.astype(int))]):
            if isNeighbor:
                offset = np.zeros(3)
                # connections on each level are in negative z direction
                offset[i] = -1 if i == 2 else 1
                neighborLocation = self.location + offset
                neighbors.append(LGraphNode(
                    neighborLocation, self._connections))
        return neighbors

    @property
    def neighbors(self) -> List["LGraphNode"]:
        neighbors = self.linkedNeighbors
        for i in range(3):
            offset = np.zeros(3)
            # connections on each level are in negative z direction (this is reversed)
            offset[i] = -1 if i == 2 else 1
            neighborLocation = self.location - offset
            neighbor = LGraphNode(neighborLocation, self._connections)
            if(neighbor.isValid and self in neighbor.linkedNeighbors):
                neighbors.append(neighbor)
        return neighbors


class LabyrinthGraph():

    def __init__(self, cubeSize: int):
        self.connections = np.zeros(
            (cubeSize, cubeSize, cubeSize, 3), dtype=bool)

    def getNode(self, location: np.ndarray):
        return LGraphNode(location, self.connections)

    @property
    def topCornerNode(self) -> LGraphNode:
        return self.getNode([0, 0, self.connections.shape[2]-1])

    @property
    def bottomCornerNode(self) -> LGraphNode:
        return self.getNode([*self.connections.shape[:2]-np.ones(2), 0])

    def getLabyrinthCube(self, wallThickness, pathThickness, spacing):
        levels = []
        for k in range(self.connections.shape[2]):              #z

            isRoom = np.zeros(self.connections.shape[:2])
            
            for i in range(self.connections.shape[0]):          #x
                for j in range(self.connections.shape[1]):      #y
                    isRoom[i,j] = len(self.getNode(np.array([i,j,k])).neighbors) > 0
            
            level = LabyrinthLevel( wallThickness, pathThickness,
                                    self.connections[:,:,k,:], isRoom)

            levels.append(level)
        return LabyrinthCube(levels, spacing)

    def addEdge(self, node1 : LGraphNode, node2 : LGraphNode):
        diff = node2.location-node1.location
        abssum = np.sum(np.abs(diff))
        if(abssum == 1):
            if  (diff[0] == 1):
                self.connections[tuple([*node1.location, 0])] = True
            elif(diff[0] == -1):
                self.connections[tuple([*node2.location, 0])] = True
            elif(diff[1] == 1):
                self.connections[tuple([*node1.location, 1])] = True
            elif(diff[1] == -1):
                self.connections[tuple([*node2.location, 1])] = True
            elif(diff[2] == 1):
                self.connections[tuple([*node2.location, 2])] = True
            elif(diff[2] == -1):
                self.connections[tuple([*node1.location, 2])] = True
            return True
        else:
            return False            


    def setRandomTree(self, seed):
        rs = np.random.RandomState(seed=seed)
        visited = np.zeros(self.connections.shape[:3], dtype=bool)
        startNode = self.topCornerNode
        stack = [startNode]
        while stack:
            currentNode = stack.pop()
            print(currentNode.location)
            adjNodes = np.array(currentNode.closeNodes)
            perm = rs.permutation(len(adjNodes))
            print(perm)
            permAdjNodes = adjNodes[perm]
            for node in permAdjNodes:
                if not visited[tuple(node.location)]:
                    self.addEdge(currentNode, node)
                    visited[tuple(node.location)] = True
                    stack.append(node)


if __name__ == "__main__":

    from copy import deepcopy

    def testAddEdge():
        print("test add edge")
        lgraph = LabyrinthGraph(4)
        node = lgraph.getNode([1,1,1])
        above = lgraph.getNode([1,1,2])
        below = lgraph.getNode([1,1,0])
        xp = lgraph.getNode([2,1,1])
        xn = lgraph.getNode([0,1,1])
        yp = lgraph.getNode([1,2,1])
        yn = lgraph.getNode([1,0,1])
        
        to_test = [above, below, xp, xn, yp, yn]
        for testNode in to_test:
            lgraph.connections[:] = np.zeros(
            (4, 4, 4, 3), dtype=bool)
            success = lgraph.addEdge(testNode, node)
            if not success: print("failed")
            if not testNode.isValid: print("node not valid")
            print(node in testNode.neighbors)
            print(testNode in node.neighbors)

    def testGetNeighbors():
        print("test get neighbors")
        lgraph = LabyrinthGraph(4)
        lgraph.connections[1,1,1,0] = True
        lgraph.connections[1,1,2,2] = True
        lgraph.connections[1,0,1,1] = True
        print(lgraph.getNode([1,1,1]).neighbors)

    def testCreateCube():
        lgraph = LabyrinthGraph(6)
        lgraph.setRandomTree(102030123)
        print("done")
        lcube = lgraph.getLabyrinthCube(2,8,20)
        print("done")
        scad_render_to_file(lcube.getCubeSolid(), "auto3dlab.scad")

    testAddEdge()
    testGetNeighbors()
    testCreateCube()

    