import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import matplotlib.pyplot as plt

# 设置图像大小（例如1000x500像素）
image_width, image_height = 1000, 500
bg_color = (128, 128, 128)  # 背景色为中灰色
noise_color = (128, 128, 128)  # 噪声颜色，通常灰色
letter_color = (255, 255, 255)  # 字母颜色为白色
font_size = 60  # 字母大小

# 创建图像对象
image = Image.new('RGB', (image_width, image_height), bg_color)
draw = ImageDraw.Draw(image)

# 加载字体（选择一个等宽字体）
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", font_size)

# 设置字母的位置
letters = "HELLO"  # 可以是一个单词或非单词

# 获取每个字母的宽度（使用 getbbox 获取边界框）
bbox = font.getbbox(letters[0])  # 获取单个字母的边界框
letter_width = bbox[2] - bbox[0]  # 宽度 = 右边界 - 左边界
spacing = 0.6 * letter_width  # 字母之间的间距

# 将字母绘制到图像中
x_pos = (image_width - len(letters) * letter_width - (len(letters) - 1) * spacing) / 2  # 中心对齐
y_pos = (image_height - font_size) / 2  # 垂直居中

for letter in letters:
    draw.text((x_pos, y_pos), letter, font=font, fill=letter_color)
    x_pos += letter_width + spacing

# 生成噪声
def generate_noise(image_width, image_height, block_size=10):
    noise_image = np.zeros((image_height, image_width, 3), dtype=np.uint8)
    for y in range(0, image_height, block_size):
        for x in range(0, image_width, block_size):
            # 随机生成噪声块的亮度
            brightness = random.gauss(128, 50)  # 高斯分布，均值128，标准差50
            brightness = np.clip(brightness, 0, 255)  # 限制亮度范围
            noise_image[y:y+block_size, x:x+block_size] = [brightness, brightness, brightness]
    return noise_image

# 生成并应用噪声
noise_image = generate_noise(image_width, image_height, block_size=12)
noise_img = Image.fromarray(noise_image)

# 将噪声覆盖到字母上，80%不透明度
image = Image.blend(image, noise_img, alpha=0.4)

# 显示结果
plt.imshow(image)
plt.axis('off')
plt.show()
