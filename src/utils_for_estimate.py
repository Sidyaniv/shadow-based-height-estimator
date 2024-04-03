import math
import numpy as np
from typing import Tuple, Dict, List
from PIL import Image



def data_from_tiff(image):
    pass


def radians_azimuth_angle(sun_azimuth_angle: float) -> np.ndarray:
    return math.radians(sun_azimuth_angle)


def get_image_center(image_path) -> Tuple[float, float]:
    image = Image.open(image_path)
    
    width, height = image.size
    
    image.close()
    return (width / 2, height / 2)

# def estimate_direction(sun_azimuth_angle: float) -> np.ndarray:
#     # Convert azimuth angle to radians
#     azimuth_radians = math.radians(sun_azimuth_angle)

#     # Calculate shadow direction vector
#     return np.array([math.sin(azimuth_radians), math.cos(azimuth_radians)])


def get_points(annotations) -> List[Tuple[float]]:
    shawdows_pairs = {}
    buildings_pairs = {}
    for i, ann in enumerate(annotations):
        if ann['category_id'] == 2 :
            # Разделяем точки по кортежам
            shawdows_points = ann['segmentation'][0] 

            shawdows_pairs[i] = [(shawdows_points[index], shawdows_points[index+1]) for index in range(0, len(shawdows_points), 2)]

        if ann['category_id'] == 1 :
            # Разделяем точки по кортежам
            buildings_points = ann['segmentation'][0] 

            buildings_pairs[i] = [(buildings_points[index], buildings_points[index+1]) for index in range(0, len(buildings_points), 2)]
    return shawdows_pairs, buildings_pairs


def find_heights_and_shadows(
    shawdows_points: Dict[int, List[Tuple[float]]],
    buildings_points: Dict[int, List[Tuple[float]]],
    estimated_heights: Dict[int, float],
    threshold: int,
) -> Tuple[float, int]:

    heights = []
    shadows = []
    for key, shawdow in enumerate(shawdows_points):
            
            # area = required_area(points, threshold)
            for poi in buildings_points:
                heights.append(estimated_heights[key])
                shadows.append(key)

    return heights, shadows

# получаем необходимую зону в виде массива точек
def required_area(
    shadow_point: Tuple[int, int],
    threshold: int,
) -> Tuple[float]:
    
    area_threshold_max = shadow_point[1] + threshold
    area_threshold_min = shadow_point[1] - threshold
    
    return area_threshold_min, area_threshold_max
    