import numpy as np
from src.shadow_height_estimator import estimate_single_building_height


if __name__ == '__main__':
    shadow_mask = np.array(
        [[0, 0, 0, 1, 0, 0],
         [0, 0, 1, 1, 1, 0],
         [1, 1, 0, 1, 1, 0],
         [0, 0, 0, 0, 0, 0],
         ],
    )

    sun_azimuth_angle = 90
    scale = 1
    sun_elevation_angle = 45

    building_height = estimate_single_building_height(
        shadow_mask, sun_azimuth_angle, scale, sun_elevation_angle,
    )

    print('building_height', building_height)
