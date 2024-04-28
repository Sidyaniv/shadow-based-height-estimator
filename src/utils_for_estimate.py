import numpy as np
from typing import Tuple, Dict, List

def pixel2metr(pixels, scale: np.float16) -> float:
    return pixels * scale


def get_points(annotations) -> List[Tuple[float]]:  
    """get_points - get from annotations separated from each 
    other points of buildings and shadows

    Args:
        annotations (_type_): COCO annotation

    Returns:
        List[Tuple[float]], List[Tuple[float]] 
    """
    shawdows_tuples = {}
    buildings_tuples = {}
    for i, ann in enumerate(annotations):
        if ann['category_id'] == 2:
            # Разделяем точки по кортежам
            shawdows_points = ann['segmentation'][0]
            shawdows_tuples[i] = [(shawdows_points[index], shawdows_points[index + 1]) for index in range(0, len(shawdows_points), 2)]

        if ann['category_id'] == 1:
            # Разделяем точки по кортежам
            buildings_points = ann['segmentation'][0]
            buildings_tuples[i] = [(buildings_points[index], buildings_points[index + 1]) for index in range(0, len(buildings_points), 2)]
    return shawdows_tuples, buildings_tuples


def find_heights_and_shadows(
    rotated_shawdows_points: Dict[int, List[Tuple[float]]],
    rotated_buildings_points: Dict[int, List[Tuple[float]]],
    estimated_heights: Dict[int, float],
) -> Tuple[List[float]]:
    """find_heights_and_shadows - Looking for the ratio of the building to the appropriate height

    Args:
        rotated_shawdows_points (Dict[int, List[Tuple[float]]]): Rotated coordinates of shadow points
        rotated_buildings_points (Dict[int, List[Tuple[float]]]): Rotated coordinates of buildings points
        estimated_heights (Dict[int, float]): built height

    Returns:
        Tuple[List[float]]
    """
    heights = []
    buildings = []
    rotated_buildings_points_copy = rotated_buildings_points.copy()
    stop = False
    for shadow_key, shadow in rotated_shawdows_points.items():
        area_shadow = required_area(shadow)

        for building_key, building in rotated_buildings_points_copy.items():
            area_build = required_area(building)
            build_length = abs(np.max(area_build[1])) - abs(np.min(area_build[1]))

            for point in building:
                # проверяем входит ли точка здания в указанный диапозон, при положительном исходе выходим из цикла
                if np.min(area_shadow[0]) <= point[0] <= np.max(area_shadow[0]) :
                    if np.min(area_shadow[1]) <= point[1] <= np.min(area_shadow[1]) + build_length:
                        heights.append(estimated_heights[shadow_key])
                        buildings.append(building_key)
                        stop = True
                        del rotated_buildings_points_copy[building_key]
                        break
            if stop:
                stop = False
                break
    return heights, buildings


def required_area(rotated_shawdow_points: List[Tuple[float]],
                  ) -> Tuple[Tuple[float]]:
    unpacked_list = [item for sublist in rotated_shawdow_points for item in sublist]

    x_coordinates = unpacked_list[0::2]
    y_coordinates = unpacked_list[1::2]

    diapason_x = (np.max(x_coordinates), np.min(x_coordinates))
    diapason_y = (np.max(y_coordinates), np.min(y_coordinates))

    x_range = (diapason_x[0] , diapason_x[1])
    y_range = (diapason_y[0] , diapason_y[1])

    return x_range, y_range