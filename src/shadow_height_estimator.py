import math
import numpy as np

# from scipy.ndimage import rotate
from typing import Dict, List, Union, Tuple
from src.utils_for_estimate import find_heights_and_shadows, pixel2metr, get_points
# from src.annotations.annotation import anns_and_images


def estimate_buildings_height(rotated_shadow_points: Dict[int, List[Tuple[float]]],
                              scale,
                              sun_elevation_angle,) -> Dict[int, float]:
    dict_of_heights = {}
    for key, points in rotated_shadow_points.items():
        # распаковываем координаты, лежащие в кортежах, в список
        unpacked_list = [item for sublist in points for item in sublist]
        # выделям y-координаты
        list_of_y = unpacked_list[1::2]

        shadow_length_pixels = np.max(list_of_y) - np.min(list_of_y)
        shadow_length_meters = pixel2metr(shadow_length_pixels, scale)
        building_height = math.tan(math.radians(sun_elevation_angle)) * shadow_length_meters

        dict_of_heights[key] = round(building_height, 2)

    return dict_of_heights


def rotate_point(x_coordinate: float,
                 y_coordinate: float,
                 angle: float,
                 center: float
                 ) -> Tuple[float]:
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle), np.cos(angle)]])

    dx = x_coordinate - center[0]
    dy = y_coordinate - center[1]

    rotated_dx, rotated_dy = np.dot(rotation_matrix, [dx, dy])

    new_x = round(center[0] + rotated_dx, 2)
    new_y = round(center[1] + rotated_dy, 2)

    return new_x, new_y


def rotate_points(points: Dict[int, List[Tuple[float]]],
                  center: Tuple[float],
                  rotate_angle: float) -> Dict[int, List[Tuple[float]]]:

    dict_of_points = {}
    for key, rot_points in points.items():
        dict_of_points[key] = []

        for point in rot_points:
            coordinates = rotate_point(x_coordinate=point[0],
                                       y_coordinate=point[1],
                                       angle=rotate_angle,
                                       center=center
                                       )
            dict_of_points[key].append(coordinates)

    return dict_of_points


def rotate_angle(sun_azimuth_angle: float) -> float:
    return sun_azimuth_angle + 90


def attach_heights(
    indices_shadows: Dict[int, float],
    estimated_building_heights: Tuple[list],
) -> Dict[int, Union[float, List[int]]]:
    """attach heights from shadows to building

    Args:
        indices_shadows (Dict[int, float]): indices of shadows
        estimated_building_heights (Tuple[list]): two lists -
        1.height of building
        2.building index

    Returns:
        Dict[str, Dict[int, List[float]], str, Dict[int, List[int]]]:
          {'buildings heights': {index of building: estimated height},
          'building-shadow: {index of building: index of shadow}
          }
    """
    building_heights, building_shadows = {}, {}
    heights, building_indices = estimated_building_heights[0], estimated_building_heights[1]

    for i, height in enumerate(heights):
        building_heights.update({building_indices[i]: height})
        # ищем индекс тени для определённой высоты
        shadow_index = [key for key, value in indices_shadows.items() if value == height]
        building_shadows.update({building_indices[i]: shadow_index})

    return {'building_heights': building_heights, 'building_shadow': building_shadows}


