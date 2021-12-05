import argparse, os
from solid.objects import cube

from solid.solidpython import scad_render_to_file
from labyrinth_casing import LabyrinthCasing
from labyrinth_graph import LabyrinthGraph
from labyrinth_config import LabyrinthConfig
from subprocess import run


def exportStl(name: str):
    run(["openscad", "-o", f"{name}.stl", f"{name}.scad"])


def check_path(path_name: str) -> str:
    if os.path.isdir(path_name):
        return path_name
    else:
        os.makedirs(path_name)
        return path_name


def check_config(config_name: str) -> dict:
    try:
        return {
            "config_name": config_name,
            "config": getattr(LabyrinthConfig, config_name),
        }
    except AttributeError:
        raise AttributeError(f'the config named "{config_name}" does not exist')


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Generate a Labyrinth Cube")

    parser.add_argument("c", help="name of the config to use", type=check_config)
    parser.add_argument("p", help="path for .scad and .stl output", type=check_path)

    parser.add_argument(
        "--vp",
        help="output .scad file for labyrinth path visualization",
        dest="path_vis",
        action="store_true",
    )
    parser.add_argument(
        "--vc",
        help="output .scad file for labyrinth path visualization",
        dest="case_vis",
        action="store_true",
    )
    parser.add_argument(
        "--stl",
        help="output .stl files labyrinth levels and casing",
        dest="stl",
        action="store_true",
    )
    parser.set_defaults(path_vis=False)
    parser.set_defaults(case_vis=False)
    parser.set_defaults(stl=False)

    args = parser.parse_args()
    print(args)

    config = args.c["config"]
    config_name = args.c["config_name"]

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

    if args.stl:
        name = os.path.join(args.p, f"casing_{config_name}")
        lcase.createScadFile(name)
        exportStl(name)
        for i, level in enumerate(lcube.levels):
            name = os.path.join(args.p, f"level{i}_{config_name}")
            level.createScadFile(name)
            exportStl(name)

    if args.case_vis:
        lcube.spacing = config["levelSpacing"]
        vis_output_path = os.path.join(args.p, "labyrinth_case_visualization.scad")
        scad_render_to_file(lcase.getCubeInCasingSolid(), vis_output_path)
    if args.path_vis:
        lcube.spacing = config["viewSpacing"]
        vis_output_path = os.path.join(args.p, "labyrinth_path_visualization.scad")
        scad_render_to_file(
            lcube.getCubeSolid() + lcube.getPathSolid(path), vis_output_path
        )
