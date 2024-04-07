import os
import numpy as np
import cv2
from pycocotools.coco import COCO
from typing import Tuple, Dict, List


def load_image(image_info, images_directory):
    return cv2.imread(os.path.join(images_directory, image_info['file_name']))


def load_masks(image_id, coco):
    annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))
    return [coco.annToMask(ann) * ann['category_id'] for ann in annotations]


def coco2masks(coco_annotation_file: str, images_directory: str):
    coco = COCO(coco_annotation_file)

    mask_list = []
    for image_id in coco.getImgIds():
        mask_list.extend(load_masks(image_id, coco))

    return np.array(mask_list)


def load_annotations(image_id, coco):
    
    annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))
    return annotations


def anns_and_images(coco_annotation_file: str, images_directory: str):
    coco = COCO(coco_annotation_file)

    image_list = []
    ann_list = []

    # перебераем id всех изображений в файле coco_annotation_file
    for image_id in coco.getImgIds():
        image_list.append(load_image(coco.loadImgs(image_id)[0], images_directory))
        ann_list.extend(load_annotations(image_id, coco))
        
    return np.array(image_list), np.array(ann_list)



#* Все функции далее созданы для работы с НОВЫМИ аннотациями, в перевернутом изображении
def get_bboxes(anns) -> List[float]:
    bboxes = []

    for ann in anns:
        bboxes.append(ann['bbox']) 
    return bboxes


def attach_bboxes (shadows_points: List[Tuple[float]],
                    building_points: List[Tuple[float]],
                    anns) :
    shadows_dict = {}
    building_dict = {}

    bb = get_bboxes(anns)

    for key in shadows_points.keys():
        shadows_dict[key] = bb[key] 


    for key in building_points.keys():
        building_dict[key] = bb[key] 

    return shadows_dict, building_dict