def buildings_info(
    hyperparameters
) -> Dict[int, Union[float, int]]:
    """
    Creates a dictionary where the key is the number `int` of the building's
    COCO annotation in the masks `np.ndarray`, and the value is the building mask corresponding
    to this index and a list of heights `List[float]` that may belong to this annotation.

    As input, it accepts annotation, the value of the sun's azimuth angle
    in degrees `float`, a scale `int` that indicates how many meters are in one
    pixel of the image, the sun's elevation angle `float` in degrees, the threshold `int` and
    center of image. For searching for the building closest to the shadow for marking. Heights are calculated
    from shadow annotations and matched to buildings using a threshold.
    It is important to choose the right threshold for calculating building heights.

    Args:
        Dict[
            'anns': COCO annotations
            'sun_azimuth_angle': float
            'scale': int
            'sun_elevation_angle': float
            'threshold': int
            'img_center': float
            ]

    Returns:
        {uid: {'annotation': COCO annotation, 'heights': List[float]}}
    """

    shadows_points = get_points(hyperparameters['anns'])[0]
    building_points = get_points(hyperparameters['anns'])[1]

    angle_of_rotate = rotate_angle(hyperparameters['sun_azimuth_angle'])

    rotated_points_of_shadows = rotate_points(points=shadows_points,
                                              center=hyperparameters['img_center'],
                                              rotate_angle=angle_of_rotate)
    rotated_points_of_buildings = rotate_points(points=building_points,
                                                center=hyperparameters['img_center'],
                                                rotate_angle=angle_of_rotate)

    shadows_heigth = estimate_buildings_height(rotated_points_of_shadows,
                                               hyperparameters['scale'],
                                               hyperparameters['sun_elevation_angle'],
                                               )

    heights_and_shadows = find_heights_and_shadows(rotated_points_of_shadows,
                                                   rotated_points_of_buildings,
                                                   shadows_heigth,
                                                   hyperparameters['threshold']
                                                   )

    building_heights_shadows = attach_heights(
        estimate_buildings_height(
            rotated_points_of_shadows,
            hyperparameters['scale'],
            hyperparameters['sun_elevation_angle'],
        ),

        heights_and_shadows
    )

    result_dict = {}

    for idx_building, heights in building_heights_shadows['building_heights'].items():
        result_dict[idx_building] = {
            'anns': hyperparameters['anns'][idx_building],
            'heights': heights,
        }

    return result_dict

# from utils_for_estimate import (get_points,
#                                     get_image_center,
#                                     find_heights_and_shadows,
#                                     extreme_points,
#                                     extra_rotate_angle,
#                                     find_horizontal_area,
#                                     )
# from annotations.annotation import anns_and_images
# import numpy as np

# dataset_dir = '../3d_tools_dataset/'
# annot_file = dataset_dir + 'annotations/instances_default.json'
# images_directory = dataset_dir + 'image_png/'
# image_directory = dataset_dir + 'image_png/test_1.png'

# SCALE = np.float16(0.1)
# SUN_AZIMUTH_ANGLE = np.uint8(100)
# SUN_ELEVATION_ANGLE = np.uint8(30)
# ROTATE_ANGLE = SUN_AZIMUTH_ANGLE + 90.0
# THRESHOLD = np.uint8(5)
# BROWN = (np.uint8(128), np.uint8(64), np.uint8(48))
# BLUE = (np.uint8(0), np.uint8(0), np.uint8(255))
# COLORS = np.array([BROWN, BLUE])

# image, anns = anns_and_images(coco_annotation_file=annot_file, images_directory=images_directory)

# shadows_points = get_points(anns)[0]
# building_points = get_points(anns)[1]

# center = get_image_center(image_path=image_directory)
# rotated_points_of_shadows = rotate_points(points=shadows_points, center=center, rotate_angle=ROTATE_ANGLE)
# rotated_points_of_buildings = rotate_points(points=building_points, center=center, rotate_angle=ROTATE_ANGLE)

# extra_angles = {}
# list_of_areas = []
# for iteration, points_of_shadow in rotated_points_of_shadows.items():
#     area = find_horizontal_area(points_of_shadow, THRESHOLD)
#     extr_poi = extreme_points(points_of_shadow, area)
#     extra_angles[iteration] = extra_rotate_angle(extr_poi)
    
# shadows_heigth = estimate_buildings_height(rotated_points_of_shadows, SCALE, SUN_ELEVATION_ANGLE)

# find = find_heights_and_shadows(rotated_points_of_shadows,
#                                 rotated_points_of_buildings,
#                                 shadows_heigth,
#                                 THRESHOLD
#                                 )

# attach = attach_heights(shadows_heigth, find)


# print(extra_angles)
# print(shadows_heigth)