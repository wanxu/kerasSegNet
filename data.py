# coding:utf-8
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import numpy as np
import os
import glob

import cv2


# from libtiff import TIFF

class myAugmentation(object):
    """
    A class used to augmentate image
    Firstly, read train image and label seperately, and then merge them together for the next process
    Secondly, use keras preprocessing to augmentate image
    Finally, seperate augmentated image apart into train image and label
    """

    def __init__(self, train_path="train", label_path="label", merge_path="merge", aug_merge_path="aug_merge",
                 aug_train_path="aug_train", aug_label_path="aug_label", train_img_type="jpg", label_img_type="png"):

        """
        Using glob to get all .img_type form path
        """

        self.train_imgs = glob.glob(train_path + "/*." + train_img_type)
        self.label_imgs = glob.glob(label_path + "/*." + label_img_type)
        self.train_path = train_path
        self.label_path = label_path
        self.merge_path = merge_path
        if not os.path.lexists(merge_path):
            os.mkdir(merge_path)
        self.train_img_type = train_img_type
        self.label_img_type = label_img_type
        self.aug_merge_path = aug_merge_path
        if not os.path.lexists(aug_merge_path):
            os.mkdir(aug_merge_path)
        self.aug_train_path = aug_train_path
        if not os.path.lexists(aug_train_path):
            os.mkdir(aug_train_path)
        self.aug_label_path = aug_label_path
        if not os.path.lexists(aug_label_path):
            os.mkdir(aug_label_path)
        self.slices = len(self.train_imgs)
        self.datagen = ImageDataGenerator(
            rotation_range=0.2,
            width_shift_range=0.05,
            height_shift_range=0.05,
            shear_range=0.05,
            zoom_range=0.05,
            horizontal_flip=True,
            fill_mode='nearest')

    def Augmentation(self):

        """
        Start augmentation.....
        """
        trains = self.train_imgs
        labels = self.label_imgs
        path_train = self.train_path
        path_label = self.label_path
        path_merge = self.merge_path
        train_img_type = self.train_img_type
        label_img_type = self.label_img_type
        path_aug_merge = self.aug_merge_path
        if len(trains) != len(labels) or len(trains) == 0 or len(trains) == 0:
            print("trains can't match labels")
            return 0
        for i in range(len(trains)):
            #
            img_t = load_img(path_train + "/" + str(i) + "." + train_img_type)
            img_l = load_img(path_label + "/" + str(i) + "." + label_img_type)
            x_t = img_to_array(img_t)
            x_l = img_to_array(img_l)
            # GBR 转为 RGB
            x_t[:, :, 2] = x_l[:, :, 0]
            img_tmp = array_to_img(x_t)
            img_tmp.save(path_merge + "/" + str(i) + "." + label_img_type)
            img = x_t
            img = img.reshape((1,) + img.shape)
            savedir = path_aug_merge + "/" + str(i)
            if not os.path.lexists(savedir):
                os.mkdir(savedir)
            self.doAugmentate(img, savedir, str(i), 1, label_img_type, 30)

    def doAugmentate(self, img, save_to_dir, save_prefix, batch_size=1, save_format='png', imgnum=30):

        """
        augmentate one image
        """
        datagen = self.datagen
        i = 0
        for batch in datagen.flow(img,
                                  batch_size=batch_size,
                                  save_to_dir=save_to_dir,
                                  save_prefix=save_prefix,
                                  save_format=save_format):
            i += 1
            if i >= imgnum:
                break

    def splitMerge(self):

        """
        split merged image apart
        """
        path_merge = self.aug_merge_path
        path_train = self.aug_train_path
        path_label = self.aug_label_path
        for i in range(self.slices):
            path = path_merge + "/" + str(i)
            train_imgs = glob.glob(path + "/*." + self.label_img_type)
            savedir = path_train + "/" + str(i)
            if not os.path.lexists(savedir):
                os.mkdir(savedir)
            savedir = path_label + "/" + str(i)
            if not os.path.lexists(savedir):
                os.mkdir(savedir)
            for imgname in train_imgs:
                midname = imgname[imgname.rindex("/") + 1:imgname.rindex("." + self.label_img_type)]
                img = cv2.imread(imgname)
                img_train = img[:, :, 2]  # cv2 read image rgb->bgr
                img_label = img[:, :, 0]
                cv2.imwrite(path_train + "/" + str(i) + "/" + midname + "_train" + "." + self.label_img_type, img_train)
                cv2.imwrite(path_label + "/" + str(i) + "/" + midname + "_label" + "." + self.label_img_type, img_label)

    def splitTransform(self):

        """
        split perspective transform images
        """
        # path_merge = "transform"
        # path_train = "transform/data/"
        # path_label = "transform/label/"
        # path_merge = "deform/deform_norm2"
        # path_train = "deform/train/"
        # path_label = "deform/label/"
        path_merge = "./data/640_480/train/aug_merge"
        path_train = "./data/640_480/train/deform/train/"
        path_label = "./data/640_480/train/deform/label/"
        if not os.path.lexists(path_train):
            os.makedirs(path_train)
        if not os.path.lexists(path_label):
            os.makedirs(path_label)
        train_imgs = []
        dirs = os.listdir(path_merge)
        for i in range(len(dirs)):
            train_imgs.extend(glob.glob(path_merge + "/" + str(i) + "/*." + self.label_img_type))
        for imgname in train_imgs:
            imgname = imgname.replace("\\", "/")
            midname = imgname[imgname.rindex("/") + 1:imgname.rindex("." + self.label_img_type)]
            img = cv2.imread(imgname)
            img_train = img[:, :, 2]  # cv2 read image rgb->bgr
            img_label = img[:, :, 0]
            cv2.imwrite(path_train + midname + "." + self.label_img_type, img_train)
            cv2.imwrite(path_label + midname + "." + self.label_img_type, img_label)


