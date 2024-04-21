import math
import numpy as np
from typing import Tuple, Dict, List
from PIL import Image


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


# получаем необходимую зону (полосу) в виде координат, ограничивающих её
def required_area(rotated_shawdow_points: List[Tuple[float]],
                  threshold: int
                  ) -> Tuple[Tuple[float]]:
    unpacked_list = [item for sublist in rotated_shawdow_points for item in sublist]

    x_coordinates = unpacked_list[0::2]
    y_coordinates = unpacked_list[1::2]

    diapason_x = (np.max(x_coordinates), np.min(x_coordinates))
    diapason_y = (np.max(y_coordinates), np.min(y_coordinates))

    x_range = (diapason_x[0] + threshold, diapason_x[1] - threshold)
    y_range = (diapason_y[0] + threshold, diapason_y[1] - threshold)

    return x_range, y_range


def find_horizontal_area(shadow_points: List[Tuple[float]],
              threshold: int,) -> Tuple[Tuple[float]]:
    x_diaposon = required_area(shadow_points, threshold)[0]

    x_max_range = (x_diaposon[0], x_diaposon[0] - 2 * threshold)
    x_min_range = (x_diaposon[1] + 2 * threshold, x_diaposon[1])
    return x_max_range, x_min_range


def extreme_points(rotated_shawdow_points: List[Tuple[float]],
                   horizontal_area: Tuple[Tuple[float]]
                  ) -> Tuple[Tuple[float]]:

    right_range = horizontal_area[0]
    left_range = horizontal_area[1]

    right_y_max_point = [None, 0]
    right_y_min_point = [None, 1000000]

    left_y_max_point = [None, 0]
    left_y_min_point = [None, 1000000]

    for point in rotated_shawdow_points:
        # находим крайние точки минимального диапозона y
        if right_range[1] <= point[0] <= right_range[0]:
            if point[1] > right_y_max_point[1]:
                right_y_max_point = point
            if point[1] < right_y_min_point[1]:
                right_y_min_point = point

        # находим крайние точки максимального диапозона y
        if left_range[1] <= point[0] <= left_range[0]:
            if point[1] > left_y_max_point[1]:
                left_y_max_point = point
            if point[1] < left_y_min_point[1]:
                left_y_min_point = point
    return  [left_y_min_point, right_y_max_point, left_y_max_point, right_y_min_point]


def extra_rotate_angle(extreme_points: List[List[Tuple[float]]],):
    
# катеты
    leg_1_x = round(extreme_points[1][0] - extreme_points[0][0], 2)
    leg_1_y = round(extreme_points[1][1] - extreme_points[0][1], 2)

    leg_2_x = round(extreme_points[2][0] - extreme_points[3][0], 2)
    leg_2_y = round(extreme_points[2][1] - extreme_points[3][1], 2)

    if leg_1_y <= 0:
        angle_1 = 180 - (math.atan(leg_1_x / abs(leg_1_y) ) * 180 / 3.14)
    else: 
        angle_1 = math.atan(leg_1_x / leg_1_y) * 180 / 3.14

    if leg_2_y <= 0:
        angle_2 = math.atan(leg_2_x / abs(leg_2_y)) * 180 / 3.14
    else:
        angle_2 = math.atan(leg_2_x / leg_2_y) * 180 / 3.14

    return round((angle_1 + angle_2) / 2, 2)


# def extreme_points(rotated_shawdow_points: List[Tuple[float]],
#                   ) -> Tuple[Tuple[float]]:
#     unpacked_list = [item for sublist in rotated_shawdow_points for item in sublist]

#     x_coordinates = unpacked_list[0::2]
#     y_coordinates = unpacked_list[1::2]

#     diapason_x = [np.max(x_coordinates), np.min(x_coordinates)]
#     diapason_y = [np.max(y_coordinates), np.min(y_coordinates)]

#     for index, coordinate in enumerate(x_coordinates):
#         if coordinate == diapason_x[0]:
#             x_max_point = (diapason_x[0], y_coordinates[index])
#         if coordinate == diapason_x[1]:
#             x_min_point = (diapason_x[1], y_coordinates[index])

#         # if x_max_point and x_min_point:
#         #     break


#     for index, coordinate in enumerate(y_coordinates):
#         if coordinate == diapason_y[0]:
#             y_max_point = (x_coordinates[index], diapason_y[0])
#         if coordinate == diapason_y[1]:
#             y_min_point = (x_coordinates[index], diapason_y[1])

#         # if y_max_point and y_min_point:
#             # break
#     return (x_max_point, x_min_point, y_max_point, y_min_point)


# def extra_rotate_angle(extreme_points: Tuple[Tuple[float]],):
#     x_point_max, x_point_min = extreme_points[0], extreme_points[1]
#     y_point_max, y_point_min = extreme_points[2], extreme_points[3]

# # катеты
#     leg_1_2 = round(x_point_min[0] - x_point_max[0], 2)
#     leg_1_1 = round(x_point_max[1] - x_point_min[1], 2)

#     leg_2_1 = round(y_point_max[1] - y_point_min[1], 2)
#     leg_2_2 = round(y_point_min[0] - y_point_max[0], 2)

    
#     angle_x = np.arctan(leg_1_1 / leg_1_2) * 180 / 3.14
#     angle_y = np.arctan(leg_2_1 / leg_2_2) * 180 / 3.14

#     return (angle_x + angle_y) / 2
# 1. Находим координаты точки с максимальным y и координаты точки с минимальным y
# 2. Находим координаты точки с максимальным x и координаты точки с минимальным x
# 3. Находим 2 точки: 1. Точка, лежащая на оси x уже повернутого изображения и имеющая координату x = y_max[0] и y = y_min[1]. Для y
#                     2. Точка, лежащая на оси x уже повернутого изображения и имеющая координату x = x_max[0] и y = x_min[1]. Для x