from solid.solidpython import scad_render_to_file
from labyrinth_casing import LabyrinthCasing
from labyrinth_graph import LabyrinthGraph
from labyrinth_config import LabyrinthConfig
from subprocess import run


def exportStl(name: str):
    run(["openscad", "-o", f"{name}.stl", f"{name}.scad"])


if __name__ == "__main__":

    config = LabyrinthConfig.config02
    config["levelSpacing"] = 35

    lgraph = LabyrinthGraph(config["cubeSize"])
    lgraph.setRandomTree(config["seed"])

    lcube = lgraph.getLabyrinthCube(
        config["levelWallThickness"],
        config["levelPathThickness"],
        config["levelSpacing"],
    )
    print(lcube.levels[0].levelSizeXY)
    lcube.addAllWindows()

    lcase = LabyrinthCasing(
        lcube, config["casingWallThickness"], config["casingTolerance"]
    )
    path = lgraph.findPath(lgraph.topCornerNode, lgraph.bottomCornerNode)

    name = "output/casing1"
    lcase.createScadFile(name)
    exportStl(name)
    for i, level in enumerate(lcube.levels):
        name = f"output/level{i}"
        level.createScadFile(name)
        exportStl(name)

    # scad_render_to_file(lcase.getCubeInCasingSolid(), "output/auto3dlab.scad")
    scad_render_to_file(lcube.getCubeSolid() + lcube.getPathSolid(path), "output/auto3dlab.scad")
