import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import os

# 设置图像大小（例如1000x500像素）
image_width, image_height = 1000, 500
bg_color = (128, 128, 128)  # 背景色为中灰色

# 计算每个马赛克方块的像素尺寸（假设1度=50像素）
degree_to_pixel = 50
block_size_in_degrees = 1.2  # 每个马赛克方块宽度改为0.6度
block_size = int(block_size_in_degrees * degree_to_pixel)  # 转换为像素

# 创建生成噪声的函数
def generate_noise(image_width, image_height, block_size=10):
    noise_image = np.zeros((image_height, image_width, 3), dtype=np.uint8)
    for y in range(0, image_height, block_size):
        for x in range(0, image_width, block_size):
            # 随机生成噪声块的亮度（高斯分布，均值128，标准差50）
            brightness = random.gauss(128, 50)
            brightness = np.clip(brightness, 0, 255)  # 限制亮度范围在0-255之间
            noise_image[y:y+block_size, x:x+block_size] = [brightness, brightness, brightness]
    return noise_image

# 生成并保存噪声图像
def save_noise_images(num_images=5):  # 生成5张噪声图像
    if not os.path.exists("noise"):
        os.makedirs("noise")

    for i in range(num_images):
        noise_image = generate_noise(image_width, image_height, block_size)
        noise_img = Image.fromarray(noise_image)
        file_path = f"noise/noise_{i+1}.png"  # 文件命名为 noise_1.png, noise_2.png, ...
        noise_img.save(file_path)

# 极性反转函数，保持平均亮度为128
def invert_polarity(image):
    noise_array = np.array(image)
    # 获取当前图像的平均亮度
    current_mean = np.mean(noise_array)
    # 计算反转后每个像素的新亮度
    inverted_array = 255 - noise_array
    # 计算反转后图像的亮度调整因子
    inverted_mean = np.mean(inverted_array)
    adjustment = 128 - inverted_mean
    inverted_array = np.clip(inverted_array + adjustment, 0, 255)
    
    # 创建反转后的图片
    inverted_img = Image.fromarray(inverted_array.astype(np.uint8))
    return inverted_img

# 根据噪声图像生成反转的图像并保存
def save_inverted_images():
    # 读取之前保存的噪声图像，并生成极性反转图像
    for i in range(5):  # 这里循环5次，反转前5张图像
        noise_img = Image.open(f"noise/noise_{i+1}.png")
        inverted_img = invert_polarity(noise_img)
        inverted_img.save(f"noise/inverted_noise_{i+1}.png")  # 保存为 noise/inverted_noise_1.png, noise/inverted_noise_2.png, ...

# 生成5张噪声图像并保存
save_noise_images(num_images=5)

# 生成5张极性反转的噪声图像并保存
save_inverted_images()



