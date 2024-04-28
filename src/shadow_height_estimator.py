import math
import numpy as np

from typing import Dict, List, Union, Tuple
from src.utils_for_estimate import find_heights_and_shadows, pixel2metr, get_points


def estimate_buildings_height(rotated_shadow_points: Dict[int, List[Tuple[float]]],
                              scale,
                              sun_elevation_angle,) -> Dict[int, float]:
    """estimate_buildings_height - estimate the height of the building in meters

    Args:
        rotated_shadow_points (Dict[int, List[Tuple[float]]]): 
        scale (float): meters in pixels
        sun_elevation_angle (int): sunangle

    Returns:
        Dict[int, float]
    """
    dict_of_heights = {}
    for key, points in rotated_shadow_points.items():
        # распаковываем координаты, лежащие в кортежах, в список
        unpacked_list = [item for sublist in points for item in sublist]
        # выделям y-координаты
        list_of_y = unpacked_list[1::2]

        shadow_length_pixels = np.max(list_of_y) - np.min(list_of_y)
        shadow_length_meters = pixel2metr(shadow_length_pixels, scale)
        building_height = abs(math.tan(sun_elevation_angle) * shadow_length_meters)

        dict_of_heights[key] = round(building_height, 2)

    return dict_of_heights


def rotate_point(x_coordinate: float,
                 y_coordinate: float,
                 angle: float,
                 ) -> Tuple[float]:
    """rotate_point - rotate 1 point

    Args:
        x_coordinate (float): x axis coordinate
        y_coordinate (float): y axis coordinate
        angle (float): angle of rotate basis

    Returns:
        Tuple[float]
    """
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle), np.cos(angle)]])

    rotated_dx, rotated_dy = np.dot(rotation_matrix, [x_coordinate, y_coordinate])

    new_x = round(rotated_dx, 2)
    new_y = round(rotated_dy, 2)

    return new_x, new_y


def rotate_points(points: Dict[int, List[Tuple[float]]],
                  rotate_angle: float) -> Dict[int, List[Tuple[float]]]:
    """rotate_points - Consider the coordinates of the points relative to the rotated basis

    Args:
        points (Dict[int, List[Tuple[float]]]): list of points
        rotate_angle (float): angle of rotate basis

    Returns:
        Dict[int, List[Tuple[float]]]
    """
    dict_of_points = {}
    for key, rot_points in points.items():
        dict_of_points[key] = []

        for point in rot_points:
            coordinates = rotate_point(x_coordinate=point[0],
                                       y_coordinate=point[1],
                                       angle=rotate_angle,
                                       )
            dict_of_points[key].append(coordinates)

    return dict_of_points


def rotate_angle(sun_azimuth_angle: float) -> float:
    return np.deg2rad(sun_azimuth_angle + 90) 


def attach_heights(
    indices_shadows: Dict[int, float],
    estimated_building_heights: Tuple[list],
) -> Dict[int, Union[float, List[int]]]:
    """attach heights from shadows to building

    Args:
        indices_shadows: Dict[int, float] - the ratio of the shadow to the height of its building 
    Returns:
        Dict[str, Dict[int, List[float]], str, Dict[int, List[int]]]:
          {'buildings heights': {index of building: estimated height},
          'building shadow: {index of building: index of shadow}
          }
    """
    building_heights, building_shadows = {}, {}
    heights, building_indices = estimated_building_heights[0], estimated_building_heights[1]

    for i, height in enumerate(heights):
        building_heights.update({building_indices[i]: height})
        # ищем индекс тени относящийся к определённой высоте
        shadow_index = [key for key, value in indices_shadows.items() if value == height]
        building_shadows.update({building_indices[i]: shadow_index})

    return {'building_heights': building_heights, 'building_shadow': building_shadows}


def buildings_info(hyperparameters) -> Dict[int, Union[float, int]]:
    """
    Creates a dictionary where the key is the number `int` of the building's
    COCO annotation, and the value is the building annotation corresponding
    to this index and height that may belong to this annotation.

    As input, it accepts annotation, the value of the sun's azimuth angle
    in degrees `float`, a scale `int` that indicates how many meters are in one
    pixel of the image, the sun's elevation angle `float` in degrees, the threshold `int`.
    For searching for the building closest to the shadow for marking. Heights are calculated
    from shadow annotations and matched to buildings using a threshold.

    Args:
        Dict[
            'anns': COCO annotations
            'sun_azimuth_angle': float in degrees
            'scale': int
            'sun_elevation_angle': float in degrees
            'threshold': int
            ]

    Returns:
        {uid: {'annotation': COCO annotation, 'heights': float}}
    """
    hyperparameters['sun_azimuth_angle'] = np.deg2rad(hyperparameters['sun_azimuth_angle'])
    hyperparameters['sun_elevation_angle'] = np.deg2rad(hyperparameters['sun_elevation_angle'])

    shadows_points, building_points = get_points(hyperparameters['anns'])

    angle_of_rotate = rotate_angle(hyperparameters['sun_azimuth_angle'])

    rotated_points_of_shadows = rotate_points(points=shadows_points,
                                              rotate_angle=angle_of_rotate)

    rotated_points_of_buildings = rotate_points(points=building_points,
                                                rotate_angle=angle_of_rotate)

    shadows_heigth = estimate_buildings_height(rotated_points_of_shadows,
                                               hyperparameters['scale'],
                                               hyperparameters['sun_elevation_angle'],
                                               )

    heights_and_shadows = find_heights_and_shadows(rotated_points_of_shadows,
                                                   rotated_points_of_buildings,
                                                   shadows_heigth,
                                                   )

    building_heights_shadows = attach_heights(shadows_heigth, 
                                              heights_and_shadows)

    result_dict = {}

    for idx_building, heigths in building_heights_shadows['building_heights'].items():
        result_dict[idx_building] = {
            'anns': hyperparameters['anns'][idx_building],
            'heigths': heigths,
        }

    return result_dict