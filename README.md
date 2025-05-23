# Self-modulate-VisualCortex

## Folder structure

```
.
├── Output
│   ├── 1_Exp_materials
│   │   ├── 1_Exp_stimuli
│   │   │   ├── AIUVS.png
│   │   │   ├── ...
│   │   │   └── YPNSF.png
│   │   └── 1_Exp_visual_noise
│   │       ├── inverted_noise_1.png
│   │       ├── ...
│   │       └── noise_5.png
│   └── 2_Exp_behav_data
│       └── Exp1_task1_001.csv
├── README.md
└── Scripts
    ├── Exp_behav.py
    ├── Exp_nonwords.py
    └── Exp_visual_noise.py
```

<details>

<summary>行为实验程序的todo list</summary>

##### 20250522
1. 注视点需要一直呈现
2. 6次run改为4次run，一次条件重复5-6次
3. 一个block结束之后给一个线索，滴一声，避免视觉上的干扰，所以采用声音刺激

##### 20250313
- [ ] 学习阶段注视点不消失，刺激和注视点都要呈现
- [ ] 噪音改为（128，50）
- [ ] 取最后3个block的正确率，每个在90%以上
- [ ] 注视点半径缩小一点
- [ ] 分条件（self、other）画折线图，复合折线图
- [ ] 核对数据
  
##### 20250312
- [x] 噪音背景改为均值128,多尝试一些不同的标准差（目前采用的是128，30）
- [x] 在12个block中，60个trial，要保证每个刺激都有呈现5次
- [x] ITI 间隔改为0.5s～1.5s
- [x] 根据视距调整非词大小
- [x] 学习阶段的测试由至少做对5次，改为做对6/7次，正式测试阶段的block数不变
- [x] 鼠标隐藏
- [x] 学习阶段的注视点不要，非词刺激的注视点不要；
- [x] 测试阶段中非词刺激的注视点不要，但是fixation时的注视点要
- [x] 对正确率和反应时做简单的数据分析

##### 20250308
- [x] 反应时间的记录代码有问题，需要修改
> 统一修改为一种记录时间戳的方式，都统一用core.getTime()来记录。

##### 20250305
- [x] 收集数据的时候，被试信息放在前面，subject id、block、然后是stage，fixation、stim、ITI、nonword、condition、rt、subject response、real response、correct、frame rate、date
- [x] self和other的位置试次间平衡、中间增加注视点、左右顺序各一半，平衡
- [x] 学习阶段的测试要变化，比如说做对5次才可以，避免随机蒙对的，比如120个试次，失败了就+1个试次，成功了就-1个试次。
- [x] 噪音背景暗一点
- [x] 正式测试阶段的正确率每次的最低要求是70%

##### 20250303
- [x] 测试阶段的实验程序暂时还不知道如何写
- [x] 做了实验刺激
- [x] 阅读一下文章
  
  
</details>


