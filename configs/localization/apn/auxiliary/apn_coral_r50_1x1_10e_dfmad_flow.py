custom_imports = dict(imports=['my_models', 'dataloader'], allow_failed_imports=False)
# input configuration
num_classes = 3
clip_len = 1
frame_interval = 1
# model settings
model = dict(
    type='APN',
    backbone=dict(
        type='ResNet',
        pretrained='torchvision://resnet50',
        depth=50,
        norm_eval=False),
    cls_head=dict(
        type='APNHead',
        num_classes=num_classes,
        in_channels=2048,
        output_type='coral',
        loss=dict(type='ApnCORALLoss', uncorrelated_loss='ignore'),
        spatial_type='avg2d',
        clip_len=clip_len))



# dataset settings
dataset_type = 'APNDataset'
data_root_train = 'my_data/dfmad70/rawframes/resized_train'
data_root_val = 'my_data/dfmad70/rawframes/resized_test'
ann_file_train = 'my_data/dfmad70/ann_train.csv'
ann_file_val = 'my_data/dfmad70/ann_test.csv'

img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_bgr=False)

train_pipeline = [
    dict(type='FetchStackedFrames', clip_len=clip_len, frame_interval=frame_interval),
    dict(type='LabelToOrdinal'),
    dict(type='RawFrameDecode'),
    dict(type='Resize', scale=(224, 224), keep_ratio=False),
    dict(type='Flip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs', 'progression_label', 'class_label'], meta_keys=()),
    dict(type='ToTensor', keys=['imgs', 'progression_label', 'class_label']),
]
val_pipeline = [
    dict(type='FetchStackedFrames', clip_len=clip_len, frame_interval=frame_interval),
    dict(type='LabelToOrdinal'),
    dict(type='RawFrameDecode'),
    dict(type='Resize', scale=(224, 224), keep_ratio=False),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs', 'progression_label', 'class_label'], meta_keys=()),
    dict(type='ToTensor', keys=['imgs', 'progression_label', 'class_label']),
]
test_pipeline = [
    dict(type='FetchStackedFrames', clip_len=clip_len, frame_interval=frame_interval),
    dict(type='RawFrameDecode'),
    dict(type='Resize', scale=(224, 224), keep_ratio=False),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs'], meta_keys=()),
    dict(type='ToTensor', keys=['imgs']),
]

data = dict(
    videos_per_gpu=16,
    workers_per_gpu=8,
    train=dict(
        type=dataset_type,
        ann_files=ann_file_train,
        pipeline=train_pipeline,
        data_prefixes=data_root_train),
    val=dict(
        type=dataset_type,
        ann_files=ann_file_val,
        pipeline=val_pipeline,
        data_prefixes=data_root_val),
    test=dict(
        type=dataset_type,
        ann_files=ann_file_val,
        pipeline=test_pipeline,
        data_prefixes=data_root_val,
        untrimmed=True)
)

# optimizer
optimizer = dict(type='Adam', lr=1e-04)  # this lr is used for 2 gpus
optimizer_config = dict(grad_clip=None)

# learning policy
lr_config = dict(policy='fixed')
# lr_config = dict(policy='CosineRestart', restart_weights=[1, 1, 1, 1], periods=[2e04, 5e04, 5e04, 5e04], min_lr=5e-06, by_epoch=False)
total_epochs = 10

# evaluation
evaluation = dict(interval=1, save_best='mae', metrics=['loss', 'mae'], results_component=(
    'losses', 'progressions'), dataset_name='Val')

# others
checkpoint_config = dict(interval=1)
log_config = dict(interval=500, hooks=[dict(type='TensorboardLoggerHook'), dict(type='TextLoggerHook')])

# runtime settings
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = './work_dirs/apn_coral_r50_1x1_10e_dfmad_flow/'
load_from = None
resume_from = None
workflow = [('train', 1)]
output_config = dict(out=f'{work_dir}/results.json')
