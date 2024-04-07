import math
import numpy as np
from typing import Tuple, Dict, List
from PIL import Image



def data_from_tiff(image):
    pass


def radians_azimuth_angle(sun_azimuth_angle: float) -> np.ndarray:
    return math.radians(sun_azimuth_angle)


def pixel2metr(pixels, scale: np.float16) -> float:
    return pixels*scale


def new_bbox(rotated_points):
    for key in rotated_points.keys():
        for points in rotated_points[key]:
            x_min = points[0][0]
            for point in range(0, len(rotated_points[key]) - 1):
                x_min = min(x1, x2)
                y_min = min(y1, y2)
                x_max = max(x1, x2)
                y_max = max(y1, y2)

    return x_min, y_min, x_max, y_max


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
            shawdows_pairs[i] =shawdows_points
            # shawdows_pairs[i] = [(shawdows_points[index], shawdows_points[index+1]) for index in range(0, len(shawdows_points), 2)]

        if ann['category_id'] == 1 :
            # Разделяем точки по кортежам
            buildings_points = ann['segmentation'][0] 
            buildings_pairs[i] = buildings_points
            # buildings_pairs[i] = [(buildings_points[index], buildings_points[index+1]) for index in range(0, len(buildings_points), 2)]
    return shawdows_pairs, buildings_pairs


def find_heights_and_shadows(
    shawdows_points: Dict[int, List[Tuple[float]]],
    buildings_points: Dict[int, List[Tuple[float]]],
    estimated_heights: Dict[int, float],
    threshold: int,
) -> Tuple[float, int]:

    heights = []
    buildings = []
    for shadow_key, shadow in shawdows_points.items():
            
            area = required_area(shadow, threshold)
            for building_key, building in buildings_points.items():
                for point in building:   
                    # проверяем входит ли точка здания в указанный диапозон, при положительном исходе выходим из цикла 
                    if area[0][1] <= point[0] <= area[0][0]:
                        if area[1][1] <= point[1] <= area[1][0]:
                            heights.append(estimated_heights[shadow_key])
                            buildings.append(building_key)    
                            break
            # выходим из цикла, если нашли нужное здание 
            if building_key in buildings: 
                break

    return heights, buildings


def get_diapason(shawdow_points: List[Tuple[float]]):
   
    for point in shawdow_points:
        pass

    return 1 

# получаем необходимую зону в виде массива точек
def required_area(
                coordiinate_range: Tuple[float],
                y: float,
                threshold: int,
                ) -> Tuple[Tuple[float]]:
    
    x_max = coordiinate_range[0] + threshold
    x_min = coordiinate_range[1] - threshold
    x_range = (x_max, x_min)

    y_range = (y + threshold, y - threshold)

    return x_range, y_range
    