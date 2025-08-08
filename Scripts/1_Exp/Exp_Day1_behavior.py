#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Experiment 1 Procedure

Created: Feburary 9, 2025, 11:5
Author: Shanshan Zhu(zhushanshan0717@gmail.com)

For inquiries, please contact the author.
"""

# import required libraries
from psychopy import visual, event, core, data, gui
from psychopy.hardware import keyboard
import numpy as np
import pandas as pd
import os
from psychopy.monitors import Monitor
import random  
from psychopy.iohub import launchHubServer
import matplotlib.pyplot as plt

# —————————————————————Record participant information—————————————————-
expInfo = {'测试时间': data.getDateStr(),
           '受试者编号': '000',
           '年龄': '',
           '性别': ['Male', 'Female']}
dlg = gui.DlgFromDict(dictionary=expInfo,
                      title='基本信息',
                      fixed=['测试时间'])
if dlg.OK == False:
    core.quit()
    
# match pronoun based on participant gender (he/she)
if expInfo['性别'] == 'Female':
    pronoun = '她'
else:
    pronoun = '他'

# ————————————————————create experiment window———————————————————————
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=True,
                    color='grey')

# hide mouse cursor
win.setMouseVisible(False)
monitor = Monitor(name='testMonitor')

#defaultKeyboard = keyboard.Keyboard(backend='iohub')

current_dir = os.getcwd()
print(f"current_dir:{current_dir}")
parent_dir = os.path.dirname(current_dir)
print(f"parent_dir:{parent_dir}")
os.chdir(parent_dir)

# —————————————————————create folder for experiment data————————————————————

fileName = os.path.join('data', 'behavior', f"Exp1_task1_{expInfo['受试者编号']}.csv")
os.makedirs(os.path.dirname(fileName), exist_ok=True)  
dataFile = open(fileName, 'w')
dataFile.write('subject_id,age,gender,block,stage,fixation_onset,fixation_offset,'
                'stim_onset,stim_offset,ITI_onset,ITI_offset,response,label_onset,'
                'condition,nonword,subject_response,true_response,correct,rt,'
                'frame_rate,date,\n')

# measure frame rate
#frame_rate = win.getActualFrameRate()
#print(f"测得的帧率: {frame_rate} Hz")

# set default frame rate
frame_rate = 75

# set experiment components
left_option = visual.TextStim(win, text='我', height=2.5, font='Microsoft YaHei', pos=(-5, 0), color='white')
right_option = visual.TextStim(win, text=pronoun, height=2.5, font='Microsoft YaHei', pos=(5, 0), color='white')

# ————————————————experiment start: instructions————————————————————
# Page 1: Introduction Text
intro1 = f"""欢迎参加本实验！\n
本实验共分为三个阶段，\n
您的主要任务是学习并记住无意义的英文单词（简称非词）,\n
以及与其对应的标签（我、{pronoun}）之间的联结，\n
详细的实验步骤将在后续进行介绍，\n
若您已准备好开启本实验，\n
<请按空格键继续>"""

intro1 = visual.TextStim(win, 
                        text=intro1, 
                        font='Microsoft YaHei', 
                        pos=(0, 0), 
                        height=0.8, 
                        color='white', 
                        wrapWidth=30)

intro1.draw()
win.flip()
event.waitKeys(keyList=['space'])

if event.getKeys(keyList=["escape"]):
    core.quit()

# Page 2: Introduction Text
intro2 = f"""第一阶段中，屏幕中央首先会呈现一个注视点，\n
您需要将注意力保持在注视点上，\n
本阶段非词刺激会和其对应的标签（我、{pronoun}）一同出现，\n
每个非词-标签组合重复显示5遍，\n
您的目标是尽可能记住该非词所联结的标签，\n
如“ REUJZ = 我 ”，\n
<请按空格键继续>"""

intro2 = visual.TextStim(win, 
                        text=intro2, 
                        font='Microsoft YaHei', 
                        pos=(0, 0), 
                        height=0.8, 
                        color='white', 
                        wrapWidth=30)

intro2.draw()
win.flip()
event.waitKeys(keyList=['space'])

if event.getKeys(keyList=["escape"]):
    core.quit()

# Page 3: Introduction Text
intro3 = f"""本阶段没有时间限制，\n
您可以根据自己的节奏进行记忆，\n
当您认为自己已记住当前非词，\n
请按“空格键”进入下一个非词的学习，\n
进入实验后，您的鼠标就会隐藏,\n
请务必认真学习记忆，\n
<请按空格键继续>"""

intro3 = visual.TextStim(win, 
                        text=intro3, 
                        font='Microsoft YaHei', 
                        pos=(0, 0), 
                        height=0.8, 
                        color='white', 
                        wrapWidth=30)

intro3.draw()
win.flip()
event.waitKeys(keyList=['space'])

if event.getKeys(keyList=["escape"]):
    core.quit()

# Page 4: Introduction Text
intro4= f"""您将学习12个非词与标签之间的联结，\n
一共进行五轮展示，\n
<请按空格键继续>"""

intro4 = visual.TextStim(win, 
                        text=intro4, 
                        font='Microsoft YaHei', 
                        pos=(0, 0), 
                        height=0.8, 
                        color='white', 
                        wrapWidth=30)
                        
intro4.draw()
win.flip()
event.waitKeys(keyList=['space'])

if event.getKeys(keyList=["escape"]):
    core.quit()


# ————————————————define stimulus—————————————————————————

stim_path = os.path.join(parent_dir, "nonwords.csv")
print(f"stim_path:{stim_path}")

# Read the stimulus file
stim_df = pd.read_csv(stim_path)
    
def get_balanced_trials(stim_df, n_trials=12):
    """获取平衡的试验刺激"""
    # 根据被试编号构建刺激文件夹路径
    subject_id = expInfo['受试者编号'].zfill(3)  # 确保编号为3位数
    stimuli_folder = os.path.join(parent_dir, 'stimuli', f'sub-{subject_id}')
    
    # 打印路径用于调试
    print(f"刺激文件夹路径: {stimuli_folder}")
    
    # 检查路径是否存在
    if not os.path.exists(stimuli_folder):
        error_msg = f"错误: 刺激文件夹不存在 - {stimuli_folder}"
        print(error_msg)
        raise FileNotFoundError(error_msg)
    
    file_list = os.listdir(stimuli_folder)
    print(f"找到 {len(file_list)} 个文件在刺激文件夹中")
    
    valid_extensions = ('.png')
    nonword_info = []
    
    for file in file_list:
        if file.lower().endswith(valid_extensions):
            nonword = os.path.splitext(file)[0]  
            if len(nonword) >= 3:
                third_char = nonword[2].upper()
                if third_char in ('U', 'N'):
                    nonword_info.append({
                        'nonword': nonword,
                        'filename': os.path.join(stimuli_folder, file),  # 存储完整路径
                        'third_char': third_char
                    })

    # 按第三个字符分组
    u_files = [info for info in nonword_info if info['third_char'] == 'U']
    n_files = [info for info in nonword_info if info['third_char'] == 'N']

    # 打印找到的文件数量
    print(f"找到 {len(u_files)} 个U文件和 {len(n_files)} 个N文件")
    
    # 检查是否有足够的项目
    if len(u_files) < 6 or len(n_files) < 6:
        error_msg = f"需要至少6个第三个字母为U和6个为N的非词图片 (找到U: {len(u_files)}, N: {len(n_files)})"
        print(error_msg)
        raise ValueError(error_msg)

    # 创建试验列表
    trials = []
    
    # "自我"条件（1U + 1N）
    for info in u_files[:3]:
        trials.append({
            'filename': info['filename'],  # 使用完整路径
            'nonword': info['nonword'],
            'label': '我'})
            
    for info in n_files[:3]:
        trials.append({
            'filename': info['filename'], 
            'nonword': info['nonword'],
            'label': '我'})
        
    # "他/她"条件（1U + 1N）
    for info in u_files[3:6]:
        trials.append({
            'filename': info['filename'], 
            'nonword': info['nonword'],
            'label': pronoun})
            
    for info in n_files[3:6]:
        trials.append({
            'filename': info['filename'], 
            'nonword': info['nonword'],
            'label': pronoun})

    # 打乱试验顺序
    random.shuffle(trials)
        
    return pd.DataFrame(trials)
    
# create fixation point
fixation_outer = visual.Circle(
    win,
    radius=0.25, 
    edges=32,
    lineColor='black',
    fillColor=None,
    lineWidth=1.5
)
    
fixation_inner = visual.Circle(
    win,
    radius=0.10,  
    edges=32,
    fillColor='black',
    lineColor='black'
)
    
# creat image stimulus component
stim_image = visual.ImageStim(
    win,
    image=None,
    size=(36,20),
    pos=(0, 0)
)
    
# creat label text component
label_text = visual.TextStim(
    win,
    text='',
    pos=(0, -5),   
    height=2.5,    
    color='white',
    font='Microsoft YaHei'
)
    
# set exp parameters
n_blocks = 5
    
# set fixation duration
fix_duration = 0.5  
    
# get balanced trials
selected_trials = get_balanced_trials(stim_df)
    
# ————————————————experiment stage 1—————————————————————————
# learn nonwords
for block in range(n_blocks):
    for _, trial in selected_trials.iterrows():
        # present fixation point
        fixation_outer.draw()
        fixation_inner.draw()
        win.flip()
        fixation_onset = core.getTime()
        core.wait(fix_duration)
        fixation_offset = core.getTime()
        
        # present stimulus
        image_path = os.path.join('stimuli', trial['filename'])
        stim_image.image = image_path
        label_text.text = trial['label']
        
        # initialize required data records
        stim_onset = None  
        stim_offset = None  
        subject_response = None
        rt = None
        first_flip = True  
        
        # clear any previous key responses
        event.clearEvents()
        
        while True:
                
            # draw stimulus and fixation point
            stim_image.draw()
            label_text.draw()
            fixation_outer.draw()
            fixation_inner.draw()
            
            # record precise time on first flip
            if first_flip:
                stim_onset = win.flip()
                # print(stim_onset)
                first_flip = False
            else:
                win.flip()
            
            # detect key press
            keys = event.getKeys(
                keyList=['space', 'escape'],
                timeStamped=True
            )
            
            if keys:
                key_name, _ = keys[0]
                response = core.getTime()
                # print(f'response={response}')
                
                if key_name == 'space':
                    # calculate rt relative to stimulus onset
                    # convert rt to ms
                    rt = (response - stim_onset) * 1000 
                    # print(f'rt={response - stim_onset}')
                    subject_response = 'space'
                    stim_offset = core.getTime()  
                    # print(f'stim_offset={stim_offset}')
                    break  
                elif key_name == 'escape':
                    core.quit()
        win.flip()
        
        # set ITI
        ITI_onset = core.getTime()
        fixation_outer.draw()
        fixation_inner.draw()
        win.flip()
        core.wait(np.random.uniform(0.5,1.5))
        ITI_offset = core.getTime()
        
        # determine whether the participant's response was correct, '1' represents correct, '0' represents false.
        true_response = 'space'   
        if subject_response == true_response:
            correct = 1
        else:
            correct = 0
        
        # convert Chinese labels to English labels (self/other) when recording data
        condition = 'self' if trial['label'] == '我' else 'other'
        
        # record data
        data_to_write = [expInfo['受试者编号'],expInfo['年龄'],expInfo['性别'],block,'training',
        fixation_onset,fixation_offset,stim_onset,stim_offset,ITI_onset,ITI_offset,response,None,
        condition,trial['nonword'],subject_response,true_response,correct,rt,frame_rate,data.getDateStr()]
        
        dataFile.write(','.join(map(str, data_to_write)) + '\n')
        dataFile.flush() 
        
# present  ending instruction of learning phase
intro5 = f"""您已完成第一阶段的学习,\n
现在，我们将进入第二阶段，\n
在这个阶段，屏幕中央会呈现一个注视点，\n
随着注视点消失,\n
您需要判断每个非词属于哪个标签（我、{pronoun}）,\n
如果“我”在左侧，按左键“←”选择“我”，\n
如果“{pronoun}”在左侧，按左键“←”选择“{pronoun}” ，\n
请尽量准确地作出判断，\n
每个非词都需答对7次才能进入下一阶段，\n
如果您已理解实验要求，请按“ → ”键继续，\n
若仍有疑问，请按“ ← ” 键联系主试"""

intro5 = visual.TextStim(win, 
                        text=intro5, 
                        font='Microsoft YaHei', 
                        pos=(0, 0), 
                        height=0.8, 
                        color='white', 
                        wrapWidth=30)

intro5.draw()
win.flip()
    
contact_text = visual.TextStim(win, 
                              text="请联系主试", 
                              font='Microsoft YaHei',
                              pos=(0, 0), 
                              height=0.8, 
                              color='white', 
                              wrapWidth=30)

while True:
    # 等待被试响应
    keys = event.waitKeys(keyList=['left', 'right', 'escape'])
    
    if 'escape' in keys:
        core.quit()
    elif 'right' in keys:
        break  
    elif 'left' in keys:
        contact_text.draw()
        win.flip()
        event.waitKeys() 

#——————————————————————— experiment stage 2: run a test trial ——————————————————————#
# create components
feedback = visual.TextStim(win, text='', height=2.5, font='Microsoft YaHei', pos=(0, 0), color='white')
too_slow_text = visual.TextStim(win, text='太慢！', height=2.5, font='Microsoft YaHei', pos=(0, 0), color='red')

# define the function to run a test trial
def run_test_trial(trial, flip_side, block):
    subject_response = None
    stim_onset = None  
    stim_offset = None 
    rt = None 
    response = None
    
    position_map = {}

    # present fixation point
    fixation_outer.draw()
    fixation_inner.draw()
    win.flip()
    fixation_onset = core.getTime()
    core.wait(fix_duration)
    fixation_offset = core.getTime()
    
    # present nonword stimulus
    image_path = os.path.join('stimuli', trial['filename'])
    stim_image = visual.ImageStim(win, image=image_path, size=(36,20), pos=(0, 0))
    stim_onset = core.getTime() 
    stim_image.draw()
    fixation_outer.draw()
    fixation_inner.draw()
    win.flip()
    core.wait(0.9)
    stim_offset = core.getTime() 
        
    # randomly adjust the position of self and other labels
    flip_side = random.choice([True, False])
    if flip_side:
        left_option = visual.TextStim(win, text=pronoun, height=2.5, font='Microsoft YaHei', pos=(-5, 0), color='white')
        right_option = visual.TextStim(win, text='我', height=2.5, font='Microsoft YaHei', pos=(5, 0), color='white')
        position_map = {pronoun: 'left', '我': 'right'}
    else:
        left_option = visual.TextStim(win, text='我', height=2.5, font='Microsoft YaHei', pos=(-5, 0), color='white')
        right_option = visual.TextStim(win, text=pronoun, height=2.5, font='Microsoft YaHei', pos=(5, 0), color='white')
        position_map = {'我': 'left', pronoun: 'right'}

    
    # present label prompt
    fixation_outer.draw()
    fixation_inner.draw()
    left_option.draw()
    right_option.draw()
    win.flip()
        
    # record the start time of response
    label_onset = core.getTime()
    # print(f'labelonset{label_onset}')
    
    # set timeout duration
    timeout = 2.0
    responded = False
    
    # clear any previously recorded events
    event.clearEvents()
    while (core.getTime() - label_onset) < timeout:
        keys = event.getKeys(keyList=['left', 'right', 'escape'])
        if 'escape' in keys:  
            win.close()
            core.quit()
            
        if keys:
            # print(f'{keys}')
            key_name = keys[0]
            response = core.getTime()
            # print(f"response={response}")
            rt_seconds = response - label_onset
            # calculate rt (convert to ms)
            rt = rt_seconds * 1000 
            # print(f"RT (ms): {rt:.1f}")
            subject_response = key_name
            responded = True
            break
    
    if not responded:
        response = None
        rt = None
    
    # check if the participant responded correctly,'1' represent correct,'0' represent false
    true_response = position_map[trial['label']]

    correct = 1 if subject_response == true_response else 0
    
    # provide feedback
    if subject_response is None:
        too_slow_text.draw()
        core.wait(0.5)
    else:
        feedback.setText("正确！" if correct == 1 else "错误！")
        feedback.color = 'green' if correct == 1 else 'red'
        feedback.draw()
    
    win.flip()
    core.wait(0.5)
        
    # ITI interval
    ITI_onset = core.getTime()
    win.flip()
    core.wait(np.random.uniform(0.5,1.5))
    ITI_offset = core.getTime()
    
    # convert Chinese labels to English labels (self/other) when recording data
    condition = 'self' if trial['label'] == '我' else 'other'
    
    # record data
    data_to_write = [expInfo['受试者编号'],expInfo['年龄'],expInfo['性别'],None,'testing',
        fixation_onset,fixation_offset,stim_onset,stim_offset,ITI_onset,ITI_offset,response,label_onset,
        condition,trial['nonword'],subject_response,true_response,correct,rt,
        frame_rate,data.getDateStr()]
    
    dataFile.write(','.join(map(str, data_to_write)) + '\n')
    dataFile.flush()
    
    return correct, flip_side
    
# Run the full test session
def run_test_session():
    """Run the full test session"""
    
    nonword_info = selected_trials[['nonword', 'filename', 'label']].drop_duplicates()
    nonword_map = nonword_info.set_index('nonword').to_dict('index')
    
    # initialize correct count tracker
    correct_counts = {nonword: 0 for nonword in nonword_map.keys()}
    
    # continue testing until all nonwords reach 7 correct responses
    # todo 
    while any(cnt < 7 for cnt in correct_counts.values()):
        if event.getKeys(keyList=["escape"]):
            core.quit()
            
        # select a nonword that still needs testing
        remaining = [nw for nw, cnt in correct_counts.items() if cnt < 7]
        chosen_nonword = random.choice(remaining)
        trial_info = nonword_map[chosen_nonword]
        
        # randomly flip option positions 
        flip_side = random.choice([True, False])
        
        # run trial and retrive correctness value
        correct_value, _ = run_test_trial({  
            'filename': trial_info['filename'],
            'label': trial_info['label'],
            'nonword': chosen_nonword
        }, flip_side, block=None)  # Added None for block parameter

        # increase count only if response was correct
        if correct_value == 1:
            correct_counts[chosen_nonword] += 1
        
run_test_session()   
    
# ——————————————————————— experiment stage 3 ——————————————————————
intro6 = f"""您已完成第二阶段的测试，\n
现在我们将进入第三阶段，\n
在这个阶段，测试将分为12组，每组之间您会有短暂的休息时间，\n
你仍需判断非词属于“我”还是“{pronoun}”，\n
如果“我”在左侧，按左键“←”选择“我”，\n
如果“{pronoun}”在左侧，按左键“←”选择“{pronoun}” ，\n
注意，最后三组每组的正确率都需达到90%及以上才算通过，\n
如果您准备好了，\n
<请按空格键继续>"""

intro6 = visual.TextStim(win, 
                        text=intro6, 
                        font='Microsoft YaHei', 
                        pos=(0, 0), 
                        height=0.8, 
                        color='white', 
                        wrapWidth=30)

intro6.draw()
win.flip()

event.waitKeys(keyList=['space'])

if event.getKeys(keyList=["escape"]):
    core.quit()

# ————————————————— experiment stage 3: formal test phase ————————————————
n_formal_blocks = 12
trials_per_block = 60
required_accuracy = 0.9

# creat feedback components
feedback_text = visual.TextStim(win, text='', color='white', height=2.5, font='Microsoft YaHei')
too_slow_text = visual.TextStim(win, text='太慢！', color='red', height=2.5, font='Microsoft YaHei')

# define function to 'generate formal trials'
def generate_formal_trials(learned_trials, n_trials):
    """
    Parameters：
    'learned_trials': trial data used in the learning phase
    'n_trials': number of trials to generate
    """
    # extract learned non-words from the learning phase data
    learned_nonwords = learned_trials[['nonword', 'label', 'filename']].drop_duplicates()
    
    # calculate the number of repetitions for each non-word
    base_repeats = n_trials // len(learned_nonwords)
    remaining = n_trials % len(learned_nonwords)
    
    # create trial list
    trials = []
    for _ in range(base_repeats):
        trials.extend(learned_nonwords.to_dict('records'))
    
    # add remaining trials
    if remaining > 0:
        trials.extend(learned_nonwords.sample(remaining).to_dict('records'))
    
    # shuffle the order
    random.shuffle(trials)
    return trials[:n_trials]

# —————————————————experiment stage 3: define 'run_formal_trial'—————————————————
def run_formal_trial(trial, flip_side, block):
    # initialize response variables
    subject_response = None
    rt = None
    stim_onset = None
    stim_offset = None 
    response = None
    true_response = None
    position_map = {}
    
    # present fixation point
    fixation_outer.draw()
    fixation_inner.draw()
    win.flip()
    fixation_onset = core.getTime()
    core.wait(fix_duration)
    fixation_offset = core.getTime()
        
    # present stimulus
    image_path = os.path.join('stimuli', trial['filename'])
    stim_image = visual.ImageStim(win, image=image_path, size=(36,20), pos=(0, 0))
    stim_onset = core.getTime()
    stim_image.draw()
    fixation_outer.draw()
    fixation_inner.draw()
    win.flip()
    core.wait(0.9)
    stim_offset = core.getTime()
        
    # randomly adjust the position of 'self' and 'other'
    left_option = visual.TextStim(win, text='', height=2.5, font='Microsoft YaHei', pos=(-5, 0), color='white')
    right_option = visual.TextStim(win, text='', height=2.5, font='Microsoft YaHei', pos=(5, 0), color='white')
    
    if flip_side:
        left_option.text = pronoun
        right_option.text = '我'
        position_map['我'] = 'right'
        position_map[pronoun] = 'left'
    else:
        left_option.text = '我'
        right_option.text = pronoun
        position_map['我'] = 'left'
        position_map[pronoun] = 'right'
    
    # display label prompt
    fixation_outer.draw()
    fixation_inner.draw()
    left_option.draw()
    right_option.draw()
    win.flip()
    label_onset = core.getTime()
        
    # define timeout control
    timeout = 2.0
    responded = False
    
    # Clear any events that were previously recorded
    event.clearEvents()
    
    while (core.getTime() - label_onset) < timeout:
        keys = event.getKeys(keyList=['left', 'right', 'escape'], timeStamped=True)
        
        if keys:
            key_name, _ = keys[0]
            if key_name == 'escape':
                win.close()
                core.quit()
                
            response = core.getTime()
            
            # compute rt (convert to ms)
            rt_seconds = response - label_onset
            
            rt = rt_seconds * 1000 
            # print(f"RT (ms): {rt:.1f}")
            
            subject_response = key_name
            responded = True
            break
    
    if not responded:
        response = None
        rt = None
        
    if trial['label'] == '我':
        true_response = position_map['我']
    else:
        true_response = position_map[pronoun] 
    
    correct = 1 if subject_response == true_response else 0
    
    # display feedback
    if subject_response is None:
        too_slow_text.draw()
        core.wait(0.5)
    else:
        feedback_text.text = "正确！" if correct == 1 else "错误！"
        feedback_text.color = 'green' if correct == 1 else 'red'
        feedback_text.draw()
    
    win.flip()
    core.wait(0.5)
        
    # ITI interval
    ITI_onset = core.getTime()
    fixation_outer.draw()
    fixation_inner.draw()
    win.flip()
    core.wait(np.random.uniform(0.5,1.5))
    ITI_offset = core.getTime()
    
    # convert Chinese labels to English labels (self/other) when recording data
    condition = 'self' if trial['label'] == '我' else 'other'
    
    # record data 
    data_to_write = [expInfo['受试者编号'],expInfo['年龄'],expInfo['性别'],block,'formal_test',
                fixation_onset,fixation_offset,stim_onset,stim_offset,ITI_onset,ITI_offset,response,label_onset,
                condition,trial['nonword'],subject_response,true_response,correct,
                rt,frame_rate,data.getDateStr()]
        
    dataFile.write(','.join(map(str, data_to_write)) + '\n')
    dataFile.flush()
    
    return correct == 1

# ———————————————————————exp stage3: run the Formal Test Phase—————————————————————
total_correct = 0
total_trials = 0
block_accuracies = []

for block in range(n_formal_blocks):
    trials = generate_formal_trials(selected_trials, trials_per_block)
    block_correct = 0
    
    for trial in trials:
        flip_side = random.choice([True, False])
        is_correct = run_formal_trial(trial, flip_side, block)
        total_trials += 1
        if is_correct:
            total_correct += 1
            block_correct += 1
            
    # calculate current block's accuracy
    block_accuracy = block_correct / trials_per_block
    block_accuracies.append(block_accuracy)
    
    # present current block's info
    block_info = visual.TextStim(win,
        text=f"block {block+1}/{n_formal_blocks} 完成\n正确率: {block_accuracy:.1%}\n"
        "您有1分钟的休息时间\n若已准备好进入下一组，请随时按'空格键'继续",
        font='Microsoft YaHei',
        height=0.8,
        color='white'
    )
    block_info.draw()
    win.flip()
    core.wait(0.5)
    # Wait for up to 60 seconds; if the user presses the space key, proceed immediately
    event.waitKeys(maxWait=60, keyList=['space'])

# check if the last three blocks all meet the criteria
required_blocks = 3
if len(block_accuracies) >= required_blocks:
    last_three_blocks = block_accuracies[-required_blocks:]
    passed = all(acc >= required_accuracy for acc in last_three_blocks)  # Changed 0.9 to required_accuracy
else:
    passed = False
    
# ——————————————————————— experiment end——————————————————————
final_message = visual.TextStim(win,
    text="恭喜完成实验任务！\n请按空格键退出" if passed else "未达到实验通过标准\n请按空格键退出\n联系主试。",
    font='Microsoft YaHei',
    height=0.8,
    color='white',
)

final_message.draw()
win.flip()
event.waitKeys(keyList=['space'])

# close window
dataFile.close()
win.close()
core.quit()