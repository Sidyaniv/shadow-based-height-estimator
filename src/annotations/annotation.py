import os
import numpy as np
import cv2
from pycocotools.coco import COCO


def load_image(image_info: str, images_directory: str):
    return cv2.imread(os.path.join(images_directory, image_info['file_name']))


def load_annotations(image_id, coco):

    annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))
    return annotations


def anns_and_images(coco_annotation_file: str, images_directory: str):
    coco = COCO(coco_annotation_file)

    image_list = []
    ann_list = []

    for image_id in coco.getImgIds():
        image_list.append(load_image(coco.loadImgs(image_id)[0], images_directory))
        ann_list.extend(load_annotations(image_id, coco))

    return np.array(image_list), np.array(ann_list)
