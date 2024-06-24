import gradio as gr
from gradio.components import Image, File, Slider
from moonshot import paper_analysis, upload_file_data
from divide import segmentation
from internVL_read import read_paper, read_paper_combine_with_analysis
# from get_data_baidu_relevance import extract_data, scrape_publications, summarize_data, get_specific_columns
# from get_data_baidu_reference import (extract_data_reference, scrape_publications_reference,
#                                       summarize_data_reference, get_specific_columns_reference)
from internVL_find import chat_paper
from internVL_chat import chat
from get_data_consensus import extract_data
from chroma import chroma_data, chroma_query, chroma_file_data, chroma_query_write
from get_data import run
import time
from fox_write_verification import upload_files

# 在模块级别定义全局变量
divide_pth = None
page = 1


js = """
function createGradioAnimation() {
    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.style.fontSize = '2em';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    container.style.marginBottom = '20px';

    var text = 'Welcome to 狐言乱语!';
    for (var i = 0; i < text.length; i++) {
        (function(i){
            setTimeout(function(){
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.5s';
                letter.innerText = text[i];

                container.appendChild(letter);

                setTimeout(function() {
                    letter.style.opacity = '1';
                }, 50);
            }, i * 250);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    gradioContainer.insertBefore(container, gradioContainer.firstChild);

    return 'Animation created';
}
"""


# 以下是狐聊页面函数
def fox_chat(text, history, image, max2, p2, k2, tem2):
    history.append((text, chat(text_input=text, image_input=image, max2=max2, p=p2, k=k2, tem=tem2)))
    return "", history


# 以下是狐说页面函数
def fox_say_file_analysis(file):
    if file is None:
        return "No file uploaded"
    response = paper_analysis(file)
    collected_messages = []
    for idx, chunk in enumerate(response):
        chunk_message = chunk.choices[0].delta
        if not chunk_message.content: continue
        collected_messages.append(chunk_message)  # save the message
        yield ''.join([m.content for m in collected_messages])


def fox_say_chat(message, message2, history, combine, combine2, max1, p, k, tem):
    # 这里是需要有图像输入，
    if divide_pth is not None and (combine or combine2):
        # 此时有图像输入，但只需要结合图片，不需要结合分析
        if combine and not combine2:
            history.append((message, read_paper(text_input=message,
                                                image_input=divide_pth[page - 1],
                                                max1=int(max1),
                                                p=float(p),
                                                k=float(k),
                                                tem=float(tem),
                                                )))
            return "", history
        # 此时有图像输入，但只需要结合分析，不需要结合图片
        elif combine2 and not combine:
            history.append((message, read_paper_combine_with_analysis(text_input=message,
                                                                      analysis_input=message2,
                                                                      image_input=None,
                                                                      max1=int(max1),
                                                                      p=float(p),
                                                                      k=float(k),
                                                                      tem=float(tem),
                                                                      )))
            return "", history
        # 此时有图像输入，需要结合图片和分析
        else:
            history.append((message, read_paper_combine_with_analysis(text_input=message,
                                                                      analysis_input=message2,
                                                                      image_input=divide_pth[page - 1],
                                                                      max1=int(max1),
                                                                      p=float(p),
                                                                      k=float(k),
                                                                      tem=float(tem),
                                                                      )))
            return "", history
    # 不管怎么样，这是无图，无需结合图像和分析的回答。和有图但不需要结合图像和分析的回答。
    else:
        history.append((message, read_paper(text_input=message,
                                            image_input=None,
                                            max1=int(max1),
                                            p=float(p),
                                            k=float(k),
                                            tem=float(tem),
                                            )))
        return "", history, ""


def fox_say_image_show(file):
    global divide_pth, page
    page = 1
    divide_pth = segmentation(file)
    return divide_pth[0], f"当前为第1/{len(divide_pth)}页"


def fox_say_image_switch1():
    global divide_pth, page
    if page == 1:
        return divide_pth[page - 1], f"当前为第{page}/{len(divide_pth)}页"
    else:
        page -= 1
        return divide_pth[page - 1], f"当前为第{page}/{len(divide_pth)}页"


def fox_say_image_switch2():
    global divide_pth, page
    if page == len(divide_pth):
        return divide_pth[page - 1], f"当前为第{page}/{len(divide_pth)}页"
    else:
        page += 1
        return divide_pth[page - 1], f"当前为第{page}/{len(divide_pth)}页"


# 以下是狐找页面函数
tittle_and_abstract_relevance = []
tittle_and_abstract_reference = []
tittle_and_abstract_consensus = []


