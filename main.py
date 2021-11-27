from solid.solidpython import scad_render_to_file
from labyrinth_casing import LabyrinthCasing
from labyrinth_graph import LabyrinthGraph
from subprocess import run

def exportStl(name: str):
    run(["openscad", "-o", f"{name}.stl", f"{name}.scad"])

if __name__ == "__main__":
    lgraph = LabyrinthGraph(4)
    lgraph.setRandomTree(6)
    lcube = lgraph.getLabyrinthCube(2, 14, 17)
    lcase = LabyrinthCasing(lcube, 2, 0.3)
    path = lgraph.findPath(lgraph.topCornerNode, lgraph.bottomCornerNode)

    name = "casing1"
    lcase.createScadFile(name)
    exportStl(name)
    for i, level in enumerate(lcube.levels):
        name = f"level{i}"
        level.createScadFile(name)
        exportStl(name)


    scad_render_to_file(lcase.getCubeInCasingSolid(), "auto3dlab.scad")
    #scad_render_to_file(lcube.getCubeSolid()+lcube.getPathSolid(path), "auto3dlab.scad")