class dataProcess(object):
    def __init__(self, out_rows, out_cols, data_path="./data/640_480/train/deform/train",
                 label_path="./data/640_480/train/deform/label",
                 test_path="./data/640_480/test/image", npy_path="./npydata", img_type="png"):

        """

        """

        self.out_rows = out_rows
        self.out_cols = out_cols
        self.data_path = data_path
        self.label_path = label_path
        self.img_type = img_type
        self.test_path = test_path
        self.npy_path = npy_path

    def create_train_data(self):
        i = 0
        print('-' * 30)
        print('Creating training images...')
        print('-' * 30)
        imgs = glob.glob(self.data_path + "/*." + self.img_type)
        print(len(imgs))
        imgdatas = np.ndarray((len(imgs), self.out_rows, self.out_cols, 1), dtype=np.uint8)
        imglabels = np.ndarray((len(imgs), self.out_rows, self.out_cols, 1), dtype=np.uint8)
        for imgname in imgs:
            imgname = imgname.replace("\\", "/")
            midname = imgname[imgname.rindex("/") + 1:]
            img = load_img(self.data_path + "/" + midname, grayscale=True)
            label = load_img(self.label_path + "/" + midname, grayscale=True)
            img = img_to_array(img)
            label = img_to_array(label)
            # img = cv2.imread(self.data_path + "/" + midname,cv2.IMREAD_GRAYSCALE)
            # label = cv2.imread(self.label_path + "/" + midname,cv2.IMREAD_GRAYSCALE)
            # img = np.array([img])
            # label = np.array([label])
            imgdatas[i] = img
            imglabels[i] = label
            if i % 100 == 0:
                print('Done: {0}/{1} images'.format(i, len(imgs)))
            i += 1
        print('loading done')
        np.save(self.npy_path + '/imgs_train.npy', imgdatas)
        np.save(self.npy_path + '/imgs_mask_train.npy', imglabels)
        print('Saving to .npy files done.')

    def create_test_data(self):
        i = 0
        print('-' * 30)
        print('Creating test images...')
        print('-' * 30)
        imgs = glob.glob(self.test_path + "/*." + "jpg")
        imgs.extend(glob.glob(self.test_path + "/*." + "png"))
        print(len(imgs))
        imgdatas = np.ndarray((len(imgs), self.out_rows, self.out_cols, 1), dtype=np.uint8)
        for imgname in imgs:
            imgname = imgname.replace("\\", "/")
            midname = imgname[imgname.rindex("/") + 1:]
            img = load_img(self.test_path + "/" + midname, grayscale=True)
            img = img_to_array(img)
            # img = cv2.imread(self.test_path + "/" + midname,cv2.IMREAD_GRAYSCALE)
            # img = np.array([img])
            imgdatas[i] = img
            i += 1
        print('loading done')
        np.save(self.npy_path + '/imgs_test.npy', imgdatas)
        print('Saving to imgs_test.npy files done.')

    def load_train_data(self):
        print('-' * 30)
        print('load train images...')
        print('-' * 30)
        imgs_train = np.load(self.npy_path + "/imgs_train.npy")
        imgs_mask_train = np.load(self.npy_path + "/imgs_mask_train.npy")
        imgs_train = imgs_train.astype('float32')
        imgs_mask_train = imgs_mask_train.astype('float32')
        imgs_train /= 255
        # mean = imgs_train.mean(axis = 0)
        # imgs_train -= mean
        imgs_mask_train /= 255
        imgs_mask_train[imgs_mask_train > 0.5] = 1
        imgs_mask_train[imgs_mask_train <= 0.5] = 0
        return imgs_train, imgs_mask_train

    def load_test_data(self):
        print('-' * 30)
        print('load test images...')
        print('-' * 30)
        imgs_test = np.load(self.npy_path + "/imgs_test.npy")
        imgs_test = imgs_test.astype('float32')
        imgs_test /= 255
        # mean = imgs_test.mean(axis = 0)
        # imgs_test -= mean
        return imgs_test


if __name__ == "__main__":
    aug = myAugmentation(train_path="./data/640_480/train/image"
                         , label_path="./data/640_480/train/label"
                         , merge_path="./data/640_480/train/merge"
                         , aug_merge_path="./data/640_480/train/aug_merge"
                         , aug_train_path="./data/640_480/train/aug_train"
                         , aug_label_path="./data/640_480/train/aug_label"
                         , train_img_type="jpg"
                         , label_img_type="png"
                         )
    # 1 image-->30 augmented images,image/label/images-->merge/images+aug_merge/images
    # aug.Augmentation()
    # aug_merge/images --> aug_train/aug_label/images
    # aug.splitMerge()
    # aug_merge/0 and 1 and .../images-->deform/train and label/images
    # aug.splitTransform()
    # deform/train and label/images-->npy files
    # mydata = dataProcess(512, 512)
    # mydata = dataProcess(224, 224)
    mydata = dataProcess(480, 640)
    mydata.create_train_data()
    mydata.create_test_data()
    # imgs_mask_train means labels
    imgs_train, imgs_mask_train = mydata.load_train_data()
    print(imgs_train.shape, imgs_mask_train.shape)
    imgs_test = mydata.load_test_data()
    print(imgs_test.shape)
