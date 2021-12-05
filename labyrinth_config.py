class LabyrinthConfig:

    default_config = {
        "cubeSize": 4,
        "seed": 6,
        "levelWallThickness": 2,
        "levelPathThickness": 14,
        "levelSpacing": 17,
        "casingWallThickness": 1.2,
        "casingTolerance": 0.6,
    }

    config01 = {
        **default_config,
        "seed": 8,
        "levelWallThickness": 1.2,
        "levelPathThickness": 15,
    }

    config02 = {
        **default_config,
        "seed": 17,
        "levelWallThickness": 1.6,
        "levelPathThickness": 14.5,
    }

    config03 = {
        **default_config,
        "seed": 18,
        "levelWallThickness": 1.6,
        "levelPathThickness": 14.5,
    }
