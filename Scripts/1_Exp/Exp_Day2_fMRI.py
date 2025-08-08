#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
- fMRI Experiment Block Design
- 为60hz刷新率的显示器计算帧数
"""

import os
import sys
import random
import copy
import numpy as np
import pandas as pd
from collections import defaultdict, OrderedDict
from psychopy import visual, event, core, data, gui, logging, prefs


# =============================================================
#                           记录被试信息
# =============================================================

expInfo = {
    '测试时间': data.getDateStr(),
    '受试者编号': '000',
    'run': ['1','2','3','4','5'],
    '年龄': '',
    '性别': ['Male', 'Female']
}
dlg = gui.DlgFromDict(dictionary=expInfo, title='基本信息', fixed=['测试时间'])
if not dlg.OK:
    core.quit()

# =============================================================
#                           初始化窗口
# =============================================================
win = visual.Window(
    size=[1920, 1080],
    allowGUI=False,
    monitor='testMonitor',
    units='deg',
    fullscr=True,
    color='grey'
)
win.setMouseVisible(False)


# =============================================================
#                           定义主要变量
# =============================================================
# 时间设置（帧数）
STIM_FRAMES = 60    # 1000ms = 60帧
FIXATION_FRAMES = 30    # 500ms = 30帧
STIMULI_PER_BLOCK = 9   # 每个block有9个刺激
NULL_FRAMES = 810       # 13.5秒 = 810帧

# 保留原有参数用于兼容性
stim_duration = 1.0
fixation_duration = 0.5
null_duration = 13.5
required_groups = ['U_self', 'U_other', 'N_self', 'N_other']
blocks_per_condition = 6

# 南师大美德刺激仪的反应盒（"3"和"4"）
target_key = '3'

# =============================================================
#                           定义主要变量
# =============================================================
current_dir = os.getcwd()
print(f"current_dir:{current_dir}")
parent_dir = os.path.dirname(current_dir)
print(f"parent_dir:{parent_dir}")
os.chdir(parent_dir)

# 定义列名
csv_header= ['subject_id', 'age', 'gender', 'run', 'condition', 'nonword', 
            'trial_num', 'stim_onset', 'stim_offset', 'fixation_onset', 'fixation_offset', 'frame_rate', 
            'date', 'response_key', 'response_time', 'is_target']
 
# 定义输出文件路径
fileName = os.path.join('data', 'fmri', f"Exp2_fMRI_{expInfo['受试者编号']}_run{expInfo['run']}.csv")
os.makedirs(os.path.dirname(fileName), exist_ok=True)
with open(fileName, 'w') as f:
    f.write(','.join(csv_header) + '\n')


# =============================================================
#                   接收trigger 信号（正式/测试）
# =============================================================

def waitForExptStartTrigger(trigger_key='s', components=None):
    # 清理键盘残留按键
    event.clearEvents(eventType='keyboard')
    print(f'正在等待触发按键：{trigger_key}')
    
    # 显示注视点等待trigger信号
    fixation_objects = components['fixation']
    while True:
        # 显示注视点
        for f in fixation_objects:
            f.draw()
        win.flip()
        
        key = event.getKeys()
        if len(key) > 0:
            print(f'检测到按键：{key[0]}')
            if key[0] == trigger_key:
                print('收到trigger信号，实验即将开始')
                return
            elif key[0] == 'escape':
                core.quit()


# =============================================================
#                     读取并预加载刺激材料
# =============================================================
def load_and_preload_stimuli(subject_id):
    day1_file = os.path.join('data', 'behavior', f"Exp1_task1_{subject_id}.csv")
    print(f"day1_file: {day1_file}")
    try:
        df = pd.read_csv(day1_file).head(12)
        for col in ['nonword', 'condition']:
            if col not in df.columns:
                raise ValueError(f"缺失必要列: {col}")
        
        stimuli = []
        stim_images = {}  # 存储预创建的ImageStim对象
        
        for _, row in df.iterrows():
            stim = OrderedDict({
                'nonword': row['nonword'],
                'condition': row['condition'],
                'filename': f"{row['nonword']}.png",
                'type': 'stim',
                'mid_letter': row['nonword'][2],
            })
            stim['group'] = f"{stim['mid_letter']}_{stim['condition']}"
            
            # 预创建ImageStim对象
            img_path = os.path.join('stimuli', f"sub-{subject_id}", stim['filename'])
            if os.path.exists(img_path):
                stim_images[stim['filename']] = visual.ImageStim(
                    win, 
                    image=img_path, 
                    size=(36, 20), 
                    pos=(0, 0)
                )
                print(f"预加载: {stim['filename']}")
            else:
                print(f"警告: 图像文件不存在: {img_path}")
            
            stimuli.append(stim)
        
        print(f"预加载完成，共加载 {len(stim_images)} 个刺激图像")
        return stimuli, stim_images
        
    except Exception as e:
        print(f"材料加载失败: {str(e)}")
        win.close()
        core.quit()

# =============================================================
#                     将刺激进行分组
# =============================================================

def group_stimuli(stimuli):
    groups = {g: [] for g in required_groups}
    for stim in stimuli:
        if stim['group'] in groups:
            groups[stim['group']].append(stim)
    for group, items in groups.items():
        if len(items) != 3:
            raise ValueError(f"组 {group} 应该恰好有3个非词（当前为 {len(items)}）")
    return groups

# =============================================================
#                     初始化分组
# =============================================================
def init_components(win):
    return {
        'fixation': [
            visual.Circle(win, radius=0.25, edges=32, lineColor='black', fillColor=None, lineWidth=1.5),
            visual.Circle(win, radius=0.10, edges=32, fillColor='black', lineColor='black')
        ]
    }

# =============================================================
#                     按ESC键退出
# =============================================================
def check_exit():
    keys = event.getKeys()
    if 'escape' in keys:
        print("ESC key pressed. Exiting experiment.")
        win.close()
        core.quit()

# =============================================================
#                     生成干扰刺激
# =============================================================
def generate_distractor_config(groups):
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

# =============================================================
#                     添加干扰刺激到block
# =============================================================
def add_distractors_to_blocks(blocks, groups, distractor_config):
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

# =============================================================
#                     呈现block（按照帧计时）
# =============================================================
def present_block_by_frames(win, components, block, condition, trial_counter, experiment_clock, stim_images):
    frame_count = 0
    trial_list = block['trial_list']
    block_onset = experiment_clock.getTime()
    
    # 预先准备所有固定对象
    fixation_objects = components['fixation']
    
    for i in range(STIMULI_PER_BLOCK):
        if i < len(trial_list):
            trial = trial_list[i]
            is_target = trial.get('is_target', False)
            
            # 所有准备工作在循环外完成
            recorded_condition = 'target' if is_target else condition
            stim_image = stim_images.get(trial['filename'])
            
            if stim_image is None:
                print(f"警告: 未找到预加载的刺激图像: {trial['filename']}")
                continue
            
            # 干扰刺激的准备工作
            response_key = 'NA'
            response_time = 'NA'
            if is_target:
                event.clearEvents()
                response_clock = core.Clock()
            
            # === 刺激呈现循环：最小化代码 ===
            stim_onset = None
            for frameN in range(STIM_FRAMES):
                if frameN == 0:
                    stim_onset = experiment_clock.getTime()
                
                stim_image.draw()
                for f in fixation_objects:
                    f.draw()
                win.flip()
                
                # 最简化的按键检测
                if is_target and response_key == 'NA':
                    keys = event.getKeys(keyList=[target_key], timeStamped=response_clock)
                    if keys:
                        response_key, response_time = keys[0][0], round(keys[0][1], 4)
            
            stim_offset = experiment_clock.getTime()
            
            # === 注视点呈现循环：最小化代码 ===
            fixation_onset = experiment_clock.getTime()
            for frameN in range(FIXATION_FRAMES):
                # 如果是最后一个刺激，显示空屏而不是注视点
                if i == STIMULI_PER_BLOCK - 1:
                    # 空屏提示（不绘制任何内容）
                    pass
                else:
                    # 正常显示注视点
                    for f in fixation_objects:
                        f.draw()
                win.flip()
            
            fixation_offset = experiment_clock.getTime()
            frame_count += (STIM_FRAMES + FIXATION_FRAMES)
            
            # 数据记录移到循环外
            trial_data = OrderedDict([
                ('subject_id', expInfo['受试者编号']),
                ('age', expInfo['年龄']),
                ('gender', expInfo['性别']),
                ('run', expInfo['run']),
                ('condition', recorded_condition),
                ('nonword', trial['nonword']),
                ('trial_num', trial_counter + i),
                ('stim_onset', round(stim_onset, 4)),
                ('stim_offset', round(stim_offset, 4)),
                ('fixation_onset', round(fixation_onset, 4)),
                ('fixation_offset', round(fixation_offset, 4)),
                ('frame_rate', 60),
                ('date', data.getDateStr()),
                ('response_key', response_key),
                ('response_time', response_time),
                ('is_target', 1 if is_target else 0)
            ])
            with open(fileName, 'a') as f:
                f.write(','.join([str(trial_data[k]) for k in csv_header]) + '\n')
    
    return frame_count

# =============================================================
#                           block生成
# =============================================================
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
        
        # 每组后都添加null block（包括最后一组）
        blocks.append({'condition': 'null', 'trial_list': None})
    
    # 生成干扰刺激配置并添加到blocks中
    distractor_config = generate_distractor_config(groups)
    blocks = add_distractors_to_blocks(blocks, groups, distractor_config)
    
    print(f"总共生成 {len(blocks)} 个blocks：")
    for i, block in enumerate(blocks):
        print(f"Block {i+1}: {block['condition']}")
    
    return blocks

# =============================================================
#                           定义结束语
# =============================================================
def show_final_message(win, current_run):
    current_run_num = int(current_run)
    
    if current_run_num < 5:  # 不是最后一个run
        text = f"第{current_run_num}个run已完成！\n\n请稍作休息，\n准备进入下一个run。\n\n感谢您的配合！"
    else:  # 最后一个run
        text = "恭喜您！\n\n所有实验已完成，\n感谢您的耐心参与！\n\n请保持静止，\n等待实验人员指示。"
    
    message = visual.TextStim(win, 
                            text=text, 
                            color='white', 
                            height=1.2, 
                            wrapWidth=25, 
                            font='Microsoft YaHei')
    message.draw()
    win.flip()
    core.wait(1.0)    

# =============================================================
#                    null block 设置（帧计时）
# =============================================================
def present_null_block_by_frames(win, components, experiment_clock, trial_counter):
    check_exit()  # 检查ESC键
    
    null_onset = experiment_clock.getTime()
    
    # 呈现810帧的注视点 (13.5秒)
    for frameN in range(NULL_FRAMES):
        check_exit()  # 每帧检查ESC键
        
        for f in components['fixation']:
            f.draw()
        win.flip()
    
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
        ('frame_rate', 60),
        ('date', data.getDateStr()),
        ('response_key', 'NA'),
        ('response_time', 'NA'),
        ('is_target', 0)
    ])
    with open(fileName, 'a') as f:
        f.write(','.join([str(null_data[k]) for k in csv_header]) + '\n')

# =============================================================
#                      定义Message函数
# =============================================================
def Message(win, text):
    message = visual.TextStim(win, 
                            text=text, 
                            color='white', 
                            height=1.0, 
                            wrapWidth=30, 
                            font='Microsoft YaHei')
    message.draw()
    win.flip()

# =============================================================
#                         主程序
# =============================================================
def main():
    # 在等待trigger之前完成所有准备工作
    components = init_components(win)
    
    stimuli, stim_images = load_and_preload_stimuli(expInfo['受试者编号'])
    
    grouped = group_stimuli(stimuli)
    blocks = generate_blocks(grouped)
    
    # 显示注视点
    for f in components['fixation']:
        f.draw()
    win.flip()
    waitForExptStartTrigger('s', components)
    
    # 创建实验时钟
    experiment_clock = core.Clock()  
    trial_counter = 1
    
    print("实验开始！")
    
    # 开始实验
    for block in blocks:
        condition = block['condition']
        if condition == 'null':
            present_null_block_by_frames(win, components, experiment_clock, trial_counter)
            trial_counter += 1
        else:
            # 传入预加载的刺激图像
            frame_count = present_block_by_frames(win, components, block, condition, trial_counter, experiment_clock, stim_images)
            print(f"Block {condition} 完成，总帧数: {frame_count}")
            trial_counter += len(block['trial_list'])

    show_final_message(win, expInfo['run'])
    win.close()
    core.quit()

if __name__ == "__main__":
    main()