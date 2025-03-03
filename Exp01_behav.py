# 导入需要的库
from psychopy import visual, event, core, data, gui
from psychopy.hardware import keyboard
import numpy as np
import pandas as pd
import os
from psychopy.monitors import Monitor

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
    
#————————————————创建实验数据文件夹———————————————#
fileName = f"data/Exp1_task1_{expInfo['受试者编号']}" + '.csv'
# 确保文件夹存在
os.makedirs(os.path.dirname(fileName), exist_ok=True)  
dataFile = open(fileName, 'w')
# 将需要记录的数据写入csv，作为列名
dataFile.write('fixation_onset,fixation_offset,stim_onset,stim_offset,ITI_onset,ITI_offset,'
                'condition,nonword,rt,response,stage,correct,'
                'frame_rate,date,age,gender,subject_id,block,subject_number,block_index\n')
 
#————————————————创建实验窗口———————————————#
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=False,
                    color='grey',
                    waitBlanking=True,
                    checkTiming=True)
win.setMouseVisible(False)
monitor = Monitor(name='testMonitor')

# 在实验开始前添加默认帧率
for _ in range(60): 
    win.flip()

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
        if 'right' in keys:  # Proceed to the next step
            return "continue"
        elif 'left' in keys:  # Contact the experimenter
            return "contact"
    else:
        # Default behavior, wait for space key
        keys = event.waitKeys(keyList=['space'])
        if 'space' in keys:
            return
            
# Page 1: Introduction Text
intro_text1 = """欢迎参加本实验！\n
本实验共分为两个阶段：\n
第一阶段需要您学习无意义的英文单词（在后续的实验中统称为非词）与标签（Self、Other）的联结，\n
其中Self指代自己，Other指代他人，\n
例如"REUJZ = self"，\n
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
intro_text3 = """在第一阶段,\n
屏幕中心会出现一个注视点,\n
您需要将注意力保持在注视点上,\n
随着注视点消失,\n
您需要学习记忆非词和标签（Self、Other）的联结,\n
进入实验后，您的鼠标就会隐藏,\n\n
如果已理解实验要求，请按‘ → ’键继续，
若仍有疑问，请按‘ ←’ 键联系主试"""

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
                nonword = os.path.splitext(file)[0]  # 去除扩展名
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
        if len(u_files) < 2 or len(n_files) < 2:
            raise ValueError("需要至少6个第三个字母为U和6个为N的非词图片")

        # 随机选择并分配
        random.shuffle(u_files)
        random.shuffle(n_files)
        
        # 创建试次列表
        trials = []
        # 我-条件 (3U + 3N)
        for info in u_files[:1] + n_files[:1]:
            trials.append({
            'filename': info['filename'], 
            'nonword': info['nonword'],
            'label': '我'})
        # 他-条件 (3U + 3N)
        for info in u_files[1:2] + n_files[1:2]:
            trials.append({
            'filename': info['filename'], 
            'nonword': info['nonword'],
            'label': '他'})

        # 打乱顺序
        random.shuffle(trials)
            
        return pd.DataFrame(trials)
        
    # 创建注视点
    fixation_outer = visual.Circle(
    win,
    radius=0.10,  # 直径0.3度换算为半径，0，15
    edges=32,
    lineColor='black',
    fillColor=None,
    lineWidth=1.5
    )
    
    fixation_inner = visual.Circle(
    win,
    radius=0.025,  # 直径0.15度换算为半径，0.075
    edges=32,
    fillColor='black',
    lineColor='black'
    )
    
    # 创建图片刺激组件
    stim_image = visual.ImageStim(
    win,
    image=None,
    pos=(0, 1),
    size=(15, 8)  # 根据实际需要调整图片大小
    )
    
    # 创建标签文本组件
    label_text = visual.TextStim(
        win,
        text='',
        pos=(0, -1),   
        height=1.2,    
        color='white',
        font='Arial Unicode MS'
    )
    
    # 设置实验参数
    n_blocks = 5
    fix_duration = 0.3  # 注视点持续时间
    stim_duration = 8.0  # 刺激呈现时间
    ITI_duration = 0.1   # 试次间隔
    
    # 获取平衡试次
    selected_trials = get_balanced_trials(stim_df)
    
    # 设置 block_index =0
    block_index = 0
    
    #———————————————————————学习阶段——————————————————————#
    # 学习非词
    for block in range(n_blocks):
        for _, trial in selected_trials.iterrows():
            # 呈现注视点
            fixation_onset = core.getTime()
            fixation_outer.draw()
            fixation_inner.draw()
            win.flip()
            core.wait(fix_duration)
            fixation_offset = core.getTime()
        
            # 呈现刺激
            image_path = os.path.join('stimuli', trial['filename'])
            stim_image.image = image_path
            label_text.text = trial['label']
        
            # 初始化所需记录的数据
            stim_onset = None  
            stim_offset = None  
            response = None
            rt = None
            first_flip = True  
            rt_clock = core.Clock()  

            # 设置最大呈现时长（8秒）
            max_duration = 8.0  
            start_time = core.getTime()  # 时长控制起点
        
            while (core.getTime() - start_time) < max_duration:
                # 绘制刺激
                stim_image.draw()
                label_text.draw()
                
                # 首次刷新记录精确时间
                if first_flip:
                    flip_time = win.flip()
                    stim_onset = flip_time  
                    first_flip = False
                else:
                    win.flip()
                
                # 检测按键
                keys = event.getKeys(
                    keyList=['space', 'escape'],
                    timeStamped=rt_clock  
                )
                
                if keys:
                    if keys[0][0] == 'space' and response is None:
                        # 记录反应时和反应
                        # 转换为毫秒
                        rt = keys[0][1] * 1000  
                        response = 'space'
                        stim_offset = core.getTime()  
                        break  

            # 处理超时情况
            if stim_offset is None:
                stim_offset = core.getTime()

            # 清除屏幕
            win.flip()

            # 试次间隔
            ITI_onset = core.getTime()
            win.flip()
            core.wait(ITI_duration)
            ITI_offset = core.getTime()
            
            # 获取帧率
            frame_rate = win.getActualFrameRate()
            if frame_rate is None:
                frame_rate = 60.0
            
            # 记录数据
            data_to_write = [
            fixation_onset, fixation_offset, stim_onset, stim_offset, ITI_onset, ITI_offset,
            trial['label'], trial['nonword'], rt, response, 'study', None,
            frame_rate, data.getDateStr(), expInfo['年龄'], expInfo['性别'],
            expInfo['受试者编号'], block_index, int(expInfo['受试者编号'][-3:]), block
            ]
            dataFile.write(','.join(map(str, data_to_write)) + '\n')
            dataFile.flush() 
        
    #———————————————————————学习阶段结束指导语——————————————————————#
    study_end_text = visual.TextStim(win,
        text="学习阶段结束！\n\n"  
         "接下来我们将对刚才学习内容进行测试\n"
         "在屏幕中央的注视点消失后，会随机呈现一个非词，您需要判断该非词属于“self” 还是 “other” \n\n"
         "按左键 '←' 代表“self”（自己）\n"
         "按右键 '→' 代表“other”（他人）\n\n"
         "如果您已经准备好了\n"
         "<请按空格键开始正式测试>",  
        font='Arial Unicode MS',
        pos=(0, 0),
        color='white',
        height=0.8,
        wrapWidth=30,          
        alignHoriz='center',   
        alignVert='center',    
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
    left_option = visual.TextStim(win, text='我', height=1.8, font='Arial Unicode MS', pos=(-5, 0), color='white')
    right_option = visual.TextStim(win, text='他', height=1.8, font='Arial Unicode MS', pos=(5, 0), color='white')
    
    # 定义运行函数
    def run_test_trial(trial):
        stim_onset = None  
        stim_offset = None 
        response = None 
        rt = None 
        
        # 注视点
        fixation_onset = core.getTime()
        fixation_outer.draw()
        fixation_inner.draw()
        win.flip()
        core.wait(0.3)
        fixation_offset = core.getTime()
        
        # 呈现非词刺激
        image_path = os.path.join('stimuli', trial['filename'])
        stim_image = visual.ImageStim(win, image=image_path, pos=(0, 0))
        stim_onset = core.getTime() 
        stim_image.draw()
        win.flip()
        core.wait(2)
        
        # 呈现标签提示
        left_option.draw()
        right_option.draw()
        win.flip()
        response_onset = core.getTime()
        
        # 创建反应clock
        rt_clock = core.Clock() 
        while rt_clock.getTime() < 2.0:
            keys = event.getKeys(keyList=['left', 'right'],
                                timeStamped=rt_clock)
            if keys:
                response = keys[0][0]
                rt = keys[0][1] * 1000
                break
        
        correct = False
        if response == 'left' and trial['label'] == '我':
            correct = True
        elif response == 'right' and trial['label'] == '他':
            correct = True
            
            # 判断正确性并给出反馈
        if response is None:
            too_slow_text.draw()
        else:
            feedback.setText("正确！" if correct else "错误！")
            feedback.color = 'green' if correct else 'red'
            feedback.draw()
        
        win.flip()
        core.wait(1)
        
        frame_rate = win.getActualFrameRate() or 60.0
        data_to_write = [stim_onset, core.getTime(), None, None, None, None,  # 占位时间参数
        trial['label'], trial['nonword'], rt, response, 'study test', correct,
        frame_rate, data.getDateStr(), expInfo['年龄'], expInfo['性别'],
        expInfo['受试者编号'], block_index, int(expInfo['受试者编号'][-3:]), -1  # block标记为测试
        ]
        dataFile.write(','.join(map(str, data_to_write)) + '\n')
        dataFile.flush()
    
        return correct
        
     # 运行完整测试流程
    def run_test_session():
        """运行完整测试阶段"""
        test_trials = selected_trials.copy()  # 使用学习阶段的试次
        remaining_trials = test_trials.sample(frac=1).reset_index(drop=True)  # 打乱顺序
    
        while True:
            errors = []
        
            # 遍历所有试次
            for idx, trial in remaining_trials.iterrows():
                correct = run_test_trial(trial)
                if not correct:
                    errors.append(trial.to_dict())  # 收集错误试次
            
            # 如果没有错误则结束
            if len(errors) == 0:
                break
            
            # 否则重新测试错误试次
            remaining_trials = pd.DataFrame(errors).sample(frac=1)
            
    run_test_session()   
        