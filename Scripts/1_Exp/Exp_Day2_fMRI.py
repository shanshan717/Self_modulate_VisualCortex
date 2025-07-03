#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fMRI Experiment Block Design 
"""

import os
import random
import copy
from collections import defaultdict, OrderedDict

import numpy as np
import pandas as pd
from psychopy import visual, event, core, sound, data, gui

import sys
from psychopy import logging, prefs


# ---------------------- 被试信息 ----------------------
expInfo = {
    '测试时间': data.getDateStr(),
    '受试者编号': '000',
    'run': '1',
    '年龄': '',
    '性别': ['Male', 'Female']
}
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

# ---------------------- 基本实验参数 ----------------------

stim_duration = 1.0
fixation_duration = 0.5
null_duration = 13.5
required_groups = ['U_self', 'U_other', 'N_self', 'N_other']
blocks_per_condition = 6

# 具体看南师大美德刺激仪
target_key = '3'
# 定义列名
csv_header= ['subject_id', 'age', 'gender', 'run', 'condition', 'nonword', 'trial_num',
            'stim_onset', 'stim_offset', 'fixation_onset', 'fixation_offset',
            'frame_rate', 'date', 'response_key', 'response_time', 'is_target']

# ---------------------- 查看路径 ----------------------
current_dir = os.getcwd()
print(f"current_dir:{current_dir}")
parent_dir = os.path.dirname(current_dir)
print(f"parent_dir:{parent_dir}")
os.chdir(parent_dir)

# ---------------------- 定义输出文件路径 ----------------------
fileName = os.path.join('data', 'fmri', f"Exp2_fMRI_{expInfo['受试者编号']}_run{expInfo['run']}.csv")
os.makedirs(os.path.dirname(fileName), exist_ok=True)
with open(fileName, 'w') as f:
    f.write(','.join(csv_header) + '\n')

# ---------------------- 等待MRI触发 -------------------------
waiting_text = visual.TextStim(win, 
                            text='Waiting for trigger...', 
                            pos=(0, 0),
                            font='Microsoft YaHei',  
                            color='white',
                            wrapWidth=30,
                            height=0.8)
waiting_text.draw()
win.flip()

# 等待trigger触发
# 联影核磁仪器发送的trigger信号是"s"
trigger_key = 's'
event.clearEvents()
print("Waiting for trigger...")

# 无限循环，直到检测到 trigger
while True:
    keys = event.getKeys()
    if trigger_key in keys:
        print(f"Trigger ({trigger_key}) detected.")
        # 在接收到触发信号后立即创建实验时钟
        experiment_clock = core.Clock()
        print(f"Experiment clock created at trigger time: {experiment_clock.getTime()}")
        break
    elif 'escape' in keys:
        print("Escape key pressed. Exiting.")
        win.close()
        core.quit()

# ---------- 定义声音提示（在每个block结束之后） --------
def play_clock_transition_beep(win, components):
    """播放声音提示同时显示注视点"""
    # 绘制注视点
    for f in components['fixation']:
        f.draw()
    win.flip()
    beep = sound.Sound('A', 
                       octave=4, 
                       sampleRate=44100, 
                       secs=0.5, 
                       stereo=True)
    beep.play()
    # core.wait(0.5)

# ---------------------- 读取刺激材料 ----------------------
def load_stimuli(subject_id):
    day1_file = os.path.join('data', 'behavior', f"Exp1_task1_{subject_id}.csv")
    print(f"day1_file: {day1_file}")
    try:
        df = pd.read_csv(day1_file).head(12)
        for col in ['nonword', 'condition']:
            if col not in df.columns:
                raise ValueError(f"缺失必要列: {col}")
        stimuli = []
        for _, row in df.iterrows():
            stim = OrderedDict({
                'nonword': row['nonword'],
                'condition': row['condition'],
                'filename': f"{row['nonword']}.png",
                'type': 'stim',
                'mid_letter': row['nonword'][2],
            })
            stim['group'] = f"{stim['mid_letter']}_{stim['condition']}"
            stimuli.append(stim)
        return stimuli
    except Exception as e:
        print(f"材料加载失败: {str(e)}")
        win.close()
        core.quit()

# ---------------------- 分组 ----------------------
def group_stimuli(stimuli):
    groups = {g: [] for g in required_groups}
    for stim in stimuli:
        if stim['group'] in groups:
            groups[stim['group']].append(stim)
    for group, items in groups.items():
        if len(items) != 3:
            raise ValueError(f"组 {group} 应该恰好有3个非词（当前为 {len(items)}）")
    return groups

# ---------------------- 初始化组件 ----------------------
def init_components(win):
    return {
        'fixation': [
            visual.Circle(win, radius=0.25, edges=32, lineColor='black', fillColor=None, lineWidth=1.5),
            visual.Circle(win, radius=0.10, edges=32, fillColor='black', lineColor='black')
        ]
    }

# ---------------------- 检查ESC键退出 ----------------------
def check_exit():
    """检查是否按下ESC键，如果是则退出程序"""
    keys = event.getKeys()
    if 'escape' in keys:
        print("ESC key pressed. Exiting experiment.")
        win.close()
        core.quit()

# ---------------------- 生成干扰刺激配置 ----------------------
def generate_distractor_config(groups):
    """
    生成干扰刺激配置
    从24个block中选择4个，在这4个block中添加8个干扰刺激
    """
    # 总共24个blocks (4个条件 × 6个blocks)
    total_blocks = len(required_groups) * blocks_per_condition
    
    # 随机选择4个block索引
    selected_block_indices = random.sample(range(total_blocks), 4)
    
    # 为每个选中的block分配干扰刺激数量 (总共8个，每个block 1-3个)
    distractor_counts = []
    remaining = 8
    for i in range(4):
        if i == 3:  # 最后一个block分配剩余的
            distractor_counts.append(remaining)
        else:
            # 随机分配1-3个，但要确保剩余的能够分配完
            max_count = min(3, remaining - (3 - i))
            count = random.randint(1, max_count)
            distractor_counts.append(count)
            remaining -= count
    
    # 为每个选中的block生成干扰刺激配置
    distractor_config = {}
    for i, block_idx in enumerate(selected_block_indices):
        # 在第4-9位置中随机选择位置放置干扰刺激
        positions = random.sample(range(3, 9), distractor_counts[i])  # 3-8对应第4-9个位置
        distractor_config[block_idx] = positions
    
    print(f"选中的blocks: {selected_block_indices}")
    print(f"干扰刺激配置: {distractor_config}")
    
    return distractor_config

# ---------------------- 添加干扰刺激到block ----------------------
def add_distractors_to_blocks(blocks, groups, distractor_config):
    """
    向指定的blocks中添加干扰刺激
    """
    all_stimuli = []
    for group_stimuli in groups.values():
        all_stimuli.extend(group_stimuli)
    
    block_counter = 0
    for block in blocks:
        if block['condition'] != 'null':
            if block_counter in distractor_config:
                positions = distractor_config[block_counter]
                current_condition = block['condition']
                
                # 获取其他条件的刺激作为干扰
                other_conditions = [c for c in required_groups if c != current_condition]
                
                for pos in positions:
                    # 随机选择一个其他条件的刺激作为干扰
                    distractor_condition = random.choice(other_conditions)
                    distractor_stimuli = groups[distractor_condition]
                    distractor = random.choice(distractor_stimuli)
                    
                    # 复制并标记为干扰刺激
                    distractor_trial = copy.deepcopy(distractor)
                    distractor_trial['is_target'] = True
                    distractor_trial['original_condition'] = current_condition
                    distractor_trial['distractor_condition'] = distractor_condition
                    
                    # 替换指定位置的刺激
                    block['trial_list'][pos] = distractor_trial
                    
                print(f"Block {block_counter} ({current_condition}): 在位置 {positions} 添加了干扰刺激")
            
            block_counter += 1
    
    return blocks

# ---------------------- 单个 trial ----------------------
def run_trial(win, components, trial, condition, trial_num, experiment_clock):
    response_key = 'NA'
    response_time = 'NA'
    frame_rate = 60
    is_target = trial.get('is_target', False)
    
    # 如果是干扰刺激，使用target作为condition
    if is_target:
        recorded_condition = 'target'
    else:
        recorded_condition = condition

    # 检查ESC键
    check_exit()

    # fixation - 使用实验时钟
    fixation_onset = experiment_clock.getTime()
    print(f"fixation_onset: {fixation_onset}")
    for f in components['fixation']:
        f.draw()
    win.flip()
    
    # 等待注视点时间，不播放声音
    core.wait(fixation_duration)

    fixation_offset = experiment_clock.getTime()
    print(f"fixation_offset: {fixation_offset}")

    # 检查ESC键
    check_exit()

    # stimulus
    img_path = os.path.join('stimuli', f"sub-{expInfo['受试者编号']}", trial['filename'])
    stim_image = visual.ImageStim(win, image=img_path, size=(36, 20), pos=(0, 0))
    stim_image.draw()
    for f in components['fixation']:
        f.draw()
    win.flip()

    stim_onset = experiment_clock.getTime()
    fixation_offset = stim_onset
    print(f"fixation_offset: {fixation_offset}")
    print(f"stim_onset: {stim_onset}")
    # 如果是干扰刺激，监听按键反应
    if is_target:
        event.clearEvents()
        response_clock = core.Clock()
        
        # 在刺激呈现期间监听按键
        while response_clock.getTime() < stim_duration:
            check_exit()  # 检查ESC键
            keys = event.getKeys(keyList=[target_key], timeStamped=response_clock)
            if keys:
                response_key = keys[0][0]
                response_time = round(keys[0][1], 4)
                break
        
        # 如果在刺激呈现期间没有反应，继续等待一小段时间
        if response_key == 'NA':
            remaining_time = stim_duration - response_clock.getTime()
            if remaining_time > 0:
                core.wait(remaining_time)
    else:
        core.wait(stim_duration)
    
    stim_offset = experiment_clock.getTime()

    trial_data = OrderedDict([
        ('subject_id', expInfo['受试者编号']),
        ('age', expInfo['年龄']),
        ('gender', expInfo['性别']),
        ('run', expInfo['run']),
        ('condition', recorded_condition),
        ('nonword', trial['nonword']),
        ('trial_num', trial_num),
        ('stim_onset', round(stim_onset, 4)),
        ('stim_offset', round(stim_offset, 4)),
        ('fixation_onset', round(fixation_onset, 4)),
        ('fixation_offset', round(fixation_offset, 4)),
        ('frame_rate', frame_rate),
        ('date', data.getDateStr()),
        ('response_key', response_key),
        ('response_time', response_time),
        ('is_target', 1 if is_target else 0)
    ])
    with open(fileName, 'a') as f:
        f.write(','.join([str(trial_data[k]) for k in csv_header]) + '\n')

# ---------------------- block生成 ----------------------
def generate_blocks(groups):
    blocks = []
    total_sets = blocks_per_condition  # 6组
    
    for set_idx in range(total_sets):
        # 打乱条件顺序
        condition_order = random.sample(required_groups, len(required_groups))
        
        # 添加4个条件block
        for condition in condition_order:
            items = groups[condition]
            trial_list = []
            for item in items:
                trial_list.extend([copy.deepcopy(item) for _ in range(3)])
            random.shuffle(trial_list)
            blocks.append({'condition': condition, 'trial_list': trial_list})
        
        # 前5组后添加null block，最后一组后不添加
        if set_idx < total_sets - 1:  # 0-4 (共5组)
            blocks.append({'condition': 'null', 'trial_list': None})
    
    # 生成干扰刺激配置并添加到blocks中
    distractor_config = generate_distractor_config(groups)
    blocks = add_distractors_to_blocks(blocks, groups, distractor_config)
    
    return blocks

# ---------------------- 定义结束语 ----------------------
def show_final_message(win, text):
    """显示结束语1.0秒后自动结束"""
    message = visual.TextStim(win, 
                            text=text, 
                            color='white', 
                            height=1.0, 
                            wrapWidth=30, 
                            font='Microsoft YaHei')
    message.draw()
    win.flip()
    # 显示1.0秒后自动结束
    core.wait(1.0)  

# ---------------------- 主程序入口 ----------------------
def main():
    components = init_components(win)
    stimuli = load_stimuli(expInfo['受试者编号'])
    grouped = group_stimuli(stimuli)
    blocks = generate_blocks(grouped)
    trial_counter = 1

    for block in blocks:
        condition = block['condition']
        if condition == 'null':
            check_exit()  # 检查ESC键
            
            null_onset = experiment_clock.getTime()
            for f in components['fixation']:
                f.draw()
            win.flip()
            core.wait(null_duration)
            null_offset = experiment_clock.getTime()

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
                ('frame_rate', 75),
                ('date', data.getDateStr()),
                ('response_key', 'NA'),
                ('response_time', 'NA'),
                ('is_target', 0)
            ])
            with open(fileName, 'a') as f:
                f.write(','.join([str(null_data[k]) for k in csv_header]) + '\n')
            trial_counter += 1
        else:
            for i, trial in enumerate(block['trial_list']):
                run_trial(win, components, trial, condition, trial_counter, experiment_clock)
                trial_counter += 1
            play_clock_transition_beep(win, components)

    show_final_message(win, "该run已结束，感谢您的参与！")
    win.close()
    core.quit()

if __name__ == "__main__":
    main()