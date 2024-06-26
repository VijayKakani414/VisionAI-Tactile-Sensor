# --------------------------------------------------------------------------
# Tensorflow Implementation of Tacticle Sensor Project
# Licensed under The MIT License [see LICENSE for details]
# Written by Cheng-Bin Jin
# Email: sbkim0407@gmail.com
# Re-used for Vision-based tactile sensor mechanism for the estimation of contact position and force distribution using deep learning
# --------------------------------------------------------------------------
import os
import cv2
import logging
import numpy as np

import utils as utils


class Dataset(object):
    def __init__(self, shape, mode=0, img_format='.png', resize_factor=0.5, is_train=True, log_dir=None, is_debug=False):
        self.shape = shape
        self.mode = mode
        self.img_format = img_format
        self.resize_factor = resize_factor
        self.is_train = is_train
        self.log_dir = log_dir
        self.is_debug = is_debug
        self.top_left = (20, 90)
        self.bottom_right = (390, 575)
        self.binarize_threshold = 20.
        self.input_shape = (int(np.floor(self.resize_factor * (self.bottom_right[0] - self.top_left[0]))),
                            int(np.floor(self.resize_factor * (self.bottom_right[1] - self.top_left[1]))), 2)
        self.train_ratio, self.val_ratio, self.test_ratio = 0.6, 0.2, 0.2

        self.logger = logging.getLogger(__name__)  # logger
        self.logger.setLevel(logging.INFO)
        utils.init_logger(logger=self.logger, log_dir=log_dir, is_train=is_train, name='cls_dataset')

        self._read_img_path()  # read all img paths

        self.print_parameters()
        if self.is_debug:
            self._debug_roi_test()

    def _read_img_path(self):
        self.cls01_left = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_0'),
                                                endswith=self.img_format,
                                                condition='_L_')
        self.cls01_right = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_0'),
                                                 endswith=self.img_format,
                                                 condition='_R_')

        self.cls02_left = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_1'),
                                           endswith=self.img_format,
                                           condition='_L_')
        self.cls02_right = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_1'),
                                           endswith=self.img_format,
                                           condition='_R_')

        self.cls03_left = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_2'),
                                           endswith=self.img_format,
                                           condition='_L_')
        self.cls03_right = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_2'),
                                                 endswith=self.img_format,
                                                 condition='_R_')

        self.cls04_left = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_3'),
                                                endswith=self.img_format,
                                                condition='_L_')
        self.cls04_right = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_3'),
                                                 endswith=self.img_format,
                                                 condition='_R_')

        self.cls05_left = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_4'),
                                                endswith=self.img_format,
                                                condition='_L_')
        self.cls05_right = utils.all_files_under(folder=os.path.join('../data', 'cls_' + self.shape, self.shape + '_4'),
                                                 endswith=self.img_format,
                                                 condition='_R_')

        self._read_train_img_path()     # Read training img paths
        self._read_val_img_path()       # Read val img paths
        self._read_test_img_path()      # Read test img paths

    def _read_train_img_path(self):
        self.train_left_img_paths = list()
        self.train_right_img_paths = list()
        self.train_labels = list()

        left_paths = [self.cls01_left, self.cls02_left, self.cls03_left, self.cls04_left, self.cls05_left]
        right_paths = [self.cls01_right, self.cls02_right, self.cls03_right, self.cls04_right, self.cls05_right]

        for label, (left_path, right_path) in enumerate(zip(left_paths, right_paths)):
            self.train_left_img_paths.extend(left_path[0:int(self.train_ratio * len(left_path))])
            self.train_right_img_paths.extend(right_path[0:int(self.train_ratio * len(right_path))])
            self.train_labels.extend(label * np.ones(int(self.train_ratio * len(left_path)), dtype=np.uint8))

        assert len(self.train_left_img_paths) == len(self.train_right_img_paths)
        self.num_train = len(self.train_left_img_paths)

    def _read_val_img_path(self):
        self.val_left_img_paths = list()
        self.val_right_img_paths = list()
        self.val_labels = list()

        left_paths = [self.cls01_left, self.cls02_left, self.cls03_left, self.cls04_left, self.cls05_left]
        right_paths = [self.cls01_right, self.cls02_right, self.cls03_right, self.cls04_right, self.cls05_right]

        for label, (left_path, right_path) in enumerate(zip(left_paths, right_paths)):
            self.val_left_img_paths.extend(left_path[int(self.train_ratio * len(left_path))
                                                     :int((self.train_ratio + self.val_ratio) * len(left_path))])
            self.val_right_img_paths.extend(right_path[int(self.train_ratio * len(left_path))
                                                       :int((self.train_ratio + self.val_ratio) * len(right_path))])
            self.val_labels.extend(label * np.ones(int(self.val_ratio * len(left_path)), dtype=np.uint8))

        assert len(self.val_left_img_paths) == len(self.val_right_img_paths)
        self.num_val = len(self.val_left_img_paths)

    def _read_test_img_path(self):
        self.test_left_img_paths = list()
        self.test_right_img_paths = list()
        self.test_labels = list()

        left_paths = [self.cls01_left, self.cls02_left, self.cls03_left, self.cls04_left, self.cls05_left]
        right_paths = [self.cls01_right, self.cls02_right, self.cls03_right, self.cls04_right, self.cls05_right]

        for label, (left_path, right_path) in enumerate(zip(left_paths, right_paths)):
            self.test_left_img_paths.extend(left_path[-int(self.test_ratio * len(left_path)):])
            self.test_right_img_paths.extend(right_path[-int(self.test_ratio * len(right_path)):])
            self.test_labels.extend(label * np.ones(int(self.test_ratio * len(left_path)), dtype=np.uint8))

        assert len(self.test_left_img_paths) == len(self.test_right_img_paths)
        self.num_test = len(self.test_left_img_paths)

    def print_parameters(self):
        if self.is_train:
            self.logger.info('\nDataset parameters:')
            self.logger.info('Shape: \t\t\t{}'.format(self.shape))
            self.logger.info('Mode: \t\t\t{}'.format(self.mode))
            self.logger.info('img_format: \t\t\t{}'.format(self.img_format))
            self.logger.info('resize_factor: \t\t{}'.format(self.resize_factor))
            self.logger.info('is_train: \t\t\t{}'.format(self.is_train))
            self.logger.info('is_debug: \t\t\t{}'.format(self.is_debug))
            self.logger.info('top_left: \t\t\t{}'.format(self.top_left))
            self.logger.info('bottom_right: \t\t{}'.format(self.bottom_right))
            self.logger.info('binarize_threshold: \t\t{}'.format(self.binarize_threshold))
            self.logger.info('Num of cls01_left imgs: \t{}'.format(len(self.cls01_left)))
            self.logger.info('Num of cls01_right imgs: \t{}'.format(len(self.cls01_right)))
            self.logger.info('Num of cls02_left imgs: \t{}'.format(len(self.cls02_left)))
            self.logger.info('Num of cls02_right imgs: \t{}'.format(len(self.cls02_right)))
            self.logger.info('Num of cls03_left imgs: \t{}'.format(len(self.cls03_left)))
            self.logger.info('Num of cls03_right imgs: \t{}'.format(len(self.cls03_right)))
            self.logger.info('Num of cls04_left imgs: \t{}'.format(len(self.cls04_left)))
            self.logger.info('Num of cls04_right imgs: \t{}'.format(len(self.cls04_right)))
            self.logger.info('Num of cls05_left imgs: \t{}'.format(len(self.cls05_left)))
            self.logger.info('Num of cls05_right imgs: \t{}'.format(len(self.cls05_right)))
            self.logger.info('Num. of train imgs: \t\t{}'.format(self.num_train))
            self.logger.info('Num. of val imgs: \t\t{}'.format(self.num_val))
            self.logger.info('Numo of test imgs: \t\t{}'.format(self.num_test))
            self.logger.info('input_shape: \t\t{}'.format(self.input_shape))
        else:
            print('Dataset parameters:')
            print('Shape: \t\t\t{}'.format(self.shape))
            print('Mode: \t\t\t{}'.format(self.mode))
            print('img_format: \t\t\t{}'.format(self.img_format))
            print('resize_factor: \t\t{}'.format(self.resize_factor))
            print('is_train: \t\t\t{}'.format(self.is_train))
            print('is_debug: \t\t\t{}'.format(self.is_debug))
            print('top_left: \t\t\t{}'.format(self.top_left))
            print('bottom_right: \t\t{}'.format(self.bottom_right))
            print('binarize_threshold: \t\t{}'.format(self.binarize_threshold))
            print('Num of cls01_left imgs: \t{}'.format(len(self.cls01_left)))
            print('Num of cls01_right imgs: \t{}'.format(len(self.cls01_right)))
            print('Num of cls02_left imgs: \t{}'.format(len(self.cls02_left)))
            print('Num of cls02_right imgs: \t{}'.format(len(self.cls02_right)))
            print('Num of cls03_left imgs: \t{}'.format(len(self.cls03_left)))
            print('Num of cls03_right imgs: \t{}'.format(len(self.cls03_right)))
            print('Num of cls04_left imgs: \t{}'.format(len(self.cls04_left)))
            print('Num of cls04_right imgs: \t{}'.format(len(self.cls04_right)))
            print('Num of cls05_left imgs: \t{}'.format(len(self.cls05_left)))
            print('Num of cls05_right imgs: \t{}'.format(len(self.cls05_right)))
            print('Num. of train imgs: \t\t{}'.format(self.num_train))
            print('Num. of val imgs: \t\t{}'.format(self.num_val))
            print('Numo of test imgs: \t\t{}'.format(self.num_test))
            print('input_shape: \t\t{}'.format(self.input_shape))

    def _debug_roi_test(self, batch_size=5, color=(0, 0, 255), thickness=2, save_folder='../debug'):
        if not os.path.isdir(save_folder):
            os.makedirs(save_folder)

        indexes = np.random.random_integers(low=0, high=self.num_train, size=batch_size)

        left_img_paths = [self.train_left_img_paths[index] for index in indexes]
        right_img_paths = [self.train_right_img_paths[index] for index in indexes]

        for left_path, right_path in zip(left_img_paths, right_img_paths):
            left_img = cv2.imread(left_path)
            right_img = cv2.imread(right_path)

            # Draw roi
            left_img_roi = cv2.rectangle(left_img.copy(), (self.top_left[1], self.top_left[0]),
                                         (self.bottom_right[1], self.bottom_right[0]), color=color, thickness=thickness)
            right_img_roi = cv2.rectangle(right_img.copy(), (self.top_left[1], self.top_left[0]),
                                          (self.bottom_right[1], self.bottom_right[0]), color=color, thickness=thickness)

            # Cropping
            left_img_crop = left_img[self.top_left[0]:self.bottom_right[0], self.top_left[1]: self.bottom_right[1]]
            right_img_crop = right_img[self.top_left[0]:self.bottom_right[0], self.top_left[1]: self.bottom_right[1]]

            # BGR to Gray
            left_img_gray = cv2.cvtColor(left_img_crop, cv2.COLOR_BGR2GRAY)
            right_img_gray = cv2.cvtColor(right_img_crop, cv2.COLOR_BGR2GRAY)

            # Thresholding
            _, left_img_binary = cv2.threshold(left_img_gray, self.binarize_threshold , 255., cv2.THRESH_BINARY)
            _, right_img_binary = cv2.threshold(right_img_gray, self.binarize_threshold , 255., cv2.THRESH_BINARY)

            # Resize img
            left_img_resize = cv2.resize(left_img_binary , None, fx=self.resize_factor, fy=self.resize_factor,
                                         interpolation=cv2.INTER_NEAREST)
            right_img_resize = cv2.resize(right_img_binary, None, fx=self.resize_factor, fy=self.resize_factor,
                                          interpolation=cv2.INTER_NEAREST)

            roi_canvas = np.hstack([left_img_roi, right_img_roi])
            crop_canvas = np.hstack([left_img_crop, right_img_crop])
            gray_canvas = np.hstack([left_img_gray, right_img_gray])
            binary_canvas = np.hstack([left_img_binary, right_img_binary])
            resize_canvas = np.hstack([left_img_resize, right_img_resize])

            # Save img
            cv2.imwrite(os.path.join(save_folder, 's1_roi_' + os.path.basename(left_path)), roi_canvas)
            cv2.imwrite(os.path.join(save_folder, 's2_crop_' + os.path.basename(left_path)), crop_canvas)
            cv2.imwrite(os.path.join(save_folder, 's3_gray_' + os.path.basename(left_path)), gray_canvas)
            cv2.imwrite(os.path.join(save_folder, 's4_binary_' + os.path.basename(left_path)), binary_canvas)
            cv2.imwrite(os.path.join(save_folder, 's5_resize_' + os.path.basename(left_path)), resize_canvas)

    def train_random_batch(self, batch_size=4):
        # Random select samples
        indexes = np.random.random_integers(low=0, high=self.num_train-1, size=batch_size)
        # Select img paths
        left_img_paths = [self.train_left_img_paths[index] for index in indexes]
        right_img_paths = [self.train_right_img_paths[index] for index in indexes]
        # Read imgs and labels
        batch_imgs = self.data_reader(left_img_paths, right_img_paths)
        batch_labels = np.reshape(np.asarray([self.train_labels[index] for index in indexes]), (-1, 1))

        return batch_imgs, batch_labels

    def direct_batch(self, batch_size, start_index, stage='val'):
        if stage == 'val':
            num_imgs = self.num_val
            left_img_paths = self.val_left_img_paths
            right_img_paths = self.val_right_img_paths
            labels = self.val_labels
        elif stage == 'test':
            num_imgs = self.num_test
            left_img_paths = self.test_left_img_paths
            right_img_paths = self.test_right_img_paths
            labels = self.test_labels
        else:
            raise NotImplementedError

        if start_index + batch_size < num_imgs:
            end_index = start_index + batch_size
        else:
            end_index = num_imgs

        # Select indexes
        indexes = [idx for idx in range(start_index, end_index)]
        # Select img paths
        left_img_paths = [left_img_paths[index] for index in indexes]
        right_img_paths = [right_img_paths[index] for index in indexes]
        # Read imgs and labels
        batch_imgs = self.data_reader(left_img_paths, right_img_paths)
        batch_labels = np.reshape(np.asarray([labels[index] for index in indexes]), (-1, 1))

        return batch_imgs, batch_labels

    def data_reader(self, left_img_paths, right_img_paths):
        batch_size = len(left_img_paths)
        batch_imgs = np.zeros((batch_size, *self.input_shape), dtype=np.float32)

        for i, (left_path, right_path) in enumerate(zip(left_img_paths, right_img_paths)):
            # Process imgs
            left_img = cv2.imread(left_path)
            right_img = cv2.imread(right_path)

            # Stage 1: cropping
            left_img_crop = left_img[self.top_left[0]:self.bottom_right[0], self.top_left[1]: self.bottom_right[1]]
            right_img_crop = right_img[self.top_left[0]:self.bottom_right[0], self.top_left[1]: self.bottom_right[1]]

            # Stage 2: BGR to Gray
            left_img_gray = cv2.cvtColor(left_img_crop, cv2.COLOR_BGR2GRAY)
            right_img_gray = cv2.cvtColor(right_img_crop, cv2.COLOR_BGR2GRAY)

            # Stage 3: Thresholding
            _, left_img_binary = cv2.threshold(left_img_gray, self.binarize_threshold, 255., cv2.THRESH_BINARY)
            _, right_img_binary = cv2.threshold(right_img_gray, self.binarize_threshold, 255., cv2.THRESH_BINARY)

            # Stage 4: Resize img
            left_img_resize = cv2.resize(left_img_binary, None, fx=self.resize_factor, fy=self.resize_factor,
                                         interpolation=cv2.INTER_NEAREST)
            right_img_resize = cv2.resize(right_img_binary, None, fx=self.resize_factor, fy=self.resize_factor,
                                          interpolation=cv2.INTER_NEAREST)

            batch_imgs[i, :] = np.dstack([left_img_resize, right_img_resize])

        return batch_imgs

