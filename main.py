import matplotlib.pyplot as plt
from scipy.ndimage import rotate
from src.shadow_height_estimator import (
                                        attach_heights, 
                                        )
from src.visualization_masks import (draw_masks,
                                    draw_random_masks,
                                    draw_sample_building_shadow,
                                    )
from src.annotations.annotation import (ann_and_images,
                                        coco2masks)
import numpy as np

from typing import Tuple, Dict

dataset_dir = '../shared_data/SatelliteTo3D-Datasets/3d_tools_dataset/'
annot_file = dataset_dir + 'annotations/instances_default.json'
images_directory = dataset_dir + 'image_png/'
image_directory = dataset_dir + 'image_png/test_1.png'


SCALE = np.float16(0.1)
SUN_AZIMUTH_ANGLE = np.uint8(100)
SUN_ELEVATION_ANGLE = np.uint8(30)
ROTATE_ANGLE = SUN_AZIMUTH_ANGLE - 180
THRESHOLD = np.uint8(7)
BROWN = (np.uint8(128), np.uint8(64), np.uint8(48))
BLUE = (np.uint8(0), np.uint8(0), np.uint8(255))
COLORS = np.array([BROWN, BLUE])


image, masks = coco2masks(coco_annotation_file=annot_file, images_directory=images_directory)

# random_segment = draw_random_masks(image[0], masks)
segment = draw_masks(image[0], masks, COLORS)

# from PIL import Image




# # from scipy import ndimage, datasets
# # import matplotlib.pyplot as plt
# # fig = plt.figure(figsize=(10, 3))
# # ax1, ax2, ax3 = fig.subplots(1, 3)
# # img = images[0]
# # img_45 = ndimage.rotate(img, 45, reshape=False)
# # ax1.imshow(img, cmap='gray')
# # ax1.set_axis_off()
# # ax2.imshow(img_45, cmap='gray')
# # ax2.set_axis_off()
# # # ax3.imshow(full_img_45, cmap='gray')
# # ax3.set_axis_off()
# # fig.set_layout_engine('tight')
# # plt.show()

