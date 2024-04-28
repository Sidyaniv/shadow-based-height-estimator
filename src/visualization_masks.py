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
        masked_image = np.where(
            np.repeat(mask[:, :, np.newaxis], 3, axis=2),
            np.asarray(colors[label], dtype='uint8'),
            masked_image,
        )
        masked_image = masked_image.astype(np.uint8)
        image = image.astype(np.uint8)
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
        image = image.astype(np.uint8)
    return cv2.addWeighted(image, alpha, masked_image, 1 - alpha, 0)


def draw_sample_building_shadow(image, masks, building_shadow, colors):
    masked_image = image.copy()
    alpha = 0.3
    key = random.choice(list(building_shadow.keys()))  # noqa: S311
    blank = masks[key][:, :, np.newaxis]

    masked_image = np.where(
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


def draw_heigths_map(image, masks, heigths):
    masked_image = np.zeros([2516,4663,3])
    BLACK = (np.uint8(0), np.uint8(0), np.uint8(0))

    iterations = []
    for iter, _ in heigths.items():
        iterations.append(iter)

    for index, mask in enumerate(masks):
        if 1 in mask:
            label = 0
            if index in heigths.keys():
                heigth = heigths[index]['heigths']
                if heigth < 8.5:
                    red = (np.uint8(30 * heigth), np.uint8(0), np.uint8(0)) 
                elif heigth < 17:
                    red = (np.uint8(255), np.uint8(15 * heigth), np.uint8(0))
                elif heigth < 25.5:
                    red = (np.uint8(255), np.uint8(255), np.uint8(56.66 * heigth))
                # red = (np.uint8(8.5 * heigth), np.uint8(0), np.uint8(0)) 
        else:
            label = 1
            red = (np.uint8(0), np.uint8(0), np.uint8(0))
        colors = [red, BLACK]

        masked_image = np.where(
            np.repeat(mask[:, :, np.newaxis], 3, axis=2),
            np.asarray(colors[label], dtype='uint8'),
            masked_image,
        )
        masked_image = masked_image.astype(np.uint8)
    return masked_image