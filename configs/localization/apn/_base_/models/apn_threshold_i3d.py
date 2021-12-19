# model settings
model = dict(
    type='APN',
    backbone=dict(
        type='ResNet3d_sony',
        pretrained='checkpoints/r3d_sony/model_rgb.pth',
        modality='rgb'),
    cls_head=dict(
        type='APNHead',
        num_classes=20,
        in_channels=1024,
        output_type='coral',
        loss=dict(type='ApnCORALLoss', uncorrelated_progs='random'),
        spatial_type='avg3d',
        dropout_ratio=0.5))