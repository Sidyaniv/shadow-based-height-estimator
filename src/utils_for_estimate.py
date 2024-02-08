import math
import numpy as np


def estimate_direction(sun_azimuth_angle):
    # Convert azimuth angle to radians
    azimuth_radians = math.radians(sun_azimuth_angle)

    # Calculate shadow direction vector
    return np.array([math.sin(azimuth_radians), math.cos(azimuth_radians)])


def estimate_shadow_points(shadow_mask):
    # Find edge points of the shadow
    y_indices, x_indices = np.where(shadow_mask == 1)
    return np.array(list(zip(x_indices, y_indices)))


def find_heights_and_shadows(indices_shadows, mask, estimated_heights, threshold):
    heights = []
    shadows = []
    for key, shadow_point in indices_shadows.items():
        if 1 in required_area(mask, shadow_point, threshold):
            heights.append(estimated_heights[key])
            shadows.append(key)

    return heights, shadows


def required_area(mask, shadow_point, threshold):
    area_threshold = shadow_point[0] + threshold
    return mask[shadow_point[0]: area_threshold, shadow_point[1]]
