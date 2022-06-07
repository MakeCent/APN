from abc import ABCMeta

import torch
import torch.nn as nn
from mmaction.models.heads.base import AvgConsensus

from mmcv.cnn import kaiming_init, normal_init, constant_init
from mmaction.models.builder import HEADS, build_loss
from mmdet.models.builder import build_loss as mmdet_build_loss


# class BiasLayer(nn.Module, metaclass=ABCMeta):
#     def __init__(self, input_channel, num_bias):
#         super(BiasLayer, self).__init__()
#         self.input_channel = input_channel
#         self.num_bias = num_bias
#
#         self.bias = nn.Parameter(torch.zeros(input_channel, num_bias).float(), requires_grad=True)
#
#     def forward(self, x):
#         return x.unsqueeze(-1).repeat_interleave(self.num_bias, dim=-1) + self.bias


@HEADS.register_module()
class APNHead(nn.Module, metaclass=ABCMeta):
    """Regression head for APN.

    Args:
        num_stages (int): Number of stages to be predicted.
        in_channels (int): Number of channels in input feature.
        loss (dict): Config for building loss.
            Default: dict(type='CrossEntropyLoss')
        spatial_type (str): Pooling type in spatial dimension. Default: 'avg'.
        dropout_ratio (float): Probability of dropout layer. Default: 0.5.
        kwargs (dict, optional): Any keyword argument to be used to initialize
            the head.
    """

    def __init__(self,
                 num_classes=20,
                 num_stages=100,
                 in_channels=2048,
                 hid_channels=256,
                 loss_cls=dict(type='FocalLoss', gamma=2.0, alpha=0.25),
                 loss_reg=dict(type='BCELossWithLogits'),
                 dropout_ratio=0.5):
        super().__init__()

        self.num_classes = num_classes
        self.in_channels = in_channels
        self.hid_channels = hid_channels
        self.loss_cls = mmdet_build_loss(loss_cls)
        self.loss_reg = build_loss(loss_reg)
        self.num_stages = num_stages
        self.dropout_ratio = dropout_ratio

        self.avg_pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        if self.dropout_ratio > 0:
            self.dropout = nn.Dropout(p=self.dropout_ratio)
        else:
            self.dropout = nn.Identity()

        self.cls_fc = nn.Linear(self.in_channels, self.num_classes)

        self.coral_fc = nn.Linear(self.in_channels, 1, bias=False)
        self.coral_bias = nn.Parameter(torch.zeros(1, self.num_stages), requires_grad=True)

    def init_weights(self):
        kaiming_init(self.cls_fc, a=0, nonlinearity='relu', distribution='uniform')
        kaiming_init(self.coral_fc, a=0, nonlinearity='relu', distribution='uniform')
        constant_init(self.coral_bias, 0)

    def forward(self, x):
        x = self.avg_pool(x)
        x = x.view(x.shape[0], -1)
        x = self.dropout(x)
        cls_score = self.cls_fc(x)
        reg_score = self.coral_fc(x) + self.coral_bias
        return cls_score, reg_score
