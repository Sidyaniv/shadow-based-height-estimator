import numpy as np
import cv2
import random


def draw_masks(image, masks, colors):
    alpha = 0.3
    masked_image = image.copy()
    for mask in masks:
        if 1 in mask:
            label = 0
        else:
            label = 1

        masked_color =  np.where(
            np.repeat(mask[:, :, np.newaxis], 3, axis=2),
            np.expand_dims(np.asarray(colors[label], dtype='uint8'), axis=(0, 1)),
            0)

        masked_image = np.where(
            np.repeat(mask[:, :, np.newaxis], 3, axis=2),
             # перебираем элементы  np.repeat(mask[:, :, np.newaxis], 3, axis=2) и если значение элемента true, то на выходе получим соответствующий элемент  masked_color. иначе соответствующий элемент masked_image
            masked_color,
            # np.asarray(colors[label], dtype='uint8'),
            masked_image,
        )
        masked_image = masked_image.astype(np.uint8)
    return cv2.addWeighted(image, alpha, masked_image, 1 - alpha, 0)


def draw_random_masks(image, masks):
    alpha = 0.3
    masked_image = image.copy()
    max_value = 255
    for mask in masks:
        masked_image = np.where(
            np.repeat(mask[:, :, np.newaxis], 3, axis=2),
            np.random.randint(0, max_value, size=(3)),
            masked_image,
        )
        masked_image = masked_image.astype(np.uint8)
    return cv2.addWeighted(image, alpha, masked_image, 1 - alpha, 0)


def draw_sample_building_shadow(image, masks, building_shadow, colors):
    masked_image = image.copy()
    alpha = 0.3
    key = random.choice(list(building_shadow.keys()))  # noqa: S311
    blank = masks[key][:, :, np.newaxis]

    masked_image = np.where(
        # перебираем элементы np.repeat(blank, 3, axis=2) и если значение элемента true, то на выходе получим соответствующий элемент np.asarray(colors[0], dtype='uint8')
        np.repeat(blank, 3, axis=2),
        np.asarray(colors[0], dtype='uint8'),
        masked_image,
    )

    if building_shadow[key]:
        for mask_idx in building_shadow[key]:
            blank = masks[mask_idx][:, :, np.newaxis]
            masked_image = np.where(
                np.repeat(blank, 3, axis=2),
                np.asarray(colors[1], dtype='uint8'),
                masked_image,
            )
    masked_image = masked_image.astype(np.uint8)

    return cv2.addWeighted(image, alpha, masked_image, 1 - alpha, 0)


# import matplotlib.pyplot as plt
# from scipy.ndimage import rotate
# from shadow_height_estimator import (estimate_building_heights,
#                                         rotate_masks,
#                                         take_indices_shadows,
#                                         attach_heights, 
#                                         buildings_info,
#                                         )

# from coco2masks.coco2masks import coco2masks
# import numpy as np

# dataset_dir = '../shared_data/SatelliteTo3D-Datasets/3d_tools_dataset/'
# annot_file = dataset_dir + 'annotations/instances_default.json'
# images_directory = dataset_dir + 'image_png/'

# SCALE = np.float16(0.1)
# SUN_AZIMUTH_ANGLE = np.uint8(100)
# SUN_ELEVATION_ANGLE = np.uint8(30)
# ROTATE_ANGLE = SUN_AZIMUTH_ANGLE - 180
# THRESHOLD = np.uint8(7)
# BROWN = (np.uint8(128), np.uint8(64), np.uint8(48))
# BLUE = (np.uint8(0), np.uint8(0), np.uint8(255))
# COLORS = np.array([BROWN, BLUE])

# image, masks = coco2masks(coco_annotation_file=annot_file, images_directory=images_directory)

# segment = draw_masks(image[0], masks, COLORS)
# random_segment = draw_random_masks(image[0], masks)

# fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(20,10))

# ax[0].imshow(segment)
# ax[0].set_title('brown: buildings, blue: shadows')
# ax[0].set_axis_off()

# ax[1].imshow(random_segment)
# ax[1].set_title('random colors')
# ax[1].set_axis_off()

# plt.show()