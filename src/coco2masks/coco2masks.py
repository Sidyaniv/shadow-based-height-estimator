import os
import numpy as np
from pycocotools.coco import COCO
import cv2


def load_image(image_info, images_directory):
    return cv2.imread(os.path.join(images_directory, image_info['file_name']))


def load_masks(image_id, coco):
# def load_annotations(image_id, coco):
    
    annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))
    # return [coco.annToMask(ann) * ann['category_id'] for ann in annotations]
    return annotations


def coco2masks(coco_annotation_file: str, images_directory: str):
    coco = COCO(coco_annotation_file)
    print(coco)

    image_list = []
    mask_list = []

    # перебераем id всех изображений в файле coco_annotation_file
    for image_id in coco.getImgIds():
        # добавляем в image_list прочитанные изображения  
        image_list.append(load_image(coco.loadImgs(image_id)[0], images_directory))
        # добавляем в конец mask_list список загруженных масок  
        mask_list.extend(load_masks(image_id, coco))

    return np.array(image_list), np.array(mask_list)

dataset_dir = '../shared_data/SatelliteTo3D-Datasets/3d_tools_dataset/'
annot_file = dataset_dir + 'annotations/instances_default.json'
images_directory = dataset_dir + 'image_png/'

coco = COCO(annot_file)

image_list = []
ann_list = []
# print(coco.getImgIds())
# for image_id in coco.getImgIds():
#     print(image_id)

for image_id in coco.getImgIds():

    image_list.append(load_image(coco.loadImgs(image_id)[0], images_directory))
    ann_list.extend(load_masks(image_id, coco))
# print(image_list)
# print(ann_list)
print (ann_list[0])

# images, masks = coco2masks(coco_annotation_file=annot_file, images_directory=images_directory)
# print(images)
# print(masks)


# import matplotlib.pyplot as plt
# from scipy.ndimage import rotate
# from src.shadow_height_estimator import (estimate_building_heights,
#                                         rotate_masks,
#                                         take_indices_shadows,
#                                         attach_heights, 
#                                         buildings_info,
#                                         )
# from src.visualization_masks import (draw_masks,
#                                     draw_random_masks,
#                                     draw_sample_building_shadow,
#                                     )
# from src.coco2masks.coco2masks import coco2masks



# import numpy as np

# dataset_dir = '../shared_data/SatelliteTo3D-Datasets/3d_tools_dataset/'
# annot_file = dataset_dir + 'annotations/instances_default.json'
# images_directory = dataset_dir + 'image_png/'

# image, masks = coco2masks(coco_annotation_file=annot_file, images_directory=images_directory)
# print(image)