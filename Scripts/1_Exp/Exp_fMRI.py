#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
fMRI Experiment Procedure (Day 2)
"""
from collections import defaultdict
from psychopy import visual, event, core, data, gui
import numpy as np
import pandas as pd
import os
import random
from collections import OrderedDict

# ---------------------- 实验参数 ----------------------
BASE_PATH = "/Volumes/ss/psychopy_514/"
STIM_DURATION = 1.0
TARGET_DURATION = 1.0 
NULL_DURATION = 14.0
ITI_MIN = 3.0
ITI_MAX = 15.0
ITI_MEAN = 5.0
N_RUNS = 6
REQUIRED_GROUPS = ['U_self', 'U_other', 'N_self', 'N_other']
RESPONSE_KEYS = ['z']

# ---------------------- ITI 函数 ----------------------
def truncated_exponential(min_val, max_val, mean_val):
    rate = 1.0 / (mean_val - min_val)
    while True:
        sample = np.random.exponential(1 / rate)
        iti = min_val + sample
        if iti <= max_val:
            return iti

# ---------------------- 被试信息 ----------------------
expInfo = {'测试时间': data.getDateStr(),
           '受试者编号': '000',
           '年龄': '',
           '性别': ['Male', 'Female']}
dlg = gui.DlgFromDict(dictionary=expInfo,
                      title='基本信息',
                      fixed=['测试时间'])
if not dlg.OK:
    core.quit()

# ---------------------- 初始化窗口 ----------------------
try:
    win = visual.Window(
        size=[1920, 1080],
        allowGUI=False,
        monitor='testMonitor',
        units='deg',
        fullscr=True,
        color='grey'
    )
    win.setMouseVisible(False)
except Exception as e:
    print(f"窗口初始化失败: {str(e)}")
    core.quit()

# ---------------------- 等待 trigger 触发 ----------------------
print("Waiting for MRI trigger (press 'S' on the keyboard)...")
trigger_received = False
start_time = core.getTime()

while not trigger_received:
    keys = event.getKeys(keyList=['s'])
    print("Detected keys:", keys)  
    if 's' in keys:
        print("Trigger received, starting experiment...")
        trigger_received = True
    if core.getTime() - start_time > 30:
        print("Still waiting for trigger... (press 's')")
        start_time = core.getTime()
    core.wait(0.1)

# ---------------------- 数据文件 ----------------------
fileName = os.path.join(BASE_PATH, f"data/fmri/Exp2_fMRI_{expInfo['受试者编号']}.csv")
os.makedirs(os.path.dirname(fileName), exist_ok=True)

CSV_HEADER = [
    'subject_id', 'age', 'gender', 'run', 'trial_type', 'fixation_onset', 'fixation_offset', 
    'stim_onset', 'stim_offset', 'ITI_onset', 'ITI_offset', 'condition', 'nonword',
    'response_key', 'response_time', 'frame_rate', 'date'
]
with open(fileName, 'w') as dataFile:
    dataFile.write(','.join(CSV_HEADER) + '\n')
    
# ---------------------- 显示提示信息 ----------------------
def show_instructions(win, text, wait_key='space'):
    instr = visual.TextStim(win, text=text, wrapWidth=30, 
                          font='Arial Unicode MS', height=1.0)
    instr.draw()
    win.flip()
    event.waitKeys(keyList=[wait_key])

show_instructions(win,
    f"""欢迎参加实验！\n
    您将看到之前所学习过的非词，请保持注视。\n
    当出现不是之前所学习的非词时，请按 “z” 键反应。\n
    实验共包含{N_RUNS}个部分，每部分结束可有短暂的休息时间。\n
    准备就绪后请按空格键开始。""")

# ---------------------- 实验材料 ----------------------
def load_stimuli(subject_id):
    day1_file = os.path.join(BASE_PATH, 'data', 'behavior', f"Exp1_task1_{subject_id}.csv")
    try:
        df = pd.read_csv(day1_file)
        if df.empty:
            raise ValueError("空数据文件")
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
            stim['group'] = f"{stim['mid_letter']}_{stim['condition']}"
            stimuli.append(stim)
        print(f"成功加载 {len(stimuli)} 个刺激")
        return stimuli
    except Exception as e:
        print(f"材料加载失败: {str(e)}")
        win.close()
        core.quit()
        
# ---------------------- 定义 validate_stimuli ----------------------
def validate_stimuli(stimuli):
    if len(stimuli) < 12:
        print(f"警告：只有 {len(stimuli)} 个基础刺激，将进行重复填充")
        while len(stimuli) < 12:
            stimuli.append(random.choice(stimuli))
    elif len(stimuli) > 12:
        print(f"警告：有 {len(stimuli)} 个刺激，将裁剪为前12个")
        stimuli = stimuli[:12]
    return stimuli

def group_stimuli(stimuli):
    groups = {g: [] for g in REQUIRED_GROUPS}
    for stim in stimuli:
        if stim['group'] in groups:
            groups[stim['group']].append(stim)

    for group in REQUIRED_GROUPS:
        while len(groups[group]) < 3:
            if len(groups[group]) == 0:
                raise ValueError(f"组 {group} 没有可用刺激")
            groups[group].append(random.choice(groups[group]))

    for group in REQUIRED_GROUPS:
        random.shuffle(groups[group])
    return groups
    
# ---------------------- 定义干扰刺激函数 ----------------------
def load_target_stimuli(subject_id):
    target_dir = os.path.join(BASE_PATH, 'target', f"sub_{subject_id}")
    try:
        files = [f for f in os.listdir(target_dir) if f.endswith('.png')]
        if len(files) < 12:
            raise ValueError(f"应有12个target制绝，实际为{len(files)}")
        random.shuffle(files)
        stimuli = []
        for fname in files:
            stim = OrderedDict()
            stim['nonword'] = os.path.splitext(fname)[0]
            stim['condition'] = 'target'
            stim['filename'] = fname
            stim['type'] = 'target'
            stim['group'] = 'target'
            stim['is_target'] = True
            stimuli.append(stim)
        return stimuli 
    except Exception as e:
        print(f"target制绝加载失败: {str(e)}")
        win.close()
        core.quit()

# ---------------------- 实验组件 ----------------------
def init_components(win):
    return {
        'fixation': [
            visual.Circle(win, radius=0.25, edges=32, lineColor='black', fillColor=None, lineWidth=1.5),
            visual.Circle(win, radius=0.10, edges=32, fillColor='black', lineColor='black')
        ],
        'stim_image': visual.ImageStim(win, size=(36, 20), pos=(0,0)),
        'text': visual.TextStim(win, font='Arial Unicode MS', pos=(0, 0), height=0.8, color='white', wrapWidth=30)
    }
    
# ---------------------- 试次流程 ----------------------
def run_trial(win, components, trial, run_idx, global_clock):
    frame_rate = 75
    response_key = 'NA'
    response_time = 'NA'
    
    fixation_onset = core.getTime()
    for f in components['fixation']:
        f.draw()
    win.flip()
    core.wait(0.5)
    fixation_offset = core.getTime()
    
    stim_onset = stim_offset = 'NA'
    if trial['type'] == 'target':
        img_path = os.path.join(BASE_PATH, 'target', f"sub_{expInfo['受试者编号']}", trial['filename'])
        components['stim_image'].image = img_path
        components['stim_image'].draw()
        win.flip()
        stim_onset = core.getTime()
        resp_clock = core.Clock()
        response = []
        while resp_clock.getTime() < TARGET_DURATION:
            keys = event.getKeys(keyList=RESPONSE_KEYS + ['escape'], timeStamped=resp_clock)
            if keys:
                for key, t in keys:
                    if key in RESPONSE_KEYS:
                        response.append((key, t))
                    elif key == 'escape':
                        win.close()
                        core.quit()
        stim_offset = core.getTime()
        if response:
            response_key, response_time = response[0]
    elif trial['type'] == 'stim':
        img_path = os.path.join(BASE_PATH, 'stimuli', trial['filename'])
        components['stim_image'].image = img_path
        components['stim_image'].draw()
        win.flip()
        stim_onset = core.getTime()
        core.wait(STIM_DURATION)
        stim_offset = core.getTime()
    elif trial['type'] == 'null':
        core.wait(NULL_DURATION)
    
    # ITI
    ITI_onset = core.getTime()
    for f in components['fixation']:
        f.draw()
    win.flip()
    iti_duration = truncated_exponential(ITI_MIN, ITI_MAX, ITI_MEAN)
    core.wait(iti_duration)
    ITI_offset = core.getTime()

    trial_info = OrderedDict([
        ('subject_id', expInfo['受试者编号']),
        ('age', expInfo['年龄']),
        ('gender', expInfo['性别']),
        ('run', run_idx + 1),
        ('trial_type', trial['type']),
        ('fixation_onset', round(fixation_onset, 4)),
        ('fixation_offset', round(fixation_offset, 4)),
        ('stim_onset', round(stim_onset, 4) if stim_onset != 'NA' else 'NA'),
        ('stim_offset', round(stim_offset, 4) if stim_offset != 'NA' else 'NA'),
        ('ITI_onset', round(ITI_onset, 4)),
        ('ITI_offset', round(ITI_offset, 4)),
        ('condition', trial.get('condition', 'NA')),
        ('nonword', trial.get('nonword', 'NA')),
        ('response_key', response_key),
        ('response_time', round(response_time, 4) if response_key != 'NA' else 'NA'),
        ('frame_rate', frame_rate),
        ('date', data.getDateStr())
    ])

    try:
        with open(fileName, 'a') as f:
            f.write(','.join([str(trial_info[k]) for k in CSV_HEADER]) + '\n')
    except Exception as e:
        print(f"数据记录失败: {str(e)}")

    return True

# ---------------------- 实验设计生成 ----------------------
def insert_targets(base_design, targets):
    """插入4个target，确保不连续"""
    if len(targets) != 4:
        raise ValueError("需要4个target")
    
    temp_design = base_design.copy()
    possible_positions = list(range(len(temp_design)+1))
    selected_pos = []
    attempts = 0
    
    while len(selected_pos) < 4 and attempts < 1000:
        pos = random.choice(possible_positions)
        valid = True
        for p in selected_pos:
            if abs(pos-p) <= 1:
                valid = False
                break
        if valid:
            selected_pos.append(pos)
            possible_positions = [p for p in possible_positions 
                                if abs(p-pos) > 1]
        attempts += 1
    
    selected_pos.sort(reverse=True)
    for i, pos in enumerate(selected_pos):
        temp_design.insert(pos, targets[i])
    return temp_design

def generate_run_design(stimuli_groups, targets):
    # 生成基础设计（12个普通刺激）
    run_design = []
    group_order = random.sample(REQUIRED_GROUPS, len(REQUIRED_GROUPS))
    for group in group_order:
        run_design.extend(stimuli_groups[group][:3])
    # 插入target刺激
    run_design = insert_targets(run_design, targets)
    # 添加null试次
    run_design.append(OrderedDict([
        ('type', 'null'),
        ('nonword', 'NULL'),
        ('condition', 'NULL'),
        ('group', 'NULL'),
        ('filename', 'NULL')
    ]))
    return run_design

# ---------------------- 主流程 ----------------------
def main():
    components = init_components(win)
    # 加载刺激材料
    raw_stimuli = load_stimuli(expInfo['受试者编号'])
    target_stimuli = load_target_stimuli(expInfo['受试者编号'])
    
    # 验证并分组普通刺激
    validated_stimuli = validate_stimuli(raw_stimuli)
    stimuli_groups = group_stimuli(validated_stimuli)
    
    # 准备target刺激分配
    random.shuffle(target_stimuli)
    target_counter = defaultdict(int)
    global_clock = core.Clock()
    
    for run_idx in range(N_RUNS):
        # 显示run开始提示
        show_instructions(win, f"第{run_idx+1}部分即将开始\n请保持注视中央点\n准备就绪后请按空格键")
        
        # 生成当前run的设计
            # 生成当前run的四个target
        current_targets = []
        temp_counter = defaultdict(int)
        while len(current_targets) < 4:
            # 筛选可用target
            candidates = [t for t in target_stimuli 
                         if target_counter[t['filename']] + temp_counter[t['filename']] < 2]
            if not candidates:
                print("无法选择足够的target")
                core.quit()
            selected = random.choice(candidates)
            current_targets.append(selected)
            temp_counter[selected['filename']] += 1

        # 更新全局计数器
        for t in current_targets:
            target_counter[t['filename']] += 1
        run_design = generate_run_design(stimuli_groups, current_targets)
        
        # 运行试次
        for trial in run_design:
            success = run_trial(win, components, trial, run_idx, global_clock)
            if not success:
                win.close()
                core.quit()
            if 'escape' in event.getKeys():
                win.close()
                core.quit()
        
        # 显示run结束提示（最后一个run除外）
        if run_idx < N_RUNS-1:
            show_instructions(win, f"第{run_idx+1}部分完成\n请稍作休息\n准备继续时请按空格键")

    # 结束实验
    show_instructions(win, "实验结束！感谢您的参与！")
    win.close()
    core.quit()

if __name__ == "__main__":
    main()