#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Behavior experiment Procedure

Created February 10, 2025, 11:57
Author: Shanshan Zhu(zhushanshan0717@gmail.com)

For inquiries, please contact the author.
"""
# 导入相应模块
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

#————————————————记录被试信息———————————————#
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

#————————————————创建实验窗口———————————————#
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=False,
                    color='grey')
win.setMouseVisible(False)
monitor = Monitor(name='testMonitor')

#————————————————创建默认键盘对象，用于检测按键事件———————————————#
# Create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

#————————————————创建实验数据文件夹———————————————#
fileName = f"data/Exp1_task1_{expInfo['受试者编号']}" + '.csv'
os.makedirs(os.path.dirname(fileName), exist_ok=True)  # Ensure directory exists
dataFile = open(fileName, 'w')
dataFile.write('fixation_onset,fixation_offset,cue_onset,cue_offset,target_onset,target_offset,ITI_onset,ITI_offset,')
dataFile.write('condition,prior,rt,response,correct,orientation,stage,keypress,')
dataFile.write('refreshrate,time,age,sex,subj_index,block_index,subj_idx,block\n')

#——————————————————————# 实验前的指导语 #————————————————————————#

stimuli = pd.read_csv('demo_stimuli2.csv')

#————————————————设置实验开始前的指导语——————————————————#
def display_instruction(text):
    instruction = visual.TextStim(win, 
                                text=text, 
                                font='Arial Unicode MS', 
                                pos=(0, 0), 
                                height=0.8, 
                                color='white', 
                                wrapWidth=30)
    instruction.draw()
    win.flip()
    # Wait for space key to continue
    keys = event.waitKeys(keyList=['space'])
    if 'space' in keys:
        return

# Page 1: Introduction Text
intro_text1 = """欢迎参加本实验！\n\n
本实验共分为两个阶段：\n\n
第一阶段需要您学习无意义的英文单词与特定标签的匹配，\n
例如"REUJZ"代表"self"。\n\n
学习完成后将进入第二阶段测试，\n
测试阶段正确率需达到90%以上才能进入后续fMRI实验。\n\n
如果已清楚本实验要求\n\n
<请按空格键继续>"""
display_instruction(intro_text1)

# Page 2: Introduction Text
intro_text2 = """+\n\n\n
屏幕中心会出现一个注视点,\n
您需要注意力保持在注视点上\n
接下来请将右手食指放在“←”键上,\n
手中指放在“→”键上,\n
左手放在空格键上以便接下来进行反应\n\n
<请按空格键继续>"""

display_instruction(intro_text2) 

# Page 3: Introduction Text
intro_text3 = """请将右手食指放在“ ← ” 上\,n
右手中指放在 “ → ” 上,\n
左手放在空格键上以便接下来进行反应,\n\n
<请按空格键继续>"""

display_instruction(intro_text3)

# Page 4: Introduction Text
intro_text4 = """第一阶段为学习阶段,\n
您需要学习无意义的英文单词和标签之间的联结,\n
进入实验后，您的鼠标就会隐藏,\n\n
<请按空格键继续>"""

display_instruction(intro_text4)

# Page 5: Introduction Text
intro_text5 = """在学习阶段,\n
屏幕中央会出现一个无意义的英文单词（在后续的实验中统称为非词）,\n
您需要记住该非词与标签（Self、Other）之间的联结,\n
Self指代自己，Other指代他人，\n\n
如果已理解实验要求，请按‘ → ’键继续，
若仍有疑问，请按‘ ←’ 键联系主试"""

display_instruction(intro_text5)

# 显示说明
instruction_text = visual.TextStim(win, text=intro_text5, pos=(0, 0), color="white", font='Arial Unicode MS', height=0.8, wrapWidth=30)
instruction_text.draw()
win.flip()
#———————————————————# 行为实验阶段 #—————————————————————#

# 等待被试按键
keys = event.waitKeys(keyList=['left', 'right'])

if 'right' in keys:
    # 显示进入学习阶段的指导语
    learning_text = visual.TextStim(win, 
                                    text="接下来将进入学习阶段，您一共需要学习20个非词与标签之间的联结", 
                                    wrapWidth=30, 
                                    color="white", 
                                    font='Arial Unicode MS', 
                                    pos=(0, 0), 
                                    height=0.8)
    learning_text.draw()
    win.flip()
    # 进入学习阶段的指导语呈现2s
    core.wait(2)  

    # 读取刺激材料
    stimuli_df = pd.read_csv('demo_stimuli2.csv')

    # 学习阶段：呈现非词和标签的对应关系
    for index, row in stimuli_df.iterrows():
        nonword = row['nonwords']
        label = row['label']
        display_text = f"{nonword} = {label}"
        stimulus_text = visual.TextStim(win, 
                                        text=display_text, 
                                        wrapWidth=30, 
                                        color="white", 
                                        pos=(0, 0), 
                                        height=0.8)
        stimulus_text.draw()
        win.flip()
        # 每个非词刺激呈现2s
        core.wait(2)  

        # 进入测试阶段
        test_instr = """接下来我们将对刚才学习的非词和标签联结进行测试,\n
        在这一测试中，屏幕中央会呈现一个非词，您需要判断该非词属于self还是other,\n
        按左键‘ ←’ 代表self（自己），\n
        按右键‘ → ’代表other（他人），\n
        如果您已经准备好了，\n
        请按右键‘ → ’开始正式测试，\n
        如果您想再学习一遍非词，请按左键‘ ← ’"""

        # 呈现测试阶段指导语
        test_instr_text = visual.TextStim(win, 
            text=test_instr, 
            wrapWidth=30, 
            color="white",
            font='Arial Unicode MS',
            pos=(0, 0),  
            height=0.8)    

        # 显示测试阶段的指导语
        test_instr_text.draw()
        win.flip()

        # 等待用户按键
        keys = event.waitKeys(keyList=['left', 'right'])
        
        # 创建刺激元素
        word_stim = visual.TextStim(win, text='', height=0.1, pos=(0, 0.2))
        left_option = visual.TextStim(win, text='self', pos=(-0.3, -0.2))
        right_option = visual.TextStim(win, text='other', pos=(0.3, -0.2))
        feedback = visual.TextStim(win, text='', pos=(0, -0.4), color='yellow')
        
        # 定义测试阶段的函数
        def run_trial(word, correct_answer):
            word_stim.text = word
            while True:
                # 绘制所有刺激
                word_stim.draw()
                left_option.draw()
                right_option.draw()
                win.flip()
                
                # 等待被试反应（只接受左右方向键）
                keys = event.waitKeys(keyList=['left', 'right'])
                
                # 获取被试反应
                response = keys[0]
                
                # 判断正确性并设置反馈
                if response == correct_answer:
                    feedback.text = "Correct!"
                    feedback.color = 'green'
                    correct = True
                else:
                    feedback.text = "Wrong!"
                    feedback.color = 'red'
                    correct = False
                
                # 显示反馈
                feedback.draw()
                win.flip()
                core.wait(1)  # 显示反馈1秒
                
                return correct

        # 主试次循环
        while True:
            errors = []
            for index, row in data.iterrows():
                word = row['nonwords']
                correct_answer = 'left' if row['label'] == 'self' else 'right'
                
                # 等待用户按键
                keys = event.waitKeys(keyList=['left', 'right'])
                
                if 'right' in keys:
                    correct = run_trial(word, correct_answer)
                    if not correct:
                        errors.append(row)
                elif 'left' in keys:
                    continue  # 重新进入学习阶段
            
            # 如果没有错误，结束循环
            if not errors:
                break
            
            # 否则，重新测试错误的单词
            data = pd.DataFrame(errors)

# 关闭窗口
win.close()
core.quit()