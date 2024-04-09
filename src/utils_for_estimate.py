import math
import numpy as np
from typing import Tuple, Dict, List
from PIL import Image


def data_from_tiff(image):
    pass


def radians_azimuth_angle(sun_azimuth_angle: float) -> np.ndarray:
    return math.radians(sun_azimuth_angle)


def pixel2metr(pixels, scale: np.float16) -> float:
    return pixels * scale


def get_image_center(image_path: str) -> Tuple[float, float]:
    image = Image.open(image_path)

    width, height = image.size

    image.close()
    return (width / 2, height / 2)


def get_points(annotations) -> List[Tuple[float]]:  # noqa E501
    shawdows_tuples = {}
    buildings_tuples = {}
    for i, ann in enumerate(annotations):
        if ann['category_id'] == 2:
            # Разделяем точки по кортежам
            shawdows_points = ann['segmentation'][0]
            # shawdows_pairs[i] =shawdows_points
            shawdows_tuples[i] = [(shawdows_points[index], shawdows_points[index + 1]) for index in range(0, len(shawdows_points), 2)]

        if ann['category_id'] == 1:
            # Разделяем точки по кортежам
            buildings_points = ann['segmentation'][0]
            # buildings_pairs[i] = buildings_points
            buildings_tuples[i] = [(buildings_points[index], buildings_points[index + 1]) for index in range(0, len(buildings_points), 2)]
    return shawdows_tuples, buildings_tuples


def find_heights_and_shadows(
    rotated_shawdows_points: Dict[int, List[Tuple[float]]],
    rotated_buildings_points: Dict[int, List[Tuple[float]]],
    estimated_heights: Dict[int, float],
    threshold: int,
) -> Tuple[List[float]]:
    heights = []
    buildings = []
    stop = False
    for shadow_key, shadow in rotated_shawdows_points.items():
        area = required_area(shadow, threshold)

        for building_key, building in rotated_buildings_points.items():

            for point in building:
                # проверяем входит ли точка здания в указанный диапозон, при положительном исходе выходим из цикла
                if area[0][1] <= point[0] <= area[0][0]:
                    if area[1][1] <= point[1] <= area[1][0]:
                        heights.append(estimated_heights[shadow_key])
                        buildings.append(building_key)
                        stop = True
                        del rotated_buildings_points[building_key]
                        break
            if stop:
                stop = False
                break

    return heights, buildings


# получаем необходимую зону в виде координат, ограничивающих её
def required_area(rotated_shawdow_points: List[Tuple[float]],
                  threshold: int,
                  ) -> Tuple[Tuple[float]]:
    unpacked_list = [item for sublist in rotated_shawdow_points for item in sublist]

    x_coordinates = unpacked_list[0::2]
    y_coordinates = unpacked_list[1::2]

    diapason_x = (np.max(x_coordinates), np.min(x_coordinates))
    diapason_y = (np.max(y_coordinates), np.min(y_coordinates))

    x_range = (diapason_x[0] + threshold, diapason_x[1] - threshold)
    y_range = (diapason_y[0] + threshold, diapason_y[1] - threshold)

    return x_range, y_range
