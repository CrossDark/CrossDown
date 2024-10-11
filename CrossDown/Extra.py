import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO


EXTRA = [

]


def function_drawing(function, x_range=(-10, 10), y_range=(-20, 20), dpi=100):
    # 创建一个图像和坐标轴对象
    fig, ax = plt.subplots()

    # 生成x值
    x = np.linspace(x_range[0], x_range[1], 400)

    # 计算y值
    y = function(x)

    # 绘制图像
    ax.plot(x, y)

    # 设置坐标轴范围
    ax.set_xlim(x_range)
    ax.set_ylim(y_range)

    # 隐藏坐标轴
    ax.axis('on')

    # 将图像保存到BytesIO对象
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi)

    # 获取图像数据的Base64编码
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # 关闭图像和坐标轴对象
    plt.close(fig)

    # 返回Base64编码的字符串
    return data
