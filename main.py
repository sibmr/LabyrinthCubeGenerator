import argparse, os, json
import numpy as np

from solid.solidpython import scad_render_to_file
from labyrinth_casing import LabyrinthCasing
from labyrinth_graph import LabyrinthGraph
from labyrinth_config import LabyrinthConfig
from labyrinth_map import LabyrinthMap
from subprocess import run


def exportStl(name: str):
    run(["openscad", "-q", "--o", f"{name}.stl", f"{name}.scad"])


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


def str2int(string: str) -> int:
    return int(string)


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Generate a Labyrinth Cube")

    parser.add_argument("c", help="name of the config to use", type=check_config)
    parser.add_argument("p", help="path for .scad and .stl output", type=check_path)

    parser.add_argument(
        "-s", dest="set_seed", help="seed for random generation", type=str2int
    )
    parser.set_defaults(set_seed=-1)

    parser.add_argument(
        "--vp",
        help="output .scad file for labyrinth casing visualization",
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
    parser.add_argument(
        "--random",
        help="change random generation seed to random value and print it",
        dest="random",
        action="store_true",
    )
    parser.add_argument(
        "--no-windows",
        help="add windows to all floors",
        dest="windows",
        action="store_false",
    )
    parser.add_argument(
        "--map",
        help="create a map of the levels",
        dest="map",
        action="store_true",
    )
    parser.set_defaults(path_vis=False)
    parser.set_defaults(case_vis=False)
    parser.set_defaults(stl=False)
    parser.set_defaults(random=False)
    parser.set_defaults(windows=True)
    parser.set_defaults(maps=False)

    args = parser.parse_args()

    config = args.c["config"]
    config_name = args.c["config_name"]

    if args.random:
        new_seed = np.random.randint(10000000)
        config["seed"] = new_seed

    if args.set_seed >= 0:
        new_seed = args.set_seed
        config["seed"] = new_seed

    print("config = " + json.dumps(config, sort_keys=True, indent=4))

    lgraph = LabyrinthGraph(config["cubeSize"])
    lgraph.setRandomTree(config["seed"])

    lcube = lgraph.getLabyrinthCube(
        config["levelWallThickness"],
        config["levelPathThickness"],
        config["levelSpacing"],
    )
    print(f"Level width: {lcube.levels[0].levelSizeXY} mm")
    
    if args.windows:
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

    if args.map:
        lmap = LabyrinthMap(lcube=lcube)
        lmap.render_png(args.p)
    