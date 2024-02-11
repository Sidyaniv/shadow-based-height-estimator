import math
import numpy as np
from scipy.ndimage import rotate
from typing import Dict, List, Union, Tuple, Optional
from src.utils_for_estimate import (
    estimate_direction,
    estimate_shadow_points,
    find_heights_and_shadows,
)


def estimate_single_building_height(
    shadow_mask: np.ndarray,
    sun_azimuth_angle: float,
    scale: float,
    sun_elevation_angle: float,
) -> float:
    """Estimate single building height

    Args:
        shadow_mask (np.ndarray): building shadow mask
        sun_azimuth_angle (float):
        scale (float): meters in 1 pixel
        sun_elevation_angle (float):

    Returns:
        float: height of single building
    """

    # Project points along shadow direction and find max distance
    projections = estimate_shadow_points(shadow_mask) @ estimate_direction(
        sun_azimuth_angle,
    )

    shadow_length_pixels = np.max(projections) - np.min(projections) + 1
    shadow_length_meters = shadow_length_pixels * scale

    return math.tan(math.radians(sun_elevation_angle)) * shadow_length_meters


def rotate_masks(masks: np.ndarray, angle: float) -> np.ndarray:
    """rotate masks in list on angle

    Args:
        masks (np.ndarray): binary masks
        angle (float): sun_azimuth_angle - 180

    Returns:
        np.ndarray: rotatedlist
    """
    rotated_list = []
    idx_shad = 2
    for mask in masks:
        rotated = rotate(mask, angle)

        if idx_shad in rotated:
            rotated = np.where(rotated != idx_shad, 0, rotated)

        rotated_list.append(rotated)

    return rotated_list


def take_indices_shadows(masks: np.ndarray) -> Dict[int, Tuple[int, int]]:
    """take down indices of shadows

    Args:
        masks (np.ndarray): binary masks

    Returns:
        Dict[int, Tuple[int, int]]: indices of shadows
    """
    # {index of shadow: (max(y), mean(x))}
    indices_shadows = {}
    for i, mask in enumerate(masks):
        if np.array_equal(np.unique(mask), np.array([0, 2])):
            indices = np.where(mask == 2)
            y_center = np.mean(indices[1]).astype(int)
            indices_shadows[i] = (np.max(indices[0]), y_center)
    return indices_shadows


def estimate_building_heights(
    masks: np.ndarray,
    sun_azimuth_angle: float,
    scale: float,
    sun_elevation_angle: float,
) -> Dict[int, float]:
    """summary func estimate building height for binary masks

    Args:
        masks (np.ndarray): binary masks
        sun_azimuth_angle (float): sun azimuth angle
        scale (float): meters in pixel
        sun_elevation_angle (float): sun elevation angle for picture

    Returns:
        Dict[int, float]: {index of shadow: estimated height}
    """
    building_heights = {}
    for i, mask in enumerate(masks):
        if np.array_equal(np.unique(mask), np.array([0, 2])):
            building_shadow = np.where(mask == 2, 1, mask)
            building_height = estimate_single_building_height(
                building_shadow,
                sun_azimuth_angle,
                scale,
                sun_elevation_angle,
            )
            building_heights[i] = np.round(building_height, 2)
    return building_heights


def attach_heights(  # noqa: WPS234
    rotated_masks: np.ndarray,
    estimated_heights: Dict[int, float],
    indices_shadows: Dict[int, Tuple[int, int]],
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
    for i, mask in enumerate(rotated_masks):
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


def estimate_rotate_angle(sun_azimuth_angle: float) -> float:
    pi = 180.0
    return sun_azimuth_angle - pi


def buildings_info(  # noqa: WPS234
    hyperparameters: Dict[str, Optional[Union[np.ndarray, float, int, float, int]]],  # noqa: WPS221
) -> Dict[int, Union[np.ndarray, List[float]]]:
    """
    Creates a dictionary where the key is the number `int` of the building's binary
    mask in the masks `np.ndarray`, and the value is the building mask corresponding
    to this index and a list of heights `List[float]` that may belong to this mask.

    As input, it accepts masks `np.ndarray`, the value of the sun's azimuth angle
    in degrees `float`, a scale `int` that indicates how many meters are in one
    pixel of the image, the sun's elevation angle `float` in degrees, and the threshold `int`
    for searching for the building closest to the shadow for marking. Heights are calculated
    from shadow masks and matched to buildings using a threshold.
    It is important to choose the right threshold for calculating building heights.

    Args:
        Dict[
            'masks': np.ndarray
            'sun_azimuth_angle': float
            'scale': int
            'sun_elevation_angle': float
            'threshold': int
            ]

    Returns:
        {uid: {'mask': np.ndarray, 'heights': List[float]}}
    """

    rotated_masks = rotate_masks(hyperparameters['masks'], estimate_rotate_angle(hyperparameters['sun_azimuth_angle']))

    # dict {'building_heights': {index of building: [estimated heights]},
    # 'building_shadow': {index of building: [indices of shadows]}}
    building_heights_shadows = attach_heights(
        rotated_masks,
        estimate_building_heights(
            hyperparameters['masks'],
            hyperparameters['sun_azimuth_angle'],
            hyperparameters['scale'],
            hyperparameters['sun_elevation_angle'],
        ),
        take_indices_shadows(rotated_masks),
        hyperparameters['threshold'],
    )

    result_dict = {}

    for idx_building, heights in building_heights_shadows['building_heights'].items():
        result_dict[idx_building] = {
            'mask': hyperparameters['masks'][idx_building],
            'heights': heights,
        }

    return result_dict
