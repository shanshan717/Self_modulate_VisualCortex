#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
- fMRI Experiment functional localiser
- 为60hz刷新率的显示器计算帧数
"""


from psychopy import visual, event, core, data, gui
import numpy as np
import pandas as pd
import os
import random

# =============================================================
#                           记录被试信息
# =============================================================
expInfo = {
    '测试时间': data.getDateStr(),
    '受试者编号': '000',
    'run': ['1','2'],
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
    allowGUI=True,
    monitor='testMonitor',
    units='deg',
    fullscr=True,
    color='grey'
)
win.setMouseVisible(False)

# =============================================================
#                           定义主要变量
# =============================================================
default_params = {
    'n_task_blocks': 14,  # 14个任务block
    'n_null_blocks': 14,  # 14个null block
    'block_duration_s': 13.5,  # block时长13.5秒
    'letter_duration_s': 0.3,  # 字母刺激300ms
    'isi_duration_s': 0.2,  # 注视点200ms
    'null_duration_s': 13.5,  # null block时长13.5秒
    'n_letters_per_block': 27,  # 每个block 27个字母
    'frame_rate': 60,  # 60Hz刷新率
    'tr_length': 1.35,  # TR长度1.35秒
    'trs_per_block': 10,  # 每个block 10个TR
    'total_trs': 280,  # 总TR数 (14+14)*10
    'initial_delay_trs': 0,  # 初始延迟TR数（联影机器空扫不出图，trigger后直接开始）
}


# =============================================================
#                           刺激参数设置 
# =============================================================
letter_params = {
    'height': 5.5,
    'width': 3.6,
    'spacing': 0.6,
    'num_letters': 5,
    'y_offset': 0.2  # N block 上移偏移量
}

# =============================================================
#                           定义注视点 
# =============================================================
fixation_outer = visual.Circle(
    win, radius=0.25, edges=32,
    lineColor='black', fillColor=None, lineWidth=1.5
)

fixation_inner = visual.Circle(
    win, radius=0.10, edges=32,
    fillColor='black', lineColor='black'
)

# =============================================================
#                     定义MRI trigger触发函数 
# =============================================================
def wait_for_trigger(win, trigger_key='s'):
    """
    南师大联影uMR590扫描仪发送键盘触发信号
    参数：
        win: PsychoPy窗口对象
        trigger_key: trigger信号 's'
    """
    # 清理键盘残留按键
    event.clearEvents(eventType='keyboard')
    
    while True:
        # 显示注视点
        fixation_outer.draw()
        fixation_inner.draw()
        win.flip()
        
        keys = event.getKeys()
        if len(keys) > 0:
            trigger_time = core.getTime()  # 立即记录时间
            if keys[0] == trigger_key:
                return trigger_time  # 立即返回触发时间
            elif keys[0] == 'escape':
                core.quit()


# =============================================================
#                           设置结果输出路径
# =============================================================
# 查看当前工作目录
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
# 切换到父目录
os.chdir(parent_dir)

# 输出文件数据的列名
header = ['subject_id', 'age', 'gender', 'run', 'block', 'condition',
    'stim_onset', 'stim_offset', 'fixation_onset', 'fixation_offset',
    'null_onset', 'null_offset','frame_rate', 'date']

filename = os.path.join('data', 'fmri', f"Exp2_fMRI_localiser_{expInfo['受试者编号']}_run{expInfo['run']}.csv")

data_dir = os.path.dirname(filename)
os.makedirs(data_dir, exist_ok=True)
    
# =============================================================
#                           计算帧数
# =============================================================
def calculate_frames(duration_s, frame_rate=60):
    """计算指定时长对应的帧数"""
    return int(round(duration_s * frame_rate))


# =============================================================
#                           定义呈现文本函数
# =============================================================
def present_message(win, text, duration_frames=None):
    message = visual.TextStim(
        win,
        text=text,
        pos=(0, 0),
        font='Microsoft YaHei',
        height=0.8,
        color='white',
        wrapWidth=30
    )
    if duration_frames:
        for frame in range(duration_frames):
            message.draw()
            win.flip()
    else:
        message.draw()
        win.flip()

# =============================================================
#                          定义实验流程函数
# =============================================================
def run_experiment(experiment_clock):
    experiment_params = default_params.copy()
    
    # 计算帧数
    # 300ms = 18帧
    letter_frames = calculate_frames(experiment_params['letter_duration_s'])  
    # 200ms = 12帧
    isi_frames = calculate_frames(experiment_params['isi_duration_s'])  
    # 13.5s = 810帧     
    null_frames = calculate_frames(experiment_params['null_duration_s'])      
    
    with open(filename, 'w', encoding='utf-8') as data_file:
        data_file.write(','.join(header) + '\n')
        
        block_count = 0
        
        # 创建block顺序：7个U block + 7个N block，随机排列
        u_blocks = ['U'] * 7
        n_blocks = ['N'] * 7
        task_blocks = u_blocks + n_blocks
        random.shuffle(task_blocks)
        
        # 创建完整的block序列：每个任务block后跟一个null block
        all_blocks = []
        for task_block in task_blocks:
            all_blocks.append(task_block)
            all_blocks.append('NULL')
        
        # 执行所有block
        for block_idx, block_type in enumerate(all_blocks):
            
            if 'escape' in event.getKeys():
                raise KeyboardInterrupt
            
            block_count += 1
            
            if block_type == 'NULL':
                # ==================== NULL BLOCK ====================
                null_onset = experiment_clock.getTime()
                
                for frame in range(null_frames):
                    fixation_outer.draw()
                    fixation_inner.draw()
                    win.flip()
                    
                    # 检查退出键
                    if frame % 60 == 0:  # 每秒检查一次
                        if 'escape' in event.getKeys():
                            raise KeyboardInterrupt
                
                null_offset = experiment_clock.getTime()
                
                # 记录null block数据
                null_data = [
                    expInfo['受试者编号'], expInfo['年龄'], expInfo['性别'][0], 
                    expInfo['run'], block_count, 'NULL',
                    "", "", "", "",
                    f"{null_onset:.4f}", f"{null_offset:.4f}",
                    experiment_params['frame_rate'], data.getDateStr()
                ]
                data_file.write(','.join(map(str, null_data)) + '\n')
                data_file.flush()
                
            else:
                # ==================== TASK BLOCK ====================
                
                for letter_idx in range(experiment_params['n_letters_per_block']):
                    
                    if 'escape' in event.getKeys():
                        raise KeyboardInterrupt
                    
                    # 创建字母刺激
                    stim = visual.TextStim(
                        win=win,
                        text='U',
                        height=letter_params['height'],
                        color='white',
                        flipVert=(block_type == 'N'),
                        pos=(0, letter_params['y_offset'] if block_type == 'N' else 0)
                    )
                    
                    # ==================== 字母刺激阶段 ====================
                    stim_onset = experiment_clock.getTime()
                    
                    for frame in range(letter_frames):
                        stim.draw()
                        fixation_outer.draw()
                        fixation_inner.draw()
                        win.flip()
                    
                    stim_offset = experiment_clock.getTime()
                    
                    # ==================== 注视点阶段 ====================
                    fixation_onset = experiment_clock.getTime()
                    
                    for frame in range(isi_frames):
                        fixation_outer.draw()
                        fixation_inner.draw()
                        win.flip()
                    
                    fixation_offset = experiment_clock.getTime()
                    
                    # ==================== 数据记录 ====================
                    trial_data = [
                        expInfo['受试者编号'], expInfo['年龄'], expInfo['性别'][0], 
                        expInfo['run'], block_count, block_type,
                        f"{stim_onset:.4f}", f"{stim_offset:.4f}",
                        f"{fixation_onset:.4f}", f"{fixation_offset:.4f}",
                        "", "",
                        experiment_params['frame_rate'], data.getDateStr()
                    ]
                    data_file.write(','.join(map(str, trial_data)) + '\n')
                    data_file.flush()
    
    return block_count

# =============================================================
#                          等待MRI触发 + 运行实验
# =============================================================
try:
    # 等待MRI触发信号
    ttl_onset = wait_for_trigger(win)
    
    # 收到trigger信号后立即创建新的实验时钟
    experiment_clock = core.Clock()  
    
    print("实验开始！")

    # 运行实验，传入experiment_clock
    total_blocks = run_experiment(experiment_clock)
    
    # 实验结束消息 - 根据run数显示不同消息
    current_run = int(expInfo['run'])
    if current_run == 1:
        end_message = "第一个run结束！"
    else:
        end_message = "恭喜您完成本阶段的任务，感谢您的参与！"
    
    # 显示消息1秒
    message = visual.TextStim(
        win,
        text=end_message,
        pos=(0, 0),
        font='Microsoft YaHei',
        height=0.8,
        color='white',
        wrapWidth=30
    )
    message.draw()
    win.flip()
    core.wait(1.0)  # 显示1秒
    
except KeyboardInterrupt:
    print("实验被用户手动终止（ESC）")
except Exception as e:
    print(f"实验异常终止: {str(e)}")
finally:
    win.close()
    core.quit()
