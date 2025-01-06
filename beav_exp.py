import os  
import random  
import numpy as np  
from psychopy import visual, core, event, data, logging, gui 


# ---------- 设置相对路径 ----------
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# ---------- 实验信息 ----------
psychopyVersion = '2021.2.3'
expName = 'beav_self_cortex'  
expInfo = {'participant': '', 'session': '001'}
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # 用户点击了取消

# 添加时间戳
expInfo['date'] = data.getDateStr()  
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

# ---------- 创建数据文件路径 ----------
filename = _thisDir + os.sep + u'data/%s_%s' % (expInfo['participant'], expName)

thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='/Volumes/T7/Psychopy/beav_exp.py',
    savePickle=True, saveWideText=True,
    dataFileName=filename)

# 日志设置
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # 控制台输出仅显示警告及以上信息

endExpNow = False 
frameTolerance = 0.001  


# ---------- 窗口设置 ----------
win = visual.Window(
    size=[1920, 1080], fullscr=True, screen=0, 
    winType='pyglet', allowGUI=True, allowStencil=False,
    monitor='testMonitor', color='grey', colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='deg')
win.setMouseVisible(False)


# ---------- 固定注视点 ----------
def fixation():
    """
    绘制复合注视点（黑色外圈 + 白色内圈）
    """
    # 外圈（黑色）
    outer_circle = visual.Circle(win, radius=0.05, edges=8, lineColor="black", fillColor="black")
    # 内圈（白色）
    inner_circle = visual.Circle(win, radius=0.03, edges=8, lineColor="white", fillColor="white")
    outer_circle.draw()
    inner_circle.draw()

# ---------- 非词刺激定义 ----------
nonwords_self = ['NVUSR', 'KJHGF', 'PLKJM', 'ZXCVB', 'QWERT']  # 自我组非词
nonwords_other = ['RTUQW', 'YUIOP', 'ASDFG', 'HJKLZ', 'XCVBN']  # 他人组非词

# 将刺激与标签组合
stimuli = nonwords_self + nonwords_other
labels = ['self'] * len(nonwords_self) + ['other'] * len(nonwords_other)
stimuli_trials = list(zip(stimuli, labels))

# ---------- 噪声生成函数 ----------
def generate_noise(win, width=0.3, opacity=0.8):
    """
    生成视觉噪声
    :param win: 窗口对象
    :param width: 噪声块的大小，相对于屏幕高度
    :param opacity: 噪声的透明度
    """
    noise_texture = np.random.rand(128, 128) * 2 - 1  # 生成随机噪声（范围：-1到1）
    noise_stim = visual.ImageStim(win, image=noise_texture, size=[width, width], opacity=opacity)
    return noise_stim
# 噪声参数
noise_size = 20  # 每个像素方块的大小（像素单位）
grid_size = 30   # 噪声网格的大小（30x30的方块）
opacity = 0.8    # 字母的透明度

# 生成像素化噪声
noise_array = np.random.rand(grid_size, grid_size) * 2 - 1  # 随机生成噪声值（范围：-1到1）
noise_stim = visual.ImageStim(
    win,
    image=noise_array,
    size=(grid_size * noise_size, grid_size * noise_size),  # 噪声图案的大小
    interpolate=False  # 关闭插值，保留像素化效果
)

# ---------- 文本刺激 ----------
stim_text = visual.TextStim(win, text='', font='Arial', height=0.05, color=(1, 1, 1))  # 文本高度设置为0.05屏幕高度

# ---------- 学习阶段 ----------
def learning_phase():
    random.shuffle(stimuli_trials)
    for stim, label in stimuli_trials * 5:  # 每个刺激重复5次
        # 1. 固定注视
        fixation()
        win.flip()
        core.wait(0.5)

        # 2. 显示刺激和标签
        noise = generate_noise(win)
        noise.draw()
        stim_text.text = stim
        stim_text.draw()
        label_text = visual.TextStim(win, text=label.upper(), pos=(0, -0.1), font='Arial', height=0.04, color=(1, 1, 1))
        label_text.draw()
        win.flip()
        core.wait(0.9)

        # 3. 匹配/不匹配提示
        noise.draw()
        stim_text.text = stim
        stim_text.draw()
        label_text.text = label.upper()
        label_text.draw()
        match_prompt = visual.TextStim(win, text="Match or Mismatch? (M/N)", pos=(0, -0.2), font='Arial', height=0.03, color=(1, 1, 1))
        match_prompt.draw()
        win.flip()

        # 4. 记录响应
        keys = event.waitKeys(maxWait=3, keyList=['m', 'n', 'escape'])
        if not keys:  # 超时未响应
            continue
        if 'escape' in keys:  # 提前退出
            core.quit()

# ---------- 测试阶段 ----------
def testing_phase():
    # 生成 40 个测试试次（半匹配，半不匹配）
    test_trials = []
    for stim, label in stimuli_trials:
        match = random.choice([True, False])  # 随机设置匹配与否
        if not match:
            label = 'self' if label == 'other' else 'other'
        test_trials.append((stim, label, match))

    random.shuffle(test_trials)
    correct_responses = 0

    for stim, label, match in test_trials:
        # 1. 固定注视
        fixation()
        win.flip()
        core.wait(0.5)

        # 2. 显示刺激和标签
        noise = generate_noise(win)
        noise.draw()
        stim_text.text = stim
        stim_text.draw()
        label_text = visual.TextStim(win, text=label.upper(), pos=(0, -0.1), font='Arial', height=0.04, color=(1, 1, 1))
        label_text.draw()
        win.flip()
        core.wait(0.9)

        # 3. 匹配/不匹配提示
        noise.draw()
        stim_text.text = stim
        stim_text.draw()
        label_text.text = label.upper()
        label_text.draw()
        win.flip()

        # 4. 记录响应
        keys = event.waitKeys(maxWait=3, keyList=['y', 'n', 'escape'])  # 'y' 匹配, 'n' 不匹配
        if not keys:  # 超时未响应
            continue
        if 'escape' in keys:  # 提前退出
            core.quit()

        # 5. 检查正确性
        response = keys[0]
        if (response == 'y' and match) or (response == 'n' and not match):
            correct_responses += 1

    # 计算正确率
    accuracy = correct_responses / len(test_trials) * 100
    print(f"Testing phase accuracy: {accuracy}%")

    # 如果正确率低于 90%，要求重新学习
    if accuracy < 90:
        print("Accuracy below 90%. Please repeat the learning phase.")
        learning_phase()

# ---------- 运行实验 ----------
learning_phase()
testing_phase()

# ---------- 结束实验 ----------
win.close()
core.quit()
