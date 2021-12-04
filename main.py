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
    lcube.addAllWindows()
    lcase = LabyrinthCasing(lcube, 1.2, 0.6)
    path = lgraph.findPath(lgraph.topCornerNode, lgraph.bottomCornerNode)

    name = "output/casing1"
    lcase.createScadFile(name)
    exportStl(name)
    for i, level in enumerate(lcube.levels):
        name = f"output/level{i}"
        level.createScadFile(name)
        exportStl(name)


    #scad_render_to_file(lcase.getCubeInCasingSolid(), "output/auto3dlab.scad")
    scad_render_to_file(lcube.getCubeSolid()+lcube.getPathSolid(path), "output/auto3dlab.scad")
