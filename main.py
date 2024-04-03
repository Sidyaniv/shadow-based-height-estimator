import matplotlib.pyplot as plt
# from scipy.ndimage import rotate
from src.shadow_height_estimator import (estimate_building_heights,
                                        take_indices_shadows,
                                        attach_heights, 
                                        )
from src.visualization_masks import (draw_masks,
                                    draw_random_masks,
                                    draw_sample_building_shadow,
                                    )
from src.annotations.annotation import ann_and_images
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

# image/s, anns = ann_and_images(coco_annotation_file=annot_file, images_directory=images_directory)
# a = images[0]
# b = anns[0]
# print(a)

from PIL import Image



def get_image_center(image_path) -> Tuple[float, float]:
    image = Image.open(image_path)
    
    width, height = image.size
    
    image.close()
    return (width / 2, height / 2)


def rotate_points(shawdow_points, center, angle):
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                                [np.sin(angle), np.cos(angle)]])

    rotated_points = []
    for point in shawdow_points:  
        dx = point[0] - center[0]
        dy = point[1] - center[1]

        # Создаем матрицу поворота
        
        # Применяем матрицу поворота к разности координат
        rotated_dx, rotated_dy = np.dot(rotation_matrix, [dx, dy])

        # Добавляем результат к координатам центра поворота
        new_x = center[0] + rotated_dx
        new_y = center[1] + rotated_dy
        new_point = (new_x, new_y)

        rotated_points.append(new_point)
        
    return rotated_points



center = get_image_center(image_directory)
print(center)

# from scipy import ndimage, datasets
# import matplotlib.pyplot as plt
# fig = plt.figure(figsize=(10, 3))
# ax1, ax2, ax3 = fig.subplots(1, 3)
# img = images[0]
# img_45 = ndimage.rotate(img, 45, reshape=False)
# ax1.imshow(img, cmap='gray')
# ax1.set_axis_off()
# ax2.imshow(img_45, cmap='gray')
# ax2.set_axis_off()
# # ax3.imshow(full_img_45, cmap='gray')
# ax3.set_axis_off()
# fig.set_layout_engine('tight')
# plt.show()
