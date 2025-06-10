from psychopy import visual, event, core, data, gui
import numpy as np
import pandas as pd
import os
import random

# ========================== 记录参与者信息 ==========================
expInfo = {
    '模式': ['inform', 'test'],
    '测试时间': data.getDateStr(),
    '受试者编号': '000',
    '年龄': '',
    '性别': ['Male', 'Female']
}

dlg = gui.DlgFromDict(
    dictionary=expInfo,
    title='基本信息',
    fixed=['测试时间']
)
if not dlg.OK:
    core.quit()

# ========================== 创建实验窗口 ==========================
win = visual.Window(
    size=[1920, 1080],
    allowGUI=True,
    monitor='testMonitor',
    units='deg',
    fullscr=True,
    color='grey'
)
win.setMouseVisible(False)

# ========================== 刺激参数设置 ==========================
letter_params = {
    'height': 5.5,
    'width': 3.6,
    'spacing': 0.6,
    'num_letters': 5,
    'y_offset': 0.2  # N block 上移偏移量
}

# ========================== 默认实验参数 ==========================
default_params = {
    'n_repeats': 18,
    'block_duration': 14,
    'letter_duration': 0.5,
    'isi_duration': 0.5,
    'ITI_duration': 9.8,
    'frame_rate': 60
}

# 根据模式选择调整参数
experiment_params = default_params.copy()
if expInfo['模式'] == 'test':
    experiment_params['n_repeats'] = 2
    experiment_params['block_duration'] = 6
    experiment_params['ITI_duration'] = 2

# ========================== 刺激组件定义 ==========================
fixation_outer = visual.Circle(
    win, radius=0.25, edges=32,
    lineColor='black', fillColor=None, lineWidth=1.5
)

fixation_inner = visual.Circle(
    win, radius=0.10, edges=32,
    fillColor='black', lineColor='black'
)

# ========================== MRI触发等待函数 ==========================
def wait_for_trigger(win):
    prompt = visual.TextStim(
        win,
        text="等待MRI触发，请按下 's' 键开始",
        font='Arial Unicode MS',
        height=1.0,
        color='white'
    )
    while True:
        prompt.draw()
        win.flip()
        keys = event.getKeys()
        if 's' in keys:
            break
        core.wait(0.1)

# ========================== 文件路径设置 ==========================
BASE_PATH = "/Volumes/ss/psychopy_514/"
os.makedirs(os.path.join(BASE_PATH, "data/fmri"), exist_ok=True)
filename = os.path.join(
    BASE_PATH,
    f"data/fmri/Exp2_fMRI_localiser_{expInfo['受试者编号']}.csv"
)

# ========================== 数据文件头 ==========================
header = [
    'subject_id', 'age', 'gender', 'block', 'condition',
    'fixation_onset', 'fixation_offset',
    'stim_onset', 'stim_offset',
    'ITI_onset', 'ITI_offset',
    'frame_rate', 'date'
]

# ========================== 实验流程函数 ==========================
def run_experiment():
    # 交替排列 block：['U', 'N', 'U', 'N', ..., 共36个]
    all_blocks = ['U' if i % 2 == 0 else 'N' for i in range(experiment_params['n_repeats'] * 2)]

    with open(filename, 'w', encoding='utf-8') as data_file:
        data_file.write(','.join(header) + '\n')

        for block_idx, block_letter in enumerate(all_blocks):
            n_trials_per_block = int(experiment_params['block_duration'] /
                                     (experiment_params['letter_duration'] + experiment_params['isi_duration']))

            for trial_idx in range(n_trials_per_block):
                if 'escape' in event.getKeys():
                    raise KeyboardInterrupt

                stim = visual.TextStim(
                    win=win,
                    text='U',
                    height=letter_params['height'],
                    color='white',
                    flipVert=(block_letter == 'N'),
                    pos=(0, letter_params['y_offset'] if block_letter == 'N' else 0)
                )

                # ==================== 注视点呈现 ====================
                fixation_onset = core.getTime()
                fixation_outer.draw()
                fixation_inner.draw()
                win.flip()
                core.wait(0.5)
                fixation_offset = core.getTime() 

                # ==================== 刺激呈现 ====================
                stim_onset = core.getTime()
                stim.draw()
                fixation_outer.draw()
                fixation_inner.draw()
                win.flip()
                core.wait(0.5)
                stim_offset = core.getTime() 

                # ==================== 数据记录 ====================
                trial_data = [
                    expInfo['受试者编号'], expInfo['年龄'], expInfo['性别'][0], block_idx + 1, block_letter,
                    f"{fixation_onset:.4f}", f"{fixation_offset:.4f}",
                    f"{stim_onset:.4f}", f"{stim_offset:.4f}",
                    "", "",
                    experiment_params['frame_rate'], data.getDateStr()
                ]
                data_file.write(','.join(map(str, trial_data)) + '\n')
                data_file.flush()

            # ==================== ITI阶段 ====================
            fixation_outer.draw()
            fixation_inner.draw()
            win.flip()
            ITI_onset = core.getTime() 
            core.wait(experiment_params['ITI_duration'])
            ITI_offset = core.getTime() 

            ITI_data = [
                expInfo['受试者编号'], expInfo['年龄'], expInfo['性别'][0], block_idx + 1, "ITI",
                "", "", "", "",
                f"{ITI_onset:.4f}", f"{ITI_offset:.4f}",
                experiment_params['frame_rate'], data.getDateStr()
            ]
            data_file.write(','.join(map(str, ITI_data)) + '\n')
            data_file.flush()

# ========================== 等待MRI触发 + 运行实验 ==========================
try:
    wait_for_trigger(win)
    run_experiment()
except KeyboardInterrupt:
    print("实验被用户手动终止（ESC）")
except Exception as e:
    print(f"实验异常终止: {str(e)}")
finally:
    win.close()
    core.quit()
