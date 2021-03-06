# -*- coding: utf-8 -*-

import os
import util
import tensorflow as tf

MODEL_URL = "http://download.tensorflow.org/models/vgg_16_2016_08_28.tar.gz"
VGG_MEAN = [123.68, 116.779, 103.939]


def _vgg_conv2d(inputs, filters):
    n_kernels = inputs.get_shape()[3].value
    w = tf.get_variable("weights", [3, 3, n_kernels, filters], tf.float32, tf.random_normal_initializer())
    b = tf.get_variable("biases", [filters], tf.float32, tf.zeros_initializer())
    h = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(inputs, w, strides=[1, 1, 1, 1], padding="SAME"), b))
    return h, w, b


class Vgg16:

    def __init__(self, img_tensor, reuse=False):
        self.saver = None
        self._build_graph(img_tensor, reuse)

    def _build_graph(self, img_tensor, reuse):
        # Convolution layers 1
        with tf.variable_scope("conv1", reuse=reuse):
            with tf.variable_scope("conv1_1"):
                self.h_conv1_1, self.w_conv1_1, self.b_conv1_1 = _vgg_conv2d(img_tensor, filters=64)
            with tf.variable_scope("conv1_2"):
                self.h_conv1_2, self.w_conv1_2, self.b_conv1_2 = _vgg_conv2d(self.h_conv1_1, filters=64)
        # Pooling 1
        pool1 = tf.nn.max_pool(self.h_conv1_2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME", name="pool1")
        # Convolution layers 2
        with tf.variable_scope("conv2", reuse=reuse):
            with tf.variable_scope("conv2_1"):
                self.h_conv2_1, self.w_conv2_1, self.b_conv2_1 = _vgg_conv2d(pool1, filters=128)
            with tf.variable_scope("conv2_2"):
                self.h_conv2_2, self.w_conv2_2, self.b_conv2_2 = _vgg_conv2d(self.h_conv2_1, filters=128)
        # Pooling 2
        pool2 = tf.nn.max_pool(self.h_conv2_2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME", name="pool2")
        # Convolution layers 3
        with tf.variable_scope("conv3", reuse=reuse):
            with tf.variable_scope("conv3_1"):
                self.h_conv3_1, self.w_conv3_1, self.b_conv3_1 = _vgg_conv2d(pool2, filters=256)
            with tf.variable_scope("conv3_2"):
                self.h_conv3_2, self.w_conv3_2, self.b_conv3_2 = _vgg_conv2d(self.h_conv3_1, filters=256)
            with tf.variable_scope("conv3_3"):
                self.h_conv3_3, self.w_conv3_3, self.b_conv3_3 = _vgg_conv2d(self.h_conv3_2, filters=256)
        # Pooling 3
        pool3 = tf.nn.max_pool(self.h_conv3_3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME", name="pool3")
        # Convolution 4
        with tf.variable_scope("conv4", reuse=reuse):
            with tf.variable_scope("conv4_1"):
                self.h_conv4_1, self.w_conv4_1, self.b_conv4_1 = _vgg_conv2d(pool3, filters=512)
            with tf.variable_scope("conv4_2"):
                self.h_conv4_2, self.w_conv4_2, self.b_conv4_2 = _vgg_conv2d(self.h_conv4_1, filters=512)
            with tf.variable_scope("conv4_3"):
                self.h_conv4_3, self.w_conv4_3, self.b_conv4_3 = _vgg_conv2d(self.h_conv4_2, filters=512)
        # Pooling 4
        pool4 = tf.nn.max_pool(self.h_conv4_3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME", name="pool4")
        # Convolution 5
        with tf.variable_scope("conv5", reuse=reuse):
            with tf.variable_scope("conv5_1"):
                self.h_conv5_1, self.w_conv5_1, self.b_conv5_1 = _vgg_conv2d(pool4, filters=512)
            with tf.variable_scope("conv5_2"):
                self.h_conv5_2, self.w_conv5_2, self.b_conv5_2 = _vgg_conv2d(self.h_conv5_1, filters=512)
            with tf.variable_scope("conv5_3"):
                self.h_conv5_3, self.w_conv5_3, self.b_conv5_3 = _vgg_conv2d(self.h_conv5_2, filters=512)
        # Pooling 5
        pool5 = tf.nn.max_pool(self.h_conv5_3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME", name="pool5")
        # Fully connected 6
        with tf.variable_scope("fc6", reuse=reuse):
            self.w_fc6 = tf.get_variable("weights", [7, 7, 512, 4096], tf.float32, tf.random_normal_initializer())
            self.b_fc6 = tf.get_variable("biases", [4096], tf.float32, tf.zeros_initializer())
            self.h_fc6 = tf.nn.relu(
                tf.nn.bias_add(tf.nn.conv2d(pool5, self.w_fc6, strides=[1, 1, 1, 1], padding="VALID"), self.b_fc6)
            )
        # Fully connected 7
        with tf.variable_scope("fc7", reuse=reuse):
            self.w_fc7 = tf.get_variable("weights", [1, 1, 4096, 4096], tf.float32, tf.random_normal_initializer())
            self.b_fc7 = tf.get_variable("biases", [4096], tf.float32, tf.zeros_initializer())
            self.h_fc7 = tf.nn.relu(
                tf.nn.bias_add(tf.nn.conv2d(self.h_fc6, self.w_fc7, strides=[1, 1, 1, 1], padding="SAME"), self.b_fc7)
            )
        # Fully connected 8
        with tf.variable_scope("fc8", reuse=reuse):
            self.w_fc8 = tf.get_variable("weights", [1, 1, 4096, 1000], tf.float32, tf.random_normal_initializer())
            self.b_fc8 = tf.get_variable("biases", [1000], tf.float32, tf.zeros_initializer())
            self.h_fc8 = tf.nn.bias_add(
                tf.nn.conv2d(self.h_fc7, self.w_fc8, strides=[1, 1, 1, 1], padding="SAME"), self.b_fc8
            )
        with tf.variable_scope("prob"):
            self.logits = self.h_fc8

    def restore_pretrained_variables(self, session):
        # Create saver
        if not self.saver:
            self.saver = tf.train.Saver(
                var_list={
                    "vgg_16/conv1/conv1_1/weights": self.w_conv1_1,
                    "vgg_16/conv1/conv1_1/biases": self.b_conv1_1,
                    "vgg_16/conv1/conv1_2/weights": self.w_conv1_2,
                    "vgg_16/conv1/conv1_2/biases": self.b_conv1_2,
                    "vgg_16/conv2/conv2_1/weights": self.w_conv2_1,
                    "vgg_16/conv2/conv2_1/biases": self.b_conv2_1,
                    "vgg_16/conv2/conv2_2/weights": self.w_conv2_2,
                    "vgg_16/conv2/conv2_2/biases": self.b_conv2_2,
                    "vgg_16/conv3/conv3_1/weights": self.w_conv3_1,
                    "vgg_16/conv3/conv3_1/biases": self.b_conv3_1,
                    "vgg_16/conv3/conv3_2/weights": self.w_conv3_2,
                    "vgg_16/conv3/conv3_2/biases": self.b_conv3_2,
                    "vgg_16/conv3/conv3_3/weights": self.w_conv3_3,
                    "vgg_16/conv3/conv3_3/biases": self.b_conv3_3,
                    "vgg_16/conv4/conv4_1/weights": self.w_conv4_1,
                    "vgg_16/conv4/conv4_1/biases": self.b_conv4_1,
                    "vgg_16/conv4/conv4_2/weights": self.w_conv4_2,
                    "vgg_16/conv4/conv4_2/biases": self.b_conv4_2,
                    "vgg_16/conv4/conv4_3/weights": self.w_conv4_3,
                    "vgg_16/conv4/conv4_3/biases": self.b_conv4_3,
                    "vgg_16/conv5/conv5_1/weights": self.w_conv5_1,
                    "vgg_16/conv5/conv5_1/biases": self.b_conv5_1,
                    "vgg_16/conv5/conv5_2/weights": self.w_conv5_2,
                    "vgg_16/conv5/conv5_2/biases": self.b_conv5_2,
                    "vgg_16/conv5/conv5_3/weights": self.w_conv5_3,
                    "vgg_16/conv5/conv5_3/biases": self.b_conv5_3,
                    "vgg_16/fc6/weights": self.w_fc6,
                    "vgg_16/fc6/biases": self.b_fc6,
                    "vgg_16/fc7/weights": self.w_fc7,
                    "vgg_16/fc7/biases": self.b_fc7,
                    "vgg_16/fc8/weights": self.w_fc8,
                    "vgg_16/fc8/biases": self.b_fc8,
                }
            )
        # Download weights
        save_dir = os.path.join(os.environ["HOME"], ".tfmodel", "vgg16")
        util.maybe_download_and_extract(dest_directory=save_dir, data_url=MODEL_URL)
        checkpoint_path = os.path.join(save_dir, "vgg_16.ckpt")
        self.saver.restore(session, checkpoint_path)