# def fox_find_baidu_relevance(text_input):
#     href_list_want = extract_data(1, text_input)
#     # print(href_list)
#     row_data = scrape_publications(href_list_want)
#     global tittle_and_abstract_relevance
#     tittle_and_abstract_relevance = get_specific_columns(row_data)
#     # print("tittle_and_abstract_relevance:\n", tittle_and_abstract_relevance)
#     # 打印DataFrame
#     # print(df.shape[0])
#     new_data = summarize_data(row_data)
#     return new_data
#
#
# def fox_find_baidu_reference(text_input):
#     href_list_want = extract_data_reference(1, text_input)
#     # print(href_list)
#     row_data = scrape_publications_reference(href_list_want)
#     global tittle_and_abstract_reference
#     tittle_and_abstract_reference = get_specific_columns_reference(row_data)
#     # print("tittle_and_abstract_relevance:\n", tittle_and_abstract_relevance)
#     # 打印DataFrame
#     # print(df.shape[0])
#     new_data = summarize_data_reference(row_data)
#     return new_data

def fox_find_data(text_input):
    relevance, reference = run(text_input, 2)
    consensus_data = extract_data(text_input, 1)
    chroma_data(1)
    chroma_data(2)
    chroma_data(3)
    return relevance, reference, consensus_data


def fox_find_chat(message, history):
    # history.append((message, chat_paper(text_input=message,
    #                                     relevance_data=tittle_and_abstract_relevance,
    #                                     reference_data=tittle_and_abstract_reference)))
    history.append((message, chroma_query(message)))
    return "", history


# 以下是狐写页面函数
def fox_write(query, history):
    history.append((query, chroma_query_write(query)))
    return "", history


def fox_write_upload(files):
    # 返回上传文件的路径列表
    text = []
    for file in files:
        text.append(upload_file_data(file))
        time.sleep(3)

    # return [file.name for file in files]
    print(type(text))
    print(text)
    chroma_file_data(text)



