#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fMRI Experiment Block Design (Run-Based)
"""

from collections import defaultdict, OrderedDict
from psychopy import visual, event, core, data, gui
import numpy as np
import pandas as pd
import random
import os
import copy

# ---------------------- 基本实验参数 ----------------------
BASE_PATH = "/Volumes/ss/psychopy_514/"
STIM_DURATION = 1.0
FIXATION_DURATION = 0.5
NULL_DURATION = 13.5
REQUIRED_GROUPS = ['U_self', 'U_other', 'N_self', 'N_other']
BLOCKS_PER_CONDITION = 8
RESPONSE_KEYS = ['s']
CSV_HEADER = [
    'subject_id', 'age', 'gender', 'run', 'condition', 'nonword', 'trial_num',
    'stim_onset', 'stim_offset', 'fixation_onset', 'fixation_offset',
    'response_key', 'response_time', 'frame_rate', 'date'
]

# ---------------------- 被试信息 ----------------------
expInfo = {'测试时间': data.getDateStr(),
            '受试者编号': '000',
            'run': '1',
            '年龄': '',
            '性别': ['Male', 'Female']}
dlg = gui.DlgFromDict(dictionary=expInfo, title='基本信息', fixed=['测试时间'])
if not dlg.OK:
    core.quit()

# ---------------------- 初始化窗口 ----------------------
win = visual.Window(
    size=[1920, 1080],
    allowGUI=False,
    monitor='testMonitor',
    units='deg',
    fullscr=True,
    color='grey'
)
win.setMouseVisible(False)
    
# ---------------------- Data File ----------------------
fileName = os.path.join(BASE_PATH, f"data/fmri/Exp2_fMRI_{expInfo['受试者编号']}_run{expInfo['run']}.csv")
os.makedirs(os.path.dirname(fileName), exist_ok=True)
with open(fileName, 'w') as f:
    f.write(','.join(CSV_HEADER) + '\n')

# ---------------------- def trigger----------------------
def wait_for_trigger(win):
    prompt = visual.TextStim(win, text="等待MRI触发，请按下 's' 键开始", font='Arial Unicode MS', height=1.0)
    clock = core.Clock()
    while True:
        prompt.draw()
        win.flip()
        keys = event.getKeys()
        if 's' in keys:
            break
        core.wait(0.1)
        
# ---------------------- Show Instructions ----------------------
def show_instructions(win, text, wait_key='space'):
    instr = visual.TextStim(win, text=text, wrapWidth=30, font='Arial Unicode MS', height=1.0)
    instr.draw()
    win.flip()
    event.waitKeys(keyList=[wait_key])

# ---------------------- Load Stimuli ----------------------
def load_stimuli(subject_id):
    day1_file = os.path.join(BASE_PATH, 'data', 'behavior', f"Exp1_task1_{subject_id}.csv")
    try:
        df = pd.read_csv(day1_file)
        if df.empty:
            raise ValueError("空数据文件")
        df = df.head(12)  

        # 检查必要列
        for col in ['nonword', 'condition']:
            if col not in df.columns:
                raise ValueError(f"缺失必要列: {col}")

        stimuli = []
        for _, row in df.iterrows():
            stim = OrderedDict()
            stim['nonword'] = row['nonword']
            stim['condition'] = row['condition']
            stim['filename'] = f"{row['nonword']}.png"
            stim['type'] = 'stim'
            stim['mid_letter'] = row['nonword'][2]
            stim['group'] = f"{stim['mid_letter']}_{stim['condition']}"  # 如 U_self
            stimuli.append(stim)

        print(f"成功加载前12个非词，来自4个条件，共 {len(stimuli)} 个刺激")
        return stimuli
    except Exception as e:
        print(f"材料加载失败: {str(e)}")
        win.close()
        core.quit()

# ---------------------- Group Stimuli ----------------------
def group_stimuli(stimuli):
    groups = {g: [] for g in REQUIRED_GROUPS}
    for stim in stimuli:
        if stim['group'] in groups:
            groups[stim['group']].append(stim)

    for group, items in groups.items():
        if len(items) != 3:
            raise ValueError(f"组 {group} 应该恰好有3个非词（当前为 {len(items)}）")

    return groups

# ---------------------- Initialize Components ----------------------
def init_components(win):
    return {
        'fixation': [
            visual.Circle(win, radius=0.25, edges=32, lineColor='black', fillColor=None, lineWidth=1.5),
            visual.Circle(win, radius=0.10, edges=32, fillColor='black', lineColor='black')
        ],
        'stim_image': visual.ImageStim(win, size=(36, 20), pos=(0, 0))
    }

# ---------------------- Run Trial ----------------------
def run_trial(win, components, trial, condition, trial_num, global_clock):
    response_key = 'NA'
    response_time = 'NA'
    frame_rate = 75

    # fixation
    fixation_onset = core.getTime()
    for f in components['fixation']:
        f.draw()
    win.flip()
    core.wait(FIXATION_DURATION)
    fixation_offset = core.getTime()

    # stimulus
    stim_onset = stim_offset = 'NA'
    img_path = os.path.join(BASE_PATH, 'stimuli', trial['filename'])
    components['stim_image'].image = img_path
    components['stim_image'].draw()
    win.flip()
    stim_onset = core.getTime()
    resp_clock = core.Clock()
    response = []
    while resp_clock.getTime() < STIM_DURATION:
        keys = event.getKeys(keyList=RESPONSE_KEYS + ['escape'], timeStamped=resp_clock)
        for key, t in keys:
            if key in RESPONSE_KEYS:
                response.append((key, t))
            elif key == 'escape':
                win.close()
                core.quit()
    stim_offset = core.getTime()
    if response:
        response_key, response_time = response[0]

    trial_data = OrderedDict([
        ('subject_id', expInfo['受试者编号']),
        ('age', expInfo['年龄']),
        ('gender', expInfo['性别']),
        ('run', expInfo['run']),
        ('condition', condition),
        ('nonword', trial['nonword']),
        ('trial_num', trial_num),
        ('stim_onset', round(stim_onset, 4)),
        ('stim_offset', round(stim_offset, 4)),
        ('fixation_onset', round(fixation_onset, 4)),
        ('fixation_offset', round(fixation_offset, 4)),
        ('response_key', response_key),
        ('response_time', round(response_time, 4) if response_key != 'NA' else 'NA'),
        ('frame_rate', frame_rate),
        ('date', data.getDateStr())
    ])
    with open(fileName, 'a') as f:
        f.write(','.join([str(trial_data[k]) for k in CSV_HEADER]) + '\n')

# ---------------------- Generate Blocks ----------------------
def generate_blocks(groups):
    blocks = []
    for _ in range(BLOCKS_PER_CONDITION):
        condition_order = random.sample(REQUIRED_GROUPS, len(REQUIRED_GROUPS))  # 打乱4组顺序
        for condition in condition_order:
            items = groups[condition]  # ✅ 固定的3个非词
            trial_list = []
            for item in items:
                trial_list.extend([copy.deepcopy(item) for _ in range(3)])  # 每个非词重复3次
            random.shuffle(trial_list)  # 打乱9个trial顺序
            blocks.append((condition, trial_list))
        blocks.append(('null', None))
    return blocks  # 移除最后多出的null

# ---------------------- Main ----------------------
def main():
    components = init_components(win)
    wait_for_trigger(win)

    stimuli = load_stimuli(expInfo['受试者编号'])
    grouped = group_stimuli(stimuli)
    blocks = generate_blocks(grouped)
    global_clock = core.Clock()
    trial_counter = 1

    for block in blocks:
        condition, trial_list = block
        if condition == 'null':
            null_onset = core.getTime()
            for f in components['fixation']:
                f.draw()
            win.flip()
            core.wait(NULL_DURATION)
            null_offset = core.getTime()
            
            # 记录 null block 的信息
            null_data = OrderedDict([
                ('subject_id', expInfo['受试者编号']),
                ('age', expInfo['年龄']),
                ('gender', expInfo['性别']),
                ('run', expInfo['run']),
                ('condition', 'null'),
                ('nonword', 'NA'),
                ('trial_num', trial_counter),
                ('stim_onset', 'NA'),
                ('stim_offset', 'NA'),
                ('fixation_onset', round(null_onset, 4)),
                ('fixation_offset', round(null_offset, 4)),
                ('response_key', 'NA'),
                ('response_time', 'NA'),
                ('frame_rate', 75),
                ('date', data.getDateStr())
            ])
            with open(fileName, 'a') as f:
                f.write(','.join([str(null_data[k]) for k in CSV_HEADER]) + '\n')

            trial_counter += 1
        else:
            for trial in trial_list:
                run_trial(win, components, trial, condition, trial_counter, global_clock)
                trial_counter += 1

    show_instructions(win, "该run已结束，感谢您的参与！")
    win.close()
    core.quit()

if __name__ == "__main__":
    main() 