#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script generates visual stimuli using PsychoPy. It calculates visual angles, 
reads nonwords from a CSV file, and presents them on a background image. 
Each stimulus is displayed and saved as an image file.

Key components:
1. **Visual Angle Calculation**: Converts degrees to pixels for accurate stimulus presentation.
2. **CSV File Reading**: Loads nonwords from 'nonwords.csv'.
3. **Window Initialization**: Creates a PsychoPy window with specified properties.
4. **Stimulus Generation**: Places nonwords on a noisy background with calculated positions.
5. **Experiment Loop**: Displays stimuli, captures screenshots, and saves them.
"""

# import libraries
from math import atan, pi
from psychopy import visual, core, event, monitors
import os
import random
import pandas as pd

# ================== visual angle calculation ==================
# viewing distance
D = 57  
# screen width (24 inch)
S = 32.31
# screen resolution
resolution = (1920, 1080)  

# Method 1: plane calculation
alpha_half = atan((S / 2) / D)  
# convert to degrees
alpha = alpha_half * 2 * 180 / pi 
print(alpha)
# convert degrees to pixels
deg2pix = int(resolution[0] / alpha)  
print(deg2pix)

# Method 2: curved screen approximation
alpha2 = S/D
alpha2 = alpha2 * 180 / pi
print(alpha2)
deg2pix2 = int(resolution[0]/alpha)
print(deg2pix2)

# ================== load nonwords from CSV ==================
current_dir = os.getcwd()
csv_path = os.path.join(current_dir, 'nonwords.csv')
df = pd.read_csv(csv_path)
nonwords = df['nonwords'].tolist()

# ================== initialize psychoPy window ==================
monitor = monitors.Monitor('testMonitor')
win = visual.Window(size=[1920, 1080],
                    allowGUI=True,
                    monitor='testMonitor',
                    units='deg',
                    fullscr=True,
                    color='grey')
# hide mouse cursor
win.setMouseVisible(False)

# ================== set Nonword Display Parameters ==================

padding_scale = 2.7
base_padding = 0.9 

# letter size parameters (degrees)
letter_height = 5.5 
letter_width = 3.6   
spacing = 0.6        
num_letters = 5
x_positions = [(i - (num_letters - 1) / 2) * (letter_width + spacing) for i in range(num_letters)]
print(x_positions)

# ================== calculate background size ==================
nonword_width = max(x_positions) - min(x_positions)  
nonword_height = letter_height

bg_width = nonword_width + 2 * base_padding * padding_scale
bg_height = nonword_height + 2 * base_padding * padding_scale
bg_size = (bg_width, bg_height)

# preload background noise images
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
            units='deg',
            size=bg_size,
            pos=(0, 0)
        )
        noise_images.append(img_stim)

# ensure output folder exists
output_folder = 'stimuli'
os.makedirs(output_folder, exist_ok=True)

# ================== function to create letter stimuli ==================
def create_letter_stimuli(word):
    stimuli = []
    for idx, char in enumerate(word):
        text = char
        flip = False
        y_pos = 0
        y_offset = 0.2
        if idx == 2 and char == 'N':
            text = 'U'
            flip = True
            y_pos = y_offset
        stim = visual.TextStim(
            win=win,
            text=text,
            pos=(x_positions[idx], y_pos),
            height=letter_height,
            opacity=0.9,
            flipVert=flip,
            alignText='center',
            anchorHoriz='center',
            anchorVert='center'
        )
        stimuli.append(stim)
    return stimuli

# ================== main Experiment Loop ================== 
for trial_word in nonwords:
    background = random.choice(noise_images)
    trial_stimuli = create_letter_stimuli(trial_word)
    
    win.flip()
    background.draw()
    for stim in trial_stimuli:
        stim.draw()
    win.flip()
    
    screenshot_path = os.path.join(output_folder, f"{trial_word}.png")
    win.getMovieFrame()
    win.saveMovieFrames(screenshot_path)
    
    core.wait(0.5)

win.close()
core.quit()