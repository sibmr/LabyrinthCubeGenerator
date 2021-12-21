class LabyrinthConfig:

    default_config = {
        "cubeSize": 4,
        "seed": 6,
        "levelWallThickness": 2,
        "levelPathThickness": 14,
        "levelSpacing": 17,
        "casingWallThickness": 1.2,
        "casingTolerance": 0.6,
        "viewSpacing" : 35
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
        **config01,
        "levelWallThickness": 1.6,
        "levelPathThickness": 14.5,
        "levelSpacing": 16.3,
        "casingTolerance": 0.3,
    }

    config04 = {
        **default_config,
        "levelWallThickness": 1.6,
        "levelPathThickness": 14.5,
        "cubeSize": 9
    }
    
    config05 = {
        **default_config,
        "seed": 8,
        "cubeSize": 10,
        "levelWallThickness": 1.2,
        "levelPathThickness": 15,
    }

    config06 = {
        **default_config,
        "levelWallThickness": 1.6,
        "levelPathThickness": 14.5,
        "cubeSize": 4,
        "levelSpacing": 16.3
    }
