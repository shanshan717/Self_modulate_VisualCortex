# Self-modulate-VisualCortex

行为实验程序

20250303
- [x] 测试阶段的实验程序暂时还不知道如何写
- [x] 做了实验刺激
- [x] 阅读一下文章

20250305
- [x] 收集数据的时候，被试信息放在前面，subject id、block、然后是stage，fixation、stim、ITI、nonword、condition、rt、subject response、real response、correct、frame rate、date
- [x] self和other的位置试次间平衡、中间增加注视点、左右顺序各一半，平衡
- [x] 学习阶段的测试要变化，比如说做对5次才可以，避免随机蒙对的，比如120个试次，失败了就+1个试次，成功了就-1个试次。
- [x] 噪音背景暗一点
- [x] 正式测试阶段的正确率每次的最低要求是70%

20250308

- [x] 反应时间的记录代码有问题，需要修改
> 统一修改为一种记录时间戳的方式，都统一用core.getTime()来记录。