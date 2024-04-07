import math
import numpy as np
from scipy.ndimage import rotate
from typing import Dict, List, Union, Tuple, Optional
from src.utils_for_estimate import find_heights_and_shadows, pixel2metr


# def estimate_single_building_height(
#     shadow_mask: np.ndarray,
#     sun_azimuth_angle: float,
#     scale: float,
#     sun_elevation_angle: float,
# ) -> float:
#     """Estimate single building height

#     Args:
#         shadow_mask (np.ndarray): building shadow mask
#         sun_azimuth_angle (float):
#         scale (float): meters in 1 pixel 
#         sun_elevation_angle (float):

#     Returns:
#         float: height of single building
#     """

#     # Project points along shadow direction and find max distance
#     # Проекция точек вдоль направления тени и нахождение максимального расстояния
#     projections = estimate_shadow_points(shadow_mask) @ estimate_direction(
#         sun_azimuth_angle,
#     )

#     shadow_length_pixels = np.max(projections) - np.min(projections) + 1
#     shadow_length_meters = shadow_length_pixels * scale

#     return math.tan(math.radians(sun_elevation_angle)) * shadow_length_meters


def estimate_buildings_height(rotated_shadow_points: Dict[int, List[Tuple[float]]],
                              scale,
                              sun_elevation_angle,) -> Dict[int, float]:
    dict_of_heights = {}
    for key, points in rotated_shadow_points.items():
        # points - список кортежей
        str_key = str(key)
        points = rotated_shadow_points[key]
        # for points in rotated_shadow_points[str_key]:
            # распаковываем координаты из кортежей
        unpacked_list = [item for sublist in points for item in sublist]
        # выделям y-координаты
        list_of_y = unpacked_list[1::2]
        
        shadow_length_pixels = np.max(list_of_y) - np.min(list_of_y)
        shadow_length_meters = pixel2metr(shadow_length_pixels, scale)
        building_height = math.tan(math.radians(sun_elevation_angle)) * shadow_length_meters
        
        dict_of_heights[key] = round(building_height, 2)

    return  dict_of_heights



def rotate_point(x_coordinate, y_coordinate, angle, center) -> Tuple[float]:
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle), np.cos(angle)]])
    
    dx = x_coordinate - center[0]
    dy = y_coordinate - center[1]

    # Применяем матрицу поворота к разности координат
    rotated_dx, rotated_dy = np.dot(rotation_matrix, [dx, dy])

    # Добавляем результат к координатам центра поворота
    new_x = round(center[0] + rotated_dx, 2)
    new_y = round(center[1] + rotated_dy, 2)

    return new_x, new_y


def rotate_points(points: Dict[int, List[float]],
                #   points: Dict[int, List[Tuple[float]]],
                  center: Tuple[float],
                  rotate_angle: float) -> Dict[int, List[Tuple[float]]]:

    dict_of_points = {}
    for key in points.keys():
        dict_of_points[key] = []

        for point in points[key]:
            coordinates = rotate_point(x_coordinate=point[0],
                                       y_coordinate=point[1], 
                                       angle=rotate_angle,
                                       center=center
                                       )
            dict_of_points[key].append(coordinates)
    
    return dict_of_points


# def take_indices_shadows(masks: np.ndarray) -> Dict[int, Tuple[int]]:
#     """take down indices of shadows

#     Args:
#         masks (np.ndarray): binary masks

#     Returns:
#         Dict[int, Tuple[int]]: indices of shadows
#     """
#     # {index of shadow: (max(y), mean(x))}
#     indices_shadows = {}
#     for i, mask in enumerate(masks):
#         if np.array_equal(np.unique(mask), np.array([0, 2])):
#             indices = np.where(mask == 2)
#             y_center = np.mean(indices[1]).astype(int)
#             indices_shadows[i] = (np.max(indices[0]), y_center)
#     return indices_shadows


# def estimate_building_heights(
#     masks: np.ndarray,
#     sun_azimuth_angle: float,
#     scale: float,
#     sun_elevation_angle: float,
# ) -> Dict[int, float]:
#     """summary func estimate building height for binary masks

#     Args:
#         masks (np.ndarray): binary masks
#         sun_azimuth_angle (float): sun azimuth angle
#         scale (float): meters in pixel
#         sun_elevation_angle (float): sun elevation angle for picture

#     Returns:
#         Dict[int, float]: {index of shadow: estimated height}
#     """
#     building_heights = {}
#     for i, mask in enumerate(masks):
#         if np.array_equal(np.unique(mask), np.array([0, 2])):
#             building_shadow = np.where(mask == 2, 1, mask)
#             building_height = estimate_single_building_height(
#                 building_shadow,
#                 sun_azimuth_angle,
#                 scale,
#                 sun_elevation_angle,
#             )
#             building_heights[i] = np.round(building_height, 2)
#     return building_heights


