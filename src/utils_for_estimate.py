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
    # np.where() возвращает кортеж индексов, если условие shadow_mask == 1 - истинно  
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

# получаем необходимую зону в виде массива точек
def required_area(
    mask: np.ndarray,
    shadow_point: Tuple[int, int],
    threshold: int,
) -> np.ndarray:
    area_threshold = shadow_point[0] + threshold

# с помощью среза массива mask получаем необходимую для нас область 
    return mask[shadow_point[0]: area_threshold, shadow_point[1]]


arr = np.array([[0, 1, 1, 0, 0, 0, 0],
                [0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0]])

point = estimate_shadow_points(arr)
print(point)
# abc = required_area(arr, (2054, 3203), 50)
# newarr = estimate_shadow_points(arr)
# angle = estimate_direction(45.0)

# projections = newarr @ angle
# print(projections)

# shadow_length_pixels = np.max(projections) - np.min(projections) + 1
# print(shadow_length_pixels)

# scale = 0.5
# shadow_length_meters = shadow_length_pixels * scale
# print(shadow_length_meters)