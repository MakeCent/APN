num_classes = 20
clip_len = 1
num_clips = 1

model = dict(
    type='APN',
    backbone=dict(
        type='EfficientNet',
        model_name='efficientnet-b7',
        weights_path='checkpoints/efficientnet/adv-efficientnet-b7-4652b6dd.pth',
        advprop=False,
        in_channels=3,
        include_top=False),
    cls_head=dict(
        type='APNHead',
        num_classes=num_classes,
        in_channels=2560,
        output_type='classification',
        loss=dict(type='SORDLoss'),
        spatial_type='avg2d',
        clip_len=clip_len))



# dataset settings
dataset_type = 'APNDataset'
data_root_train = ('my_data/thumos14/rawframes/train', 'my_data/thumos14/rawframes/val')
data_root_val = 'my_data/thumos14/rawframes/test'
ann_file_train = ('my_data/thumos14/ann_train.csv', 'my_data/thumos14/ann_val.csv')
ann_file_val = 'my_data/thumos14/ann_test.csv'

img_norm_cfg = dict(mean=[127.5, 127.5, 127.5], std=[127.5, 127.5, 127.5], to_bgr=False)

train_pipeline = [
    dict(type='FetchStackedFrames', clip_len=clip_len, num_clips=num_clips),
    dict(type='LabelToInt'),
    dict(type='RawFrameDecode'),
    dict(type='Resize', scale=(600, 600), keep_ratio=False),
    dict(type='Flip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs', 'progression_label', 'class_label'], meta_keys=()),
    dict(type='ToTensor', keys=['imgs', 'progression_label', 'class_label']),
]
val_pipeline = [
    dict(type='FetchStackedFrames', clip_len=clip_len, num_clips=num_clips),
    dict(type='LabelToOrdinal'),
    dict(type='RawFrameDecode'),
    dict(type='Resize', scale=(600, 600), keep_ratio=False),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs', 'progression_label', 'class_label'], meta_keys=()),
    dict(type='ToTensor', keys=['imgs', 'progression_label', 'class_label']),
]
test_pipeline = [
    dict(type='FetchStackedFrames', clip_len=clip_len, num_clips=num_clips),
    dict(type='RawFrameDecode'),
    dict(type='Resize', scale=(600, 600), keep_ratio=False),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs', 'progression_label', 'class_label'], meta_keys=()),
    dict(type='ToTensor', keys=['imgs', 'progression_label', 'class_label']),
]

data = dict(
    videos_per_gpu=16,
    workers_per_gpu=8,
    test_dataloader=dict(videos_per_gpu=32, workers_per_gpu=8),
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
# lr_config = dict(policy='step', step=10)
total_epochs = 10

# evaluation
eval_config = dict(metrics=['mae'], output_type='classification', dataset_name='Val')
evaluation = dict(interval=1, save_best='mae', **eval_config)

# others
checkpoint_config = dict(interval=1)
log_config = dict(interval=500, hooks=[dict(type='TensorboardLoggerHook'), dict(type='TextLoggerHook')])

# runtime settings
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = './work_dirs/apn_sord_eff7_1x1x1_10e_thumos14_rgb/'
load_from = None
resume_from = None
workflow = [('train', 1)]
output_config = dict(out=f'{work_dir}/results.json')
