import os
import numpy as np
from pycocotools.coco import COCO
import cv2

def load_image(image_info, images_directory):
    return cv2.imread(os.path.join(images_directory, image_info['file_name']))


def load_masks(image_id, coco):
    annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))
    return [coco.annToMask(ann) * ann['category_id'] for ann in annotations]


def coco2masks(coco_annotation_file: str, images_directory: str):
    coco = COCO(coco_annotation_file)

    image_list = []
    mask_list = []
    for image_id in coco.getImgIds():
        image_list.append(load_image(coco.loadImgs(image_id)[0], images_directory))
        mask_list.extend(load_masks(image_id, coco))

    return np.array(image_list), np.array(mask_list)