# 创建 Gradio blocks 界面
with gr.Blocks(theme='rawrsor1/Everforest', js=js) as demo:
    with gr.Tab("狐聊"):
        with gr.Row():
            with gr.Column():
                image_upload = Image(type="filepath", label="你有什么想给大狐狸看的吗？")
                with gr.Accordion("Parameters", open=False):
                    with gr.Column():
                        max_new_tokens2 = Slider(256,
                                                 4096,
                                                 value=1024,
                                                 step=1,
                                                 label='Max new tokens')
                        top_p2 = Slider(0.01, 1, value=0.7, step=0.01, label='Top_p')
                        top_k2 = Slider(20, 80, value=40, step=1, label='Top_k')
                        temperature2 = Slider(0.01,
                                              1,
                                              value=0.8,
                                              step=0.01,
                                              label='Temperature')

            with gr.Column():
                chat_box2 = gr.Chatbot(label="Chatbot")
                with gr.Row():
                    # 创建一个Textbox组件作为输入栏
                    fox_chat_chat_input = gr.Textbox(label="", placeholder="请输入你的消息...")
                    # 创建一个Button组件作为提交按钮
                    fox_chat_chat_button = gr.Button(value="发送")
                clear2 = gr.ClearButton([fox_chat_chat_input, chat_box2, image_upload])
        fox_chat_chat_button.click(fn=fox_chat, inputs=[fox_chat_chat_input, chat_box2,
                                                        image_upload, max_new_tokens2,
                                                        top_p2, top_k2, temperature2],
                                   outputs=[fox_chat_chat_input, chat_box2])
        fox_chat_chat_input.submit(fn=fox_chat, inputs=[fox_chat_chat_input, chat_box2,
                                                        image_upload, max_new_tokens2,
                                                        top_p2, top_k2, temperature2],
                                   outputs=[fox_chat_chat_input, chat_box2])

    with gr.Tab("狐说"):
        with gr.Row():
            # 左侧界面： PDF展示、上传、是否结合、页码扫描、参数设置
            with gr.Column(scale=15):
                # PDF页面展示组件
                pdf_image_display = Image(type="filepath", label="论文展示")

                with gr.Row():
                    # PDF文件上传组件
                    pdf_upload = File(label="上传PDF")
                    switch_button_1 = gr.Button(value="⬅️", min_width=1, size="sm")
                    page_num = gr.Textbox(label="")
                    switch_button_2 = gr.Button(value="➡️", min_width=1, size="sm")

                with gr.Row():
                    fox_say_paper_button = gr.Button(value="🦊分析")
                    checkbox = gr.Checkbox(label="结合此页展示回答")
                    checkbox2 = gr.Checkbox(label="结合论文解读回答")
                with gr.Accordion("Parameters", open=False):
                    with gr.Column():
                        max_new_tokens = Slider(256,
                                                4096,
                                                value=1024,
                                                step=1,
                                                label='Max new tokens')
                        top_p = Slider(0.01, 1, value=0.7, step=0.01, label='Top_p')
                        top_k = Slider(20, 80, value=40, step=1, label='Top_k')
                        temperature = Slider(0.01,
                                             1,
                                             value=0.8,
                                             step=0.01,
                                             label='Temperature')

            # 右侧界面： 解读框、聊天框、提交按钮、清空按钮
            with gr.Column(scale=10):
                pdf_text_display = gr.Textbox(label="论文解读")

                # 创建一个Chatbot组件作为聊天框
                chat_box = gr.Chatbot(label="What does the fox say?")

                with gr.Row():
                    # 创建一个Textbox组件作为输入栏
                    fox_say_chat_input = gr.Textbox(label="", placeholder="请输入你的消息...")
                    # 创建一个Button组件作为提交按钮
                    fox_say_chat_button = gr.Button(value="发送")
                clear = gr.ClearButton([fox_say_chat_input, chat_box])

            # 左侧界面功能链接
            fox_say_paper_button.click(fn=fox_say_file_analysis, inputs=pdf_upload, outputs=pdf_text_display)
            pdf_upload.upload(fn=fox_say_image_show, inputs=pdf_upload, outputs=[pdf_image_display, page_num])
            switch_button_1.click(fn=fox_say_image_switch1, inputs=None, outputs=[pdf_image_display, page_num])
            switch_button_2.click(fn=fox_say_image_switch2, inputs=None, outputs=[pdf_image_display, page_num])
            # 右侧界面功能链接
            fox_say_chat_input.submit(fn=fox_say_chat, inputs=[fox_say_chat_input, pdf_text_display,
                                                               chat_box, checkbox, checkbox2,
                                                               max_new_tokens, top_p, top_k, temperature],
                                      outputs=[fox_say_chat_input, chat_box])
            # 将处理函数绑定到submit_button组件
            fox_say_chat_button.click(fn=fox_say_chat, inputs=[fox_say_chat_input, pdf_text_display,
                                                               chat_box, checkbox, checkbox2,
                                                               max_new_tokens, top_p, top_k, temperature],
                                      outputs=[fox_say_chat_input, chat_box])

    with gr.Tab("狐找"):
        with gr.Row():
            with gr.Column():
                keyword_search = gr.Textbox(label="输入你想搜索的关键词")
                baidu_relevance = gr.DataFrame(label="百度学术相关序列", height=420)
                baidu_reference = gr.DataFrame(label="百度学术引用序列", height=420)

            with gr.Column():
                consensus = gr.DataFrame(label="ConsensusSJR一二区序列", height=420)
                paper_find_chat = gr.Chatbot(label="和大狐狸聊聊你想找的论文")
                with gr.Row():
                    # 创建一个Textbox组件作为输入栏
                    fox_find_chat_input = gr.Textbox(label="", placeholder="请输入你的消息...")
                    # 创建一个Button组件作为提交按钮
                    fox_find_chat_button = gr.Button(value="发送")
                clear3 = gr.ClearButton([fox_find_chat_input, paper_find_chat,
                                         keyword_search, baidu_relevance, consensus])
        # 界面功能链接
        # keyword_search.submit(fn=fox_find_baidu_relevance, inputs=keyword_search, outputs=baidu_relevance)
        # keyword_search.submit(fn=fox_find_baidu_reference, inputs=keyword_search, outputs=baidu_reference)
        keyword_search.submit(fn=fox_find_data, inputs=keyword_search,
                              outputs=[baidu_relevance, baidu_reference, consensus])
        # 将处理函数绑定到submit_button组件
        fox_find_chat_button.click(fn=fox_find_chat, inputs=[fox_find_chat_input, paper_find_chat],
                                   outputs=[fox_find_chat_input, paper_find_chat])

    with gr.Tab("狐写"):
        with gr.Column():
            paper_summary_chat = gr.Chatbot(label="你想让大狐狸写什么呢？")
            fox_write_input = gr.Textbox(label="输入你的综述要求")
            with gr.Row():
                upload_file = File(label="上传你想要一起分析的论文", file_count="multiple")
                upload_file_button = gr.Button(value="上传文件")
                clear4 = gr.ClearButton([fox_write_input, paper_summary_chat, upload_file])
        upload_file_button.click(fn=fox_write_upload, inputs=upload_file, outputs=None)
        fox_write_input.submit(fn=fox_write, inputs=[fox_write_input, paper_summary_chat],
                               outputs=[fox_write_input, paper_summary_chat])

# 启动界面
demo.queue().launch()
