from torchvision import datasets
import PIL.Image as Image
import numpy as np
import cv2
from tqdm import tqdm
import random


def crop_img_to_sidewalk(label_img, img):
    non_side_color = [255, 255, 255]  # transparent

    img_height, img_width = label_img.shape

    img_color = np.zeros((img_height, img_width, 3))
    for row in range(img_height):
        for col in range(img_width):
            label = label_img[row, col]
            img_rgb = img[row, col]

            if label == 1:  # is sidewalk
                img_color[row, col] = img_rgb
            else:
                img_color[row, col] = np.array(non_side_color)

    return img_color


def white_to_transparent(img_path):
    img = Image.open(img_path)
    img = img.convert("RGBA")

    pixdata = img.load()

    width, height = img.size
    for y in range(height):
        for x in range(width):
            if pixdata[x, y] == (255, 255, 255, 255):
                pixdata[x, y] = (255, 255, 255, 0)

    img.save(img_path, "PNG")


def create_sidewalk_segment(outputs, imgs, directory):
    outputs = outputs.data.cpu().numpy()
    pred_label_imgs = np.argmax(outputs, axis=1)  # (shape: (batch_size, img_h, img_w))
    pred_label_imgs = pred_label_imgs.astype(np.uint8)

    for i in tqdm(range(pred_label_imgs.shape[0])):
        pred_label_img = pred_label_imgs[i]  # (shape: (img_h, img_w))
        # img_id = img_ids[i]
        img = imgs[i]  # (shape: (3, img_h, img_w))

        img = img.data.cpu().numpy()
        img = np.transpose(img, (1, 2, 0))  # (shape: (img_h, img_w, 3))
        #img = img*np.array([0.229, 0.224, 0.225])
        #img = img + np.array([0.485, 0.456, 0.406])
        img = img * 255.0
        img = img.astype(np.uint8)

        pred_label_img_color = crop_img_to_sidewalk(pred_label_img, img)

        overlayed_img = pred_label_img_color  # 0.35*img + 0.65*
        overlayed_img = overlayed_img.astype(np.uint8)

        img_name = directory + 'segment_' + str(random.randint(0, 1000000)) + '.png'
        cv2.imwrite(img_name, overlayed_img)  # i was img_id
        white_to_transparent(img_name)


class ImageFolderWithPaths(datasets.ImageFolder):
    """Custom dataset that includes image file paths. Extends
    torchvision.datasets.ImageFolder
    """

    # override the __getitem__ method. this is the method dataloader calls
    def __getitem__(self, index):
        # this is what ImageFolder normally returns
        original_tuple = super(ImageFolderWithPaths, self).__getitem__(index)
        # the image file path
        path = self.imgs[index][0]
        # make a new tuple that includes original and the path
        tuple_with_path = (original_tuple + (path,))
        return tuple_with_path