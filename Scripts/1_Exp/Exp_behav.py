#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Experiment 1 Procedure

Created: Feburary 9, 2025, 11:57
Author: Shanshan Zhu(zhushanshan0717@gmail.com)

For inquiries, please contact the author.
"""

# 导入需要的库
from psychopy import visual, event, core, data, gui
from psychopy.hardware import keyboard
import numpy as np
import pandas as pd
import os
from psychopy.monitors import Monitor
import random  
from psychopy.iohub import launchHubServer
import matplotlib.pyplot as plt

#—————————————————————记录被试信息—————————————————————————#
expInfo = {'测试时间': data.getDateStr(),
           '受试者编号': '000',
           '年龄': '',
           '性别': ['Male', 'Female']}
dlg = gui.DlgFromDict(dictionary=expInfo,
                      title='基本信息',
                      fixed=['测试时间'])
if dlg.OK == False:
    core.quit()
    
#—————————————根据被试性别匹配不同标签（他/她）—————————————————#
# 确定代词
if expInfo['性别'] == 'Female':
    pronoun = '她'
else:
    pronoun = '他'

#—————————————————————创建实验窗口—————————————————————————#
monitor = Monitor(name='testMonitor')
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=True,
                    color='grey')

# 隐藏鼠标光标
win.setMouseVisible(False)

defaultKeyboard = keyboard.Keyboard(backend='iohub')

#——————————————————————创建实验数据文件夹—————————————————————#
fileName = f"data/Exp1_task1_{expInfo['受试者编号']}" + '.csv'
os.makedirs(os.path.dirname(fileName), exist_ok=True)  
dataFile = open(fileName, 'w')
dataFile.write('subject_id,age,gender,block,stage,fixation_onset,fixation_offset,'
                'stim_onset,stim_offset,ITI_onset,ITI_offset,response,label_onset,'
                'condition,nonword,subject_response,true_response,correct,rt,'
                'frame_rate,date,\n')

#———————————————————设置实验开始前的默认参数和组件————————————————————#
# 设置实验组件
left_option = visual.TextStim(win, text='我', height=1.8, font='Arial Unicode MS', pos=(-5, 0), color='white')
right_option = visual.TextStim(win, text=pronoun, height=1.8, font='Arial Unicode MS', pos=(5, 0), color='white')

# 设置默认参数
frame_rate = 60.0

#————————————————实验前：指导语———————————————#
def display_instruction(text, valid_keys=None):
    instruction = visual.TextStim(win, 
                                text=text, 
                                font='Arial Unicode MS', 
                                pos=(0, 0), 
                                height=0.8, 
                                color='white', 
                                wrapWidth=30)
    instruction.draw()
    win.flip()
    
    if valid_keys is not None:
        keys = event.waitKeys(keyList=valid_keys)
        if 'right' in keys:  
            return "continue"
        elif 'left' in keys:  
            return "contact"
    else:
        keys = event.waitKeys(keyList=['space'])
        if 'space' in keys:
            return
            
# Page 1: Introduction Text
intro_text1 = f"""欢迎参加本实验！\n
本实验共分为两个阶段：\n
第一阶段需要您学习无意义的英文单词（在后续的实验中统称为非词）与标签（我、{pronoun}）的联结，\n
例如"REUJZ = 我"，\n
第一阶段无需进行按键反应，\n
如果您已了解本阶段的实验要求，\n
<请按空格键继续>"""

display_instruction(intro_text1)

# Page 2: Introduction Text
intro_text2 = """接下来请将右手食指放在“←”键上,\n
右手中指放在“→”键上,\n
左手放在空格键上以便接下来进行反应\n
<请按空格键继续>"""

display_instruction(intro_text2) 

# Page 3: Introduction Text
intro_text3 = f"""在第一阶段,\n
屏幕中心会出现一个注视点,\n
您需要将注意力保持在注视点上,\n
随着注视点消失,\n
您需要学习记忆非词和标签（我、{pronoun}）的联结,\n
进入实验后，您的鼠标就会隐藏,\n
如果已理解实验要求，请按“ → ”键继续，\n
若仍有疑问，请按“ ← ” 键联系主试"""

# Update the function call to listen for both keys
result = display_instruction(intro_text3, valid_keys=['right', 'left'])

if result == "continue":
    loading_text = visual.TextStim(win, 
                                text="您将学习12个非词与标签之间的联结，一共进行两轮展示。", 
                                font='Arial Unicode MS', 
                                color='white',
                                pos=(0, 0),
                                height=0.8,
                                wrapWidth=30)
    # 使文本刺激可以在屏幕上显示
    loading_text.draw()
    # 更新窗口内容
    win.flip()
    # 文本内容持续显示1.5s
    core.wait(1.5)  
    
    stim_df = pd.read_csv("demo_stimuli2.csv")
    
    def get_balanced_trials(stim_df, n_trials=2):
        # 从stim_df中随机选取不重复的n_trials个nonwords
        stimuli_folder = 'stimuli'
        file_list = os.listdir(stimuli_folder)
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
                            'filename': file,
                            'third_char': third_char
                        })

        # 按第三个字符分组
        u_files = [info for info in nonword_info if info['third_char'] == 'U']
        n_files = [info for info in nonword_info if info['third_char'] == 'N']

        # 检查数量是否足够
        if len(u_files) < 3 or len(n_files) < 3:
            raise ValueError("需要至少6个第三个字母为U和6个为N的非词图片")

        # 随机选择并分配
        random.shuffle(u_files)
        random.shuffle(n_files)
        
        # 创建试次列表
        trials = []
        # 我-条件 (3U + 3N)
        for info in u_files[:3] + n_files[:3]:
            trials.append({
            'filename': info['filename'], 
            'nonword': info['nonword'],
            'label': '我'})
        # 他-条件 (3U + 3N)
        for info in u_files[3:6] + n_files[3:6]:
            trials.append({
            'filename': info['filename'], 
            'nonword': info['nonword'],
            'label': pronoun})

        # 打乱顺序
        random.shuffle(trials)
            
        return pd.DataFrame(trials)
        
    # 创建注视点
    fixation_outer = visual.Circle(
    win,
    radius=0.4, 
    edges=32,
    lineColor='black',
    fillColor=None,
    lineWidth=1.5
    )
    
    fixation_inner = visual.Circle(
    win,
    radius=0.15,  
    edges=32,
    fillColor='black',
    lineColor='black'
    )
    
    # 创建图片刺激组件
    stim_image = visual.ImageStim(
    win,
    image=None,
    size=(36,20),
    pos=(0, 2)
    )
    
    # 创建标签文本组件
    label_text = visual.TextStim(
        win,
        text='',
        pos=(0, -3),   
        height=2.5,    
        color='white',
        font='Arial Unicode MS'
    )
    
    # 设置实验参数
    n_blocks = 5
    
    # 注视点持续时间
    fix_duration = 0.5  
    
    # 获取平衡试次
    selected_trials = get_balanced_trials(stim_df)
    
    #———————————————————————学习阶段——————————————————————#
    # 学习非词
    for block in range(n_blocks):
        for _, trial in selected_trials.iterrows():
            # 呈现注视点
#            fixation_outer.draw()
#            fixation_inner.draw()
            win.flip()
            fixation_onset = core.getTime()
            core.wait(fix_duration)
            fixation_offset = core.getTime()
            
            # 呈现刺激
            image_path = os.path.join('stimuli', trial['filename'])
            stim_image.image = image_path
            label_text.text = trial['label']
        
            # 初始化所需记录的数据
            stim_onset = None  
            stim_offset = None  
            subject_response = None
            rt = None
            first_flip = True  
            
            # 清除按键反应数据
            event.clearEvents()
            
            while True:
                # 绘制刺激
                stim_image.draw()
                label_text.draw()
                
                # 首次刷新记录精确时间
                if first_flip:
                    stim_onset = win.flip()
                    print(stim_onset)
                    first_flip = False
                else:
                    win.flip()
                
                # 检测按键
                keys = event.getKeys(
                    keyList=['space', 'escape'],
                    timeStamped=True
                )
                
                if keys:
                    key_name, _ = keys[0]
                    response = core.getTime()
                    print(f'response={response}')
                    
                    if key_name == 'space':
                        # 计算相对于选项显示开始的时间
                        rt = (response - stim_onset) * 1000 # 转换为毫秒
                        print(f'rt={response - stim_onset}')
                        subject_response = 'space'
                        stim_offset = core.getTime()  
                        print(f'stim_offset={stim_offset}')
                        break  
                    elif key_name == 'espace':
                        core.quit()
            
            win.flip()
            
            # 试次间隔
            ITI_onset = core.getTime()
            win.flip()
            core.wait(np.random.uniform(0.5,1.5))
            ITI_offset = core.getTime()
            
            # 确定正确答案
            true_response = 'space'   
            
            # 判断被试是否正确
            if subject_response == true_response:
                correct = 1  # 正确
            else:
                correct = 0  # 错误
            
            # 将中文标签（我/他）记录为英文标签（self/other）
            condition = 'self' if trial['label'] == '我' else 'other'
            
            # 记录数据
            data_to_write = [expInfo['受试者编号'],expInfo['年龄'],expInfo['性别'],block,'training',
            fixation_onset,fixation_offset,stim_onset,stim_offset,ITI_onset,ITI_offset,response,None,
            condition,trial['nonword'],subject_response,true_response,correct,rt,frame_rate,data.getDateStr()]
            
            dataFile.write(','.join(map(str, data_to_write)) + '\n')
            dataFile.flush() 

    #———————————————————————学习阶段结束指导语——————————————————————#
    
    end_study= f"""学习阶段结束！\n
    接下来我们将对刚才学习内容进行测试，\n
    在屏幕中央的注视点消失后，会随机呈现一个非词，\n
    您需要判断该非词属于“我” 还是 “{pronoun}” ，\n
    按左键 '←' 代表“我”， \n
    按右键 '→' 代表“{pronoun}”，\n
    如果您已经准备好了，\n
    <请按空格键开始正式测试>"""
    
    study_end_text = visual.TextStim(win,
        text=end_study,  
        font='Arial Unicode MS',
        pos=(0, 0),
        color='white',
        height=0.8,
        wrapWidth=30,          
        units='deg'
        )
        
    study_end_text.draw()
    win.flip()

    # 按空格键开始学习阶段的测试
    event.waitKeys(keyList=['space'])
    
    #———————————————————————学习阶段的测试——————————————————————#
    # 创建组件
    feedback = visual.TextStim(win, text='', height=1.2, font='Arial Unicode MS', pos=(0, 0), color='white')
    too_slow_text = visual.TextStim(win, text='太慢！', height=1.2, font='Arial Unicode MS', pos=(0, 0), color='red')
    
    # 定义运行函数
    def run_test_trial(trial, flip_side, block):
        subject_response = None
        stim_onset = None  
        stim_offset = None 
        rt = None 
        response = None
        true_response = 'left' if trial['label'] == '我' else 'right'
        
        # 注视点
        fixation_outer.draw()
        fixation_inner.draw()
        win.flip()
        fixation_onset = core.getTime()
        core.wait(fix_duration)
        fixation_offset = core.getTime()
        
        # 呈现非词刺激
        image_path = os.path.join('stimuli', trial['filename'])
        stim_image = visual.ImageStim(win, image=image_path, size=(36,20), pos=(0, 0))
        stim_onset = core.getTime() 
        stim_image.draw()
        win.flip()
        core.wait(0.9)
        stim_offset = core.getTime() 

        # 随机调整 self 和 other 的位置
        flip_side = random.choice([True, False])
        if flip_side:
            left_option = visual.TextStim(win, text=pronoun, height=1.8, font='Arial Unicode MS', pos=(-5, 0), color='white')
            right_option = visual.TextStim(win, text='我', height=1.8, font='Arial Unicode MS', pos=(5, 0), color='white')
        else:
            left_option = visual.TextStim(win, text='我', height=1.8, font='Arial Unicode MS', pos=(-5, 0), color='white')
            right_option = visual.TextStim(win, text=pronoun, height=1.8, font='Arial Unicode MS', pos=(5, 0), color='white')
        
        # 呈现标签提示
        fixation_outer.draw()
        fixation_inner.draw()
        left_option.draw()
        right_option.draw()
        win.flip()
        # 记录开始按键的时间
        label_onset = core.getTime()
        print(f'labelonset{label_onset}')
        
        # 设置超时时间
        timeout = 2.0
        responded = False
        while (core.getTime() - label_onset) < timeout:
            keys = event.getKeys(keyList=['left', 'right'], timeStamped=True)
            
            if keys:
                key_name, _ = keys[0]
                response = core.getTime()
                
                print(f"response={response}")
                
                # 计算反应时（转换为ms）
                rt = (response - label_onset) * 1000 
                print(f"rt={response - label_onset}")
            
                subject_response = key_name
                responded = True
                break
        
        if not responded:
            response = None
            rt = None
        
        # 判断正确性
        correct = False
        if trial['label'] == '我':
            true_response = 'left'
        elif trial['label'] == pronoun:
            true_response = 'right'

        # 判断被试是否正确
        if subject_response == true_response:
            correct = 1  # 正确
        else:
            correct = 0  # 错误
        
        # 判断正确性并给出反馈
        if subject_response is None:
            too_slow_text.draw()
            core.wait(0.5)
        else:
            if correct == 1:
                feedback.setText("正确！")
                feedback.color = 'green' 
            else:
                feedback.setText("错误！")
                feedback.color = 'red' 
            feedback.draw()
        
        win.flip()
        core.wait(0.5)
            
        # 试次间隔
        ITI_onset = core.getTime()
        win.flip()
        core.wait(np.random.uniform(0.5,1.5))
        ITI_offset = core.getTime()
        
        condition = 'self' if trial['label'] == '我' else 'other'
        
        data_to_write = [expInfo['受试者编号'],expInfo['年龄'],expInfo['性别'],None,'testing',
            fixation_onset,fixation_offset,stim_onset,stim_offset,ITI_onset,ITI_offset,response,label_onset,
            condition,trial['nonword'],subject_response,true_response,correct,rt,
            frame_rate,data.getDateStr()]
            
        dataFile.write(','.join(map(str, data_to_write)) + '\n')
        dataFile.flush()
    
        return correct, flip_side
        
     # 运行完整测试流程
    def run_test_session():
        """运行完整测试阶段"""
        
        nonword_info = selected_trials[['nonword', 'filename', 'label']].drop_duplicates()
        nonword_map = nonword_info.set_index('nonword').to_dict('index')
        
        # 初始化正确次数计数器
        correct_counts = {nonword: 0 for nonword in nonword_map.keys()}
        
        # 持续测试直到所有达到7次正确
        while any(cnt < 7 for cnt in correct_counts.values()):
            # 选择需要测试的nonword
            remaining = [nw for nw, cnt in correct_counts.items() if cnt < 7]
            chosen_nonword = random.choice(remaining)
            trial_info = nonword_map[chosen_nonword]
            
            # 随机翻转选项位置
            flip_side = random.choice([True, False])
            
            # 运行试次并获取正确性
            correct_value, _ = run_test_trial({  # 接收正确性返回值
                'filename': trial_info['filename'],
                'label': trial_info['label'],
                'nonword': chosen_nonword
            }, flip_side, block)

            # 仅当回答正确时增加计数
            if correct_value == 1:
                correct_counts[chosen_nonword] += 1
            
    run_test_session()   
    
    #———————————————————————正式测试阶段指导语——————————————————————#
    formal_instruction = f"""接下来进入实验第二阶段的正式测试，\n
    和学习阶段的测试类似，你仍需判断非词属于“我”还是“{pronoun}”，\n
    按左键 “ ← ” 代表“我”，\n
    按右键 “ → ” 代表“{pronoun}”， \n
    注意，本阶段的总正确率需达到90%及以上才算通过，\n
    如果您准备好了，\n
    <请按空格键继续>"""

    display_instruction(formal_instruction)
    
    #———————————————————————正式测试阶段——————————————————————
    n_formal_blocks = 12
    trials_per_block = 60
    required_accuracy = 0.9
    
    # 创建反馈组件
    feedback_text = visual.TextStim(win, text='', color='white', height=1.2, font='Arial Unicode MS')
    too_slow_text = visual.TextStim(win, text='太慢！', color='red', height=1.2, font='Arial Unicode MS')
    
    #———————————————————正式测试试次生成函数——————————————————————#
    def generate_formal_trials(learned_trials, n_trials):
        """
        参数说明：
        learned_trials: 学习阶段使用的试次数据（DataFrame）
        n_trials: 需要生成的试次数量
        """
        # 从学习阶段数据中提取已学过的非词
        learned_nonwords = learned_trials[['nonword', 'label', 'filename']].drop_duplicates()
        
        # 计算每个非词需要重复的次数
        base_repeats = n_trials // len(learned_nonwords)
        remaining = n_trials % len(learned_nonwords)
        
        # 创建试次列表
        trials = []
        for _ in range(base_repeats):
            trials.extend(learned_nonwords.to_dict('records'))
        
        # 补充剩余试次
        if remaining > 0:
            trials.extend(learned_nonwords.sample(remaining).to_dict('records'))
        
        # 打乱顺序
        random.shuffle(trials)
        return trials[:n_trials]

    #———————————————————————正式测试试次运行函数——————————————————————#
    def run_formal_trial(trial, flip_side, block):
        # 记录变量初始化
        subject_response = None
        rt = None
        stim_onset = None
        stim_offset = None 
        response = None
        true_response = 'left' if trial['label'] == '我' else 'right'
        
        # 注视点
        fixation_outer.draw()
        fixation_inner.draw()
        win.flip()
        fixation_onset = core.getTime()
        core.wait(fix_duration)
        fixation_offset = core.getTime()
        
        # 呈现刺激
        image_path = os.path.join('stimuli', trial['filename'])
        stim_image = visual.ImageStim(win, image=image_path, size=(36,20), pos=(0, 0))
        stim_onset = core.getTime()
        stim_image.draw()
        win.flip()
        core.wait(0.9)
        stim_offset = core.getTime()
        
        # 随机调整 self 和 other 的位置
        left_option = visual.TextStim(win, text='', height=1.8, font='Arial Unicode MS', pos=(-5, 0), color='white')
        right_option = visual.TextStim(win, text='', height=1.8, font='Arial Unicode MS', pos=(5, 0), color='white')
        if flip_side:
            left_option.text = pronoun
            right_option.text = '我'
        else:
            left_option.text = '我'
            right_option.text = pronoun
        
        # 呈现标签提示
        fixation_outer.draw()
        fixation_inner.draw()
        left_option.draw()
        right_option.draw()
        win.flip()
        label_onset = core.getTime()
        
        # 超时控制
        timeout = 2.0
        responded = False
        while (core.getTime() - label_onset) < timeout:
            keys = event.getKeys(keyList=['left', 'right'], timeStamped=True)
            
            if keys:
                key_name, _ = keys[0]
                response = core.getTime()
                
                # 计算rt并转换为ms
                rt = (response - label_onset) * 1000 
                print(f"rt={response - label_onset}")
                
                subject_response = key_name
                responded = True
                break
        
        if not responded:
            response = None
            rt = None
            
        if subject_response == true_response:
            correct = 1
        else:
            correct = 0
        
        # 显示反馈
        if subject_response is None:
            too_slow_text.draw()
            core.wait(0.5)
        else:
            feedback_text.text = "正确！" if correct == 1 else "错误！"
            feedback_text.color = 'green' if correct == 1 else 'red'
            feedback_text.draw()
        
        win.flip()
        core.wait(0.5)
        
        # 试次间隔
        ITI_onset = core.getTime()
        win.flip()
        core.wait(np.random.uniform(0.5,1.5))
        ITI_offset = core.getTime()
            
        condition = 'self' if trial['label'] == '我' else 'other'
        
        # 记录数据
        data_to_write = [expInfo['受试者编号'],expInfo['年龄'],expInfo['性别'],block,'formal_test',
                    fixation_onset,fixation_offset,stim_onset,stim_offset,ITI_onset,ITI_offset,response,label_onset,
                    condition,trial['nonword'],subject_response,true_response,correct,
                    rt,frame_rate,data.getDateStr()]
            
        dataFile.write(','.join(map(str, data_to_write)) + '\n')
        dataFile.flush()
        
        return correct == 1

    #———————————————————————运行正式测试阶段——————————————————————#
    # 初始化总正确次数和总试次数
    total_correct = 0
    total_trials = 0
    
    # 遍历当前block中的每个试次
    for block in range(n_formal_blocks):
        # 生成当前block试次（使用学习阶段的数据）
        trials = generate_formal_trials(selected_trials, trials_per_block)
        block_correct = 0
        
        # 遍历当前每个block中的每个试次
        for trial in trials:
            flip_side = random.choice([True, False])
            is_correct = run_formal_trial(trial, flip_side, block)
            total_trials += 1
            if is_correct:
                total_correct += 1
                block_correct += 1
                
        # 显示block完成信息
        block_info = visual.TextStim(win,
            text=f"block {block+1}/{n_formal_blocks} 完成\n正确率: {block_correct/trials_per_block:.1%}\n<按空格键继续>",
            font='Arial Unicode MS',
            height=0.8,
            color='white'
        )
        block_info.draw()
        win.flip()
        core.wait(0.5)
        event.waitKeys(keyList=['space'])

    # 计算最终正确率
    final_accuracy = total_correct / total_trials if total_trials > 0 else 0

    #———————————————————————实验结束反馈——————————————————————#
    if final_accuracy >= required_accuracy:
        end_text = "恭喜完成实验任务！\n请按空格键退出"
    else:
        end_text = "未达到通过标准（正确率需≥90%）\n请按空格键退出\n联系主试重新开始"

    end_msg = visual.TextStim(win,
        text=end_text,
        font='Arial Unicode MS',
        height=0.8,
        color='white',
        wrapWidth=30
    )
    end_msg.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    #———————————————————————清理资源——————————————————————#
    dataFile.close()
    win.close()
    core.quit()