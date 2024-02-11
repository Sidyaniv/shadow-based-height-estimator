import math
import numpy as np
from typing import Tuple, Dict


def estimate_direction(sun_azimuth_angle: float) -> np.ndarray:
    # Convert azimuth angle to radians
    azimuth_radians = math.radians(sun_azimuth_angle)

    # Calculate shadow direction vector
    return np.array([math.sin(azimuth_radians), math.cos(azimuth_radians)])


def estimate_shadow_points(shadow_mask: np.ndarray) -> np.ndarray:
    # Find edge points of the shadow
    y_indices, x_indices = np.where(shadow_mask == 1)
    return np.array(list(zip(x_indices, y_indices)))


def find_heights_and_shadows(
    indices_shadows: Dict[int, Tuple[int, int]],
    mask: np.ndarray,
    estimated_heights: Dict[int, float],
    threshold: int,
) -> Tuple[float, int]:

    heights = []
    shadows = []
    for key, shadow_point in indices_shadows.items():
        if 1 in required_area(mask, shadow_point, threshold):
            heights.append(estimated_heights[key])
            shadows.append(key)

    return heights, shadows


def required_area(
    mask: np.ndarray,
    shadow_point: Tuple[int, int],
    threshold: int,
) -> np.ndarray:
    area_threshold = shadow_point[0] + threshold
    return mask[shadow_point[0]: area_threshold, shadow_point[1]]