def attach_heights(  # noqa: WPS234
    rotated_points: Tuple[float],
    estimated_heights: Dict[int, float],
    indices_shadows: Dict[int, Tuple[int]],
    threshold: int,
) -> Dict[int, Union[List[float], List[int]]]:
    """attach heights from shadows to building

    Args:
        rotated_masks (np.ndarray): binary masks
        estimated_heights (Dict[int, float]): estimated heights of shadows
        indices_shadows (Dict[int, Tuple[int, int]]): indices of shadows
        threshold (int): threshold of search building for estimated height of shadow

    Returns:
        Dict[str, Dict[int, List[float]], str, Dict[int, List[int]]]:
          {'buildings heights': {index of building: estimated height},
          'building-shadow: {index of building: index of shadow}
          }
    """
    building_heights, building_shadows = {}, {}
    for i, mask in enumerate(rotated_points):
        if 1 in mask:
            heights_shadows = find_heights_and_shadows(
                indices_shadows,
                mask,
                estimated_heights,
                threshold,
            )
            building_heights.update({i: heights_shadows[0]})
            building_shadows.update({i: heights_shadows[1]})

    return {'building_heights': building_heights, 'building_shadow': building_shadows}


# def estimate_rotate_angle(sun_azimuth_angle: float) -> float:
#     return 360.0 - (sun_azimuth_angle + 90.0) 


# def buildings_info(  # noqa: WPS234
#     hyperparameters: Dict[str, Optional[Union[Dict[Tuple[float]], float, int, float, int]]],  # noqa: WPS221
# ) -> Dict[int, Union[np.ndarray, List[float]]]:
#     """
#     Creates a dictionary where the key is the number `int` of the building's binary
#     mask in the masks `np.ndarray`, and the value is the building mask corresponding
#     to this index and a list of heights `List[float]` that may belong to this mask.

#     As input, it accepts masks `np.ndarray`, the value of the sun's azimuth angle
#     in degrees `float`, a scale `int` that indicates how many meters are in one
#     pixel of the image, the sun's elevation angle `float` in degrees, and the threshold `int`
#     for searching for the building closest to the shadow for marking. Heights are calculated
#     from shadow masks and matched to buildings using a threshold.
#     It is important to choose the right threshold for calculating building heights.

#     Args:
#         Dict[
#             'points': Dict[Tuple[float]]
#             'sun_azimuth_angle': float
#             'scale': int
#             'sun_elevation_angle': float
#             'threshold': int
#             ]

#     Returns:
#         {uid: {'mask': np.ndarray, 'heights': List[float]}}
#     """

#     # rotated_masks = rotate_masks(hyperparameters['masks'], estimate_rotate_angle(hyperparameters['sun_azimuth_angle']))

#     # dict {'building_heights': {index of building: [estimated heights]},
#     # 'building_shadow': {index of building: [indices of shadows]}}
#     building_heights_shadows = attach_heights(
#         rotated_masks,
#         estimate_building_heights(
#             hyperparameters['masks'],
#             hyperparameters['sun_azimuth_angle'],
#             hyperparameters['scale'],
#             hyperparameters['sun_elevation_angle'],
#         ),
#         take_indices_shadows(rotated_masks),
#         hyperparameters['threshold'],
#     )

#     result_dict = {}

#     for idx_building, heights in building_heights_shadows['building_heights'].items():
#         result_dict[idx_building] = {
#             'mask': hyperparameters['masks'][idx_building],
#             'heights': heights,
#         }

#     return result_dict


# import matplotlib.pyplot as plt
# from scipy.ndimage import rotate
# from utils_for_estimate import (get_points,
#                                     get_image_center,
#                                     )
# from annotations.annotation import coco2masks, anns_and_images, attach_bboxes
# import numpy as np

# dataset_dir = '../3d_tools_dataset/'
# annot_file = dataset_dir + 'annotations/instances_default.json'
# images_directory = dataset_dir + 'image_png/'
# image_directory = dataset_dir + 'image_png/test_1.png'

# SCALE = np.float16(0.1)
# SUN_AZIMUTH_ANGLE = np.uint8(100)
# SUN_ELEVATION_ANGLE = np.uint8(30)
# ROTATE_ANGLE = 360.0 - (SUN_AZIMUTH_ANGLE + 90.0)
# THRESHOLD = np.uint8(7)
# BROWN = (np.uint8(128), np.uint8(64), np.uint8(48))
# BLUE = (np.uint8(0), np.uint8(0), np.uint8(255))
# COLORS = np.array([BROWN, BLUE])

# image, anns = anns_and_images(coco_annotation_file=annot_file, images_directory=images_directory)
# masks = coco2masks(coco_annotation_file=annot_file, images_directory=images_directory)

# shadows_points = get_points(anns)[0]
# building_points = get_points(anns)[1]

# shadows_bboxes = attach_bboxes(shadows_points, building_points, anns)[0]
# building_bboxes = attach_bboxes(shadows_points, building_points, anns)[1]

# center = get_image_center(image_path=image_directory)
# rotated_points_of_shadows = rotate_points(points=shadows_points, center=center, rotate_angle=ROTATE_ANGLE)
# rotated_points_of_building = rotate_points(points=building_points, center=center, rotate_angle=ROTATE_ANGLE)
# # rotated_bbox = rotate_point()

# shadows_heigth = estimate_shawdows_height(rotated_points_of_shadows)
# # print(anns[1]['bbox'])
# print(shadows_heigth)