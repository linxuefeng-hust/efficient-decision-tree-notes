import numpy as np


class TreeNode(object):
    def __init__(self,
                 name=1,
                 depth=1,
                 feature_dim=None,
                 is_leaf=False):
        self.name = name
        self.depth = depth
        self.feature_dim = feature_dim
        self.is_leaf = is_leaf
        self.num_sample = 0
        self.Grad = 0
        self.Hess = 0
        self.G_left = [0 for _ in range(self.feature_dim)]
        self.H_left = [0 for _ in range(self.feature_dim)]
        self.best_uint8_thresholds = [None for _ in range(self.feature_dim)]
        self.best_thresholds = [None for _ in range(self.feature_dim)]
        self.best_gains = [-np.inf for _ in range(self.feature_dim)]
        # some data fall into this tree node
        # for each feature of these data, which is missing value, and their gradient sum, hessian sum
        self.Grad_missing = [0 for _ in range(self.feature_dim)]
        self.Hess_missing = [0 for _ in range(self.feature_dim)]

        self.is_empty = False

    def reset_Grad_Hess_missing(self):
        self.Grad_missing = [0 for _ in range(self.feature_dim)]
        self.Hess_missing = [0 for _ in range(self.feature_dim)]

    def Grad_add(self, value):
        self.Grad += value

    def Hess_add(self, value):
        self.Hess += value

    def num_sample_add(self, value):
        self.num_sample += value

    def Grad_setter(self, value):
        self.Grad = value

    def Hess_setter(self, value):
        self.Hess = value

    def num_sample_setter(self, value):
        self.num_sample = value

    def get_Gleft_Hleft(self, col, G, H):
        # update G_left,H_left, then return its value
        self.G_left[col] += G
        self.H_left[col] += H
        return self.G_left[col], self.H_left[col]

    def update_best_gain(self, col, uint8_threshold, threshold, gain):
        if gain > self.best_gains[col]:
            self.best_gains[col] = gain
            self.best_thresholds[col] = threshold
            self.best_uint8_thresholds[col] = uint8_threshold

    def get_best_feature_threshold_gain(self):
        best_feature = self.best_gains.index(max(self.best_gains))
        return best_feature, self.best_uint8_thresholds[best_feature], \
               self.best_thresholds[best_feature], self.best_gains[best_feature]

    def internal_node_setter(self, feature, uint8_threshold, threshold, nan_child, left_child, right_child, is_leaf=False):
        """
        :param feature: split feature of the intermediate node
        :param threshold: split threshold of the intermediate node
        :param left_child: left child node
        :param right_child: right child node
        :param nan_child: those missing value sample go to this branch, can be None
        """
        self.split_feature = feature
        self.split_uint8_threshold = uint8_threshold
        self.split_threshold = threshold
        self.nan_child = nan_child
        self.left_child = left_child
        self.right_child = right_child
        self.is_leaf = is_leaf
        self.clean_up()

    def leaf_node_setter(self, leaf_score, is_leaf=True):
        """
        :param leaf_score: prediction score of the leaf node
        """
        self.is_leaf = is_leaf
        self.leaf_score = leaf_score
        self.clean_up()

    def empty_node_setter(self):
        self.is_empty = True
        self.clean_up()

    def clean_up(self):
        # clear not necessary instance attribute and methods
        del self.best_uint8_thresholds, self.best_thresholds, self.best_gains, \
            self.Grad, self.Hess, self.G_left, self.H_left, self.feature_dim


"""
about TreeNode.name, an example:
               1 
      2        3       4
   5  6  7   8 9 10  11 12 13
   
name of the root node is 1, 
its left child's name is 3*root.name-1, 
its right child's name is 3*root.name+1, 
the middle child is nan_child, its name is 3*root.nam
"""