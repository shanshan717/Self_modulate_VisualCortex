from psychopy import visual, core, event, monitors
import os
import random

# ================== 参数配置 ================== 
padding_scale = 1.5  # 背景缩放系数（原1.0为刚好包裹文字）

# 字母参数
# 字母高度（单位：度）
letter_height = 3.6  
# 字母水平位置
x_positions = [-4.8, -2.4, 0, 2.4, 4.8]  

# ================== 注视点参数 ================== 
# 外圈（空心圆环）
outer_diameter = 0.3    # 直径0.3度
outer_line_color = 'black'
outer_fill_color = None  # 透明填充

# 内圈（实心圆点）
inner_diameter = 0.1   # 直径0.15度
inner_color = 'black'

# ================== 初始化窗口 ================== 
monitor = monitors.Monitor('testMonitor')
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=False,
                    color='grey')
win.setMouseVisible(False)

# ================== 计算背景尺寸 ================== 
# 原始非词尺寸
nonword_width = max(x_positions) - min(x_positions)  # 文字总宽度
nonword_height = letter_height

# 缩放后的背景尺寸
base_padding = 0.9  # 基础边距
bg_width = nonword_width + 2 * base_padding * padding_scale
bg_height = nonword_height + 2 * base_padding * padding_scale
bg_size = (bg_width, bg_height)

# 预加载背景图片（修改后）
noise_folder = 'noise'
noise_images = []
for filename in os.listdir(noise_folder):
    if filename.startswith('._'):
        continue
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(noise_folder, filename)
        img_stim = visual.ImageStim(
            win=win,
            image=img_path,
            units='deg',        # 使用度数单位
            size=bg_size,        # 设置计算后的背景尺寸
            pos=(0, 0)           # 与非词中心对齐
        )
        noise_images.append(img_stim)

# 确保stimuli文件夹存在
output_folder = 'stimuli'
os.makedirs(output_folder, exist_ok=True)

# ================== 创建固定元素 ================== 
# ================== 创建复合注视点 ================== 
# 外圈参数（空心）
outer_size = 0.3    # 外圈直径（度）
outer_color = 'black'
outer_fill = None  # 无填充

# 内圈参数（实心）
inner_size = 0.15   # 内圈直径（度）
inner_color = 'black'

# 创建两个圆形组件
fixation_outer = visual.Circle(
    win,
    radius=outer_size/2,  # 转换为半径
    edges=32,
    lineColor=outer_color,
    fillColor=outer_fill,
    lineWidth=1.5,        # 增加轮廓线宽
    pos=(0, 0)
)

fixation_inner = visual.Circle(
    win,
    radius=inner_size/2,
    edges=32,
    fillColor=inner_color,
    lineColor=inner_color,  # 边框颜色与填充一致
    pos=(0, 0)
)

# ================== 非词列表 ================== 
nonwords = ["REUJZ", "NVUSR", "MLUHN", "AIUVS", "BEUQX", "EAUYI", "SVUDP", "PVUFG", "LVUSQ" , "FVURT",
            "ODNRB", "KTNHS", "JDNST", "MSNRV", "SXNQT", "JKNGR", "YPNSF", "VFNRM", "LKNFG", "PRNFL"]

# ================== 刺激生成函数 ================== 
def create_letter_stimuli(word):
    """为单个非词创建所有字母刺激"""
    stimuli = []
    for idx, char in enumerate(word):
        # 初始化参数
        text = char
        flip = False
        y_pos = 0 
        y_offest = 0.2
         
        # 处理第三个字母的特殊情况
        if idx == 2 and char == 'N':
                text = 'U'        # 显示U字符
                flip = True
                y_pos = y_offest  # 垂直翻转
        
        # 创建文本刺激
        stim = visual.TextStim(
            win=win,
            text=text,
            pos=(x_positions[idx], y_pos),  # y轴居中
            height=letter_height,
            opacity=0.9,
            flipVert=flip,
            alignHoriz='center',
            alignVert='center'
        )
        stimuli.append(stim)
    return stimuli

# ================== 主实验循环 ================== 
for trial_word in nonwords:
    # 随机选择一个背景
    background = random.choice(noise_images)
    
    # 生成当前试次的所有刺激
    trial_stimuli = create_letter_stimuli(trial_word)
    
    # 清屏并绘制所有刺激
    win.flip()
    background.draw() 
    for stim in trial_stimuli:
        stim.draw()
    fixation_outer.draw()
    fixation_inner.draw() 
    win.flip()
    
    # 保存图片
    screenshot_path = os.path.join(output_folder, f"{trial_word}.png")
    win.getMovieFrame()
    win.saveMovieFrames(screenshot_path)
    
    core.wait(0.5)
#    # 等待按键继续（可按ESC退出）
#    keys = event.waitKeys()
#    if 'escape' in keys:
#        break

# 清理资源
win.close()
core.quit()