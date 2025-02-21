#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Behavior experiment Procedure

Created February 10, 2025, 11:57
Author: Shanshan Zhu(zhushanshan0717@gmail.com)

For inquiries, please contact the author.
"""

from psychopy import visual, core, event, data, gui
from psychopy.hardware import keyboard
import numpy as np
import pandas as pd
import os
from psychopy.monitors import Monitor
from helper_functions import *
import random  # Ensure random module is imported
from psychopy.iohub import launchHubServer
import matplotlib.pyplot as plt

#——————————————————————————————————————————#
# Fill the information
expInfo = {'测试时间': data.getDateStr(),
           '受试者编号': '000',
           '年龄': '',
           '性别': ['Male', 'Female']}
dlg = gui.DlgFromDict(dictionary=expInfo,
                      title='基本信息',
                      fixed=['测试时间'])
if dlg.OK == False:
    core.quit()

# Create experiment window
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=False,
                    color='grey')
win.setMouseVisible(False)
monitor = Monitor(name='testMonitor')

# Create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

#—————————————————————# task1 Introduction #—————————————————————————#
# Create Data
fileName = f"data/Exp1_task1_{expInfo['受试者编号']}" + '.csv'
os.makedirs(os.path.dirname(fileName), exist_ok=True)  # Ensure directory exists
dataFile = open(fileName, 'w')
dataFile.write('fixation_onset,fixation_offset,cue_onset,cue_offset,target_onset,target_offset,ITI_onset,ITI_offset,')
dataFile.write('condition,prior,rt,response,correct,orientation,stage,keypress,')
dataFile.write('refreshrate,time,age,sex,subj_index,block_index,subj_idx,block\n')

#——————————————————————# Task-study stage #————————————————————————#
#——————————————————————# 实验前的指导语 #————————————————————————#

stimuli = pd.read_csv('demo_stimuli2.csv')

# 设置开始指导语前新增实验总指导语
# 实验总指导语
instruction = visual.TextStim(win,
                    name='text',
                    text='欢迎参加本实验！\n\n'
                    '本实验共分为两个阶段：\n\n'
                    '第一阶段需要您学习无意义的英文单词与特定标签的匹配，\n'
                    '例如"REUJZ = self"。\n\n'
                    '学习完成后将进入第二阶段测试，\n'
                    '测试阶段正确率需达到90%以上才能进入后续fMRI实验。\n\n'
                    '如果已理解实验要求，请按‘→’键继续\n'
                    '若仍有疑问，请按‘←’键联系主试',
                    font='Arial Unicode MS',
                    alignText='center',
                    height= 1.2,
                    units='deg',
                    color='white',
                    pos=[0, 0])
end = False

while end == False:
    show_instruction(win=win,monitor=monitor,expInfo=expInfo,exp=1,task=1 ,start=True)
    event.clearEvents()
    breakthisloop = False
    while True:
        if breakthisloop:
            # Break out of the main loop if the flag is set
            break
        instruction.draw()
        win.flip()
        # Check for key presses ('left' or 'right')
        for key in event.getKeys(keyList=['left', 'right']):
            if key == 'left':
                # If 'left' is pressed, do not end the practice
                end = False
                breakthisloop = True
            elif key == 'right':
                end = True
                breakthisloop = True
        if breakthisloop:
            break
    # If a key was pressed, break out of the main loop
    if end:
        break

# 显示并等待响应
purpose_text.draw()
win.flip()

# 设置有效按键
valid_keys = ['right', 'left']
key_resp = event.waitKeys(keyList=valid_keys)

# 处理按键响应
if 'left' in key_resp:
    # 显示联系主试提示
    contact_text = visual.TextStim(win,
        text='请立即联系主试人员\n\n（按任意键退出）',
        font='Arial Unicode MS',
        alignText='center',
        height= 1.2,
        units='deg',
        color='white',
        pos=[0, 0])
    contact_text.draw()
    win.flip()
    event.waitKeys()  # 等待任意键
    win.close()
    core.quit()
    
# 设置开始指导语
instructions_text = visual.TextStim(win, 
    text=f'接下来将进入学习阶段\n\n（按空格键继续）',
    languageStyle= 'RTL',
    font='Arial Unicode MS',
    alignText='center',
    height = 1.2, 
    units = 'deg',
    depth=0.0,
    color = 'white',
    pos = [0, 0])

# 显示指导语，等待按空格键继续
instructions_text.draw()
win.flip()
event.waitKeys(keyList=["space"])

#——————————————————————# 实验学习阶段 #————————————————————————#

# 将学习阶段封装成函数
def run_learning_phase():
    for index, row in stimuli.iterrows():
        # 创建刺激文本
        stim_display = visual.TextStim(win,
            text = f"{row['nonwords']} = {row['label']}",
            height = 1.2, 
            units = 'deg',
            font='Arial Unicode MS',
            color = 'white',
            depth=0.0,
            alignText='center',
            pos = [0,0])
        
        # 显示刺激
        stim_display.draw()
        win.flip()
        
        # 记录按键响应
        event.waitKeys(keyList=["space"])  # 仅响应空格键
        
        # 在每次刺激后等待至少1秒
        core.wait(1.0)

# 初始学习阶段
run_learning_phase()

# 添加重新学习选择提示
retry = True
while retry:
    # 创建提示文本
    retry_text = visual.TextStim(win,
        text='如果您没有记住所有非词与标签的对应关系\n请按 R 键 重新学习\n\n如果已记住，请按 C 键 对所学的非词进行回忆',
        font='Arial Unicode MS',
        alignText='center',
        height=1.2,
        units='deg',
        color='white',
        wrapWidth=25,
        pos=[0,0])
    
    # 显示并等待响应
    retry_text.draw()
    win.flip()
    keys = event.waitKeys(keyList=['r', 'c'])
    breakthisloop = False
    while True:
        if breakthisloop:
            # Break out of the main loop if the flag is set
            break
        # Check for key presses ('r' or 'c')
        for key in event.getKeys(keyList=['r', 'c']):
            if key == 'r':
                # If 'left' is pressed, do not end the practice
                retry = True
                run_learning_phase() 
                breakthisloop = True
            elif key == 'c':
                retry = False
                breakthisloop = True
        if breakthisloop:
            break

# 将测试阶段封装成函数
def run_testing_phase(stimuli_to_test):
    wrong_items = []  # 记录答错的条目
    random.shuffle(stimuli_to_test)  # 随机打乱顺序
    
    for index, row in stimuli_to_test.iterrows():
        # 创建刺激文本（只显示非词）
        test_stim = visual.TextStim(win,
            text = f"{row['nonwords']}",
            height = 1.5, 
            units = 'deg',
            font='Arial Unicode MS',
            color = 'white',
            alignText='center',
            pos = [0,0])
        
        # 创建反应提示
        prompt = visual.TextStim(win,
            text = "左键 = self\n右键 = other",
            height = 0.8,
            pos = (0, -5),
            color = 'white')
        
        # 显示刺激和提示
        test_stim.draw()
        prompt.draw()
        win.flip()
        
        # 记录反应时间和按键
        timer = core.Clock()
        keys = event.waitKeys(keyList=['left', 'right'], timeStamped=timer)
        response, rt = keys[0]
        
        # 判断正确性
        correct = (response == 'left' and row['label'] == 'self') or \
                  (response == 'right' and row['label'] == 'other')
        
        # 错误反馈
        if not correct:
            feedback = visual.TextStim(win,
                text = f"正确对应：{row['nonwords']} = {row['label']}",
                color = 'red',
                height = 1.2)
            
            feedback.draw()
            win.flip()
            core.wait(1.5)  # 显示反馈1.5秒
            wrong_items.append({'stimulus': row['nonwords'], 'response': response, 'correct_answer': row['label'], 'rt': rt})  # 记录更多反馈信息
    
    return pd.DataFrame(wrong_items)  # 返回错误条目

# 主学习-测试循环
while True:
    # 初始学习阶段
    run_learning_phase()
    
    # 首次测试所有项目
    wrong_items = run_testing_phase(stimuli)
    
    # 如果没有错误，退出循环
    if wrong_items.empty:
        break
    
    # 错误重学机制
    retry_text = visual.TextStim(win,
        text=f'您有{len(wrong_items)}个条目需要重新学习\n\n按空格键开始针对性练习',
        height=1.2,
        color='white')
    
    retry_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])
    
    # 针对错误项再次学习
    run_learning_phase(pd.DataFrame(wrong_items))

# 最终通过提示
transition_text = visual.TextStim(win,
    text='恭喜您已掌握所有非词！\n\n接下来将进入测试阶段\n\n（按空格键继续）',
    height=1.2,
    color='white')

transition_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

#——————————————————————# 实验测试阶段 #————————————————————————#

#——————————————————————# 实验结束 #————————————————————————#
# 确保所有数据保存
dataFile.close()

# 关闭窗口
win.close()
core.quit()