import gradio as gr
from gradio.components import Image, File, Slider
from moonshot import upload_file_data
from chroma import chroma_file_data, chroma_query
import time
import os


def upload_files(files):
    # 返回上传文件的路径列表
    text = []
    for file in files:
        text.append(upload_file_data(file))
        time.sleep(3)

    # return [file.name for file in files]
    print(type(text))
    print(text)
    chroma_file_data(text)
    # chroma_query("我在寻找草莓种植相关的论文，你有什么好的推荐吗")
    return chroma_query("我在寻找草莓种植相关的论文，你有什么好的推荐吗")


# # 创建 Gradio 接口
# iface = gr.Interface(
#     fn=upload_files,                       # 指定处理函数
#     inputs=File(label="上传文件", file_count="multiple"),  # 允许上传多个文件
#     outputs="text",                        # 输出格式为文本
#     title="文件上传示例",                   # 界面标题
#     description="上传文件，显示文件路径"    # 界面描述
# )
#
# # 启动 Gradio 应用程序
# iface.launch()
