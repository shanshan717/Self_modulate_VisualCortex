#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ================== import libraries ==================
from math import atan, pi
from psychopy import visual, event, core, data, gui, monitors
import os
import random
import pandas as pd

# ================== 被试信息 ==================
expInfo = {'测试时间': data.getDateStr(),
            '受试者编号': '000',
            '性别': ['Male', 'Female']}
dlg = gui.DlgFromDict(dictionary=expInfo, title='基本信息', fixed=['测试时间'])
if not dlg.OK:
    core.quit()
    
# set save path (base on the subject id)
subj_id = expInfo['受试者编号']
output_folder = os.path.join('..', 'target',f'sub-{subj_id}')
os.makedirs(output_folder, exist_ok=True)


# ================== load nonwords from CSV ==================
csv_path = os.path.join('..', 'target.csv')
df = pd.read_csv(csv_path)

# 按照第三个字母为 n 或 u 分别抽取
nonwords_n = df[df['sub-099'].str[2].str.lower() == 'n']['sub-099'].tolist()
nonwords_u = df[df['sub-099'].str[2].str.lower() == 'u']['sub-099'].tolist()

selected_n = random.sample(nonwords_n,4)
selected_u = random.sample(nonwords_u,4)
selected_nonwords = selected_n + selected_u
random.shuffle(selected_nonwords)

# ================== initialize psychoPy window ==================
monitor = monitors.Monitor('testMonitor')
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=True,
                    color='grey')

# hide mouse cursor
win.setMouseVisible(False)

# ================== set Nonword Display Parameters ==================
# 设置字母高度、宽度以及字母之间的间隔 (deg)
letter_height = 5.5
letter_width = 3.6   
spacing = 0.6        
num_letters = 5 
x_positions = [(i - (num_letters - 1) / 2) * (letter_width + spacing) for i in range(num_letters)]
print(x_positions)
padding_scale = 2.7
base_padding = 0.9

# ================== calculate background size ==================
# 根据文字区域大小 + 边距计算背景噪声图像应呈现的尺寸
nonword_width = max(x_positions) - min(x_positions)  
nonword_height = letter_height

bg_width = nonword_width + 2 * base_padding * padding_scale
bg_height = nonword_height + 2 * base_padding * padding_scale
bg_size = (bg_width, bg_height)

# ================== 加载背景图像并分类 ==================
noise_folder = '../noise'
noise_images = {'noise': [], 'inverted': []}

for filename in os.listdir(noise_folder):
    if filename.startswith('._') or not filename.lower().endswith('.png'):
        continue
    img_path = os.path.join(noise_folder, filename)
    stim = visual.ImageStim(win=win, 
                            image=img_path, 
                            units='deg', 
                            size=bg_size, 
                            pos=(0, 0))
    if filename.startswith('noise'):
        noise_images['noise'].append(stim)
    elif filename.startswith('inverted'):
        noise_images['inverted'].append(stim)

# 随机选取6个noise和6个inverted背景图
selected_noise = random.sample(noise_images['noise'],4)
selected_inverted = random.sample(noise_images['inverted'],4)
selected_backgrounds = selected_noise + selected_inverted
random.shuffle(selected_backgrounds)

# ================== function to create letter stimuli ==================
def create_letter_stimuli(word):
    stimuli = []
    for idx, char in enumerate(word):
        text = char
        flip = False
        y_pos = 0
        y_offset = 0.2
        # 如果第三个字母为N，则显示为U上下翻转形态
        if idx == 2 and char == 'N':
            text = 'U'
            flip = True
            y_pos = y_offset
        stim = visual.TextStim(
            win=win,
            text=text,
            pos=(x_positions[idx], y_pos),
            height=letter_height,
            opacity=0.9,
            flipVert=flip,
            alignText='center',
            anchorHoriz='center',
            anchorVert='center'
        )
        stimuli.append(stim)
    return stimuli

# ================== main Experiment Loop ================== 
for i, trial_word in enumerate(selected_nonwords):
    background = selected_backgrounds[i]
    trial_stimuli = create_letter_stimuli(trial_word)

    win.flip()
    background.draw()
    for stim in trial_stimuli:
        stim.draw()
    win.flip()

    screenshot_path = os.path.join(output_folder, f"{trial_word}.png")
    win.getMovieFrame()
    win.saveMovieFrames(screenshot_path)

    core.wait(0.5)

win.close()
core.quit()