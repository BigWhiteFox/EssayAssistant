import gradio as gr
from gradio.components import Image, File, Slider
from moonshot import paper_analysis, upload_file_data
from divide import segmentation
from messages import fox_chat_chat, fox_say_read_paper, fox_say_read_paper_combine_with_analysis, fox_write_arxiv
from get_data_consensus import extract_data
from chroma import chroma_data, chroma_query, chroma_file_data, chroma_query_write
from get_data import run
import time
import webbrowser

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

    var text = 'Welcome to 狐言乱语! 😺 ';
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
def fox_chat(key, text, history, image, max_new_tokens, top_p, temperature):
    history.append((text, fox_chat_chat(key=key, message=text, image_path=image,
                                        temperature=temperature, top_p=top_p, max_tokens=max_new_tokens)))
    return "", history


# 以下是狐说页面函数
def fox_say_file_analysis(key, file):
    if file is None:
        return "No file uploaded"
    response = paper_analysis(api_key=key, file=file)
    collected_messages = []
    for idx, chunk in enumerate(response):
        chunk_message = chunk.choices[0].delta
        if not chunk_message.content: continue
        collected_messages.append(chunk_message)  # save the message
        yield ''.join([m.content for m in collected_messages])


def fox_say_chat(key, message, message2, history, combine, combine2, max_new_tokens, top_p, temperature):
    # 这里是需要有图像输入，
    if divide_pth is not None and (combine or combine2):
        # 此时有图像输入，但只需要结合图片，不需要结合分析
        if combine and not combine2:
            history.append((message, fox_say_read_paper(key=key,
                                                        message=message,
                                                        image_path=divide_pth[page - 1],
                                                        temperature=temperature,
                                                        top_p=top_p,
                                                        max_tokens=max_new_tokens)))
            return "", history
        # 此时有图像输入，但只需要结合分析，不需要结合图片
        elif combine2 and not combine:
            history.append((message, fox_say_read_paper_combine_with_analysis(key=key,
                                                                              message=message,
                                                                              analysis_input=message2,
                                                                              image_path=None,
                                                                              temperature=temperature,
                                                                              top_p=top_p,
                                                                              max_tokens=max_new_tokens)))
            return "", history
        # 此时有图像输入，需要结合图片和分析
        else:
            history.append((message, fox_say_read_paper_combine_with_analysis(key=key,
                                                                              message=message,
                                                                              analysis_input=message2,
                                                                              image_path=divide_pth[page - 1],
                                                                              temperature=temperature,
                                                                              top_p=top_p,
                                                                              max_tokens=max_new_tokens
                                                                              )))
            return "", history
    # 不管怎么样，这是无图，无需结合图像和分析的回答。和有图但不需要结合图像和分析的回答。
    else:
        history.append((message, fox_say_read_paper(key=key,
                                                    message=message,
                                                    image_path=None,
                                                    temperature=temperature,
                                                    top_p=top_p,
                                                    max_tokens=max_new_tokens)))
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
def fox_find_data(key, text_input):
    relevance, reference = run(llm_key=key, text=text_input, n=2)
    consensus_data = extract_data(text_input, 1)
    chroma_data(1)
    chroma_data(2)
    chroma_data(3)
    return relevance, reference, consensus_data


def fox_find_chat(key, message, history):
    history.append((message, chroma_query(llm_key=key, query=message)))
    return "", history


# 以下是狐写页面函数
def fox_write(key, query, max_new_tokens, top_p, temperature):
    # 在这里处理输入
    response = chroma_query_write(llm_key=key, query=query,
                                  max_tokens=max_new_tokens, top_p=top_p, temperature=temperature)
    collected_messages = []
    for idx, chunk in enumerate(response):
        chunk_message = chunk.choices[0].delta
        if not chunk_message.content: continue
        collected_messages.append(chunk_message)  # save the message
        yield ''.join([m.content for m in collected_messages])


def fox_write_extra(message):
    msg = fox_write_arxiv(message)
    # 初始化一个标志，用于指示是否已经遇到非空内容
    started_output = False
    collected_messages = []
    for content in msg.content:
        # 如果内容是非空的，设置标志为True并打印内容
        if content.answer.strip():
            started_output = True
        if started_output:
            collected_messages.append(content.answer)
            yield ''.join([m for m in collected_messages])


def fox_write_upload(key, files):
    # 返回上传文件的路径列表
    text = []
    for file in files:
        text.append(upload_file_data(api_key=key, file=file))
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
                with gr.Accordion("Key", open=False):
                    llm_key = gr.Textbox(label="请输入大模型API Key", placeholder="请输入你的API Key",
                                         value="bbbd0deb2e83869a810a3aa32d866b36.z8W6AkgbgewipUae")
                    moonshot_key = gr.Textbox(label="请输入你的月之暗面API Key", placeholder="请输入你的API Key",
                                              value="sk-by3QJVIDS2QakUYRVNe196GgP64IYSKx0BoCBlpN9ze171e0")
                image_upload = Image(type="filepath", label="你有什么想给大狐狸看的吗？")
                with gr.Accordion("Parameters", open=False):
                    with gr.Column():
                        max_new_tokens1 = Slider(minimum=256, maximum=4096, value=1024, step=1, label='Max new tokens')
                        top_p1 = Slider(minimum=0.01, maximum=1, value=0.7, step=0.01, label='Top_p')
                        temperature1 = Slider(minimum=0.01, maximum=1, value=0.8, step=0.01, label='Temperature')
            with gr.Column():
                chat_box2 = gr.Chatbot(label="嗨~~大狐狸🦊超开心遇见你！你最近有什么好玩的事情想和我分享吗？🌟 ")
                chat_box2.like(None)
                with gr.Row():
                    # 创建一个Textbox组件作为输入栏
                    fox_chat_chat_input = gr.Textbox(label="", placeholder="请输入您的消息并按回车↩")
                clear2 = gr.ClearButton([fox_chat_chat_input, chat_box2, image_upload])
        fox_chat_chat_input.submit(fn=fox_chat, inputs=[llm_key, fox_chat_chat_input, chat_box2,
                                                        image_upload, max_new_tokens1, top_p1, temperature1],
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
                    fox_say_paper_button = gr.Button(value="让大狐狸来分析一下🕵️‍♂️")
                    checkbox = gr.Checkbox(label="结合此页展示回答")
                    checkbox2 = gr.Checkbox(label="结合论文解读回答")
                with gr.Accordion("Parameters", open=False):
                    with gr.Column():
                        max_new_tokens2 = Slider(minimum=256, maximum=4096, value=1024, step=1, label='Max new tokens')
                        top_p2 = Slider(minimum=0.01, maximum=1, value=0.7, step=0.01, label='Top_p')
                        temperature2 = Slider(minimum=0.01, maximum=1, value=0.8, step=0.01, label='Temperature')
            # 右侧界面： 解读框、聊天框、提交按钮、清空按钮
            with gr.Column(scale=10):
                pdf_text_display = gr.Textbox(label="论文解读", lines=20, max_lines=20)

                # 创建一个Chatbot组件作为聊天框
                chat_box = gr.Chatbot(label="What does the 🦊 say?")
                chat_box.like(None)

                with gr.Row():
                    # 创建一个Textbox组件作为输入栏
                    fox_say_chat_input = gr.Textbox(label="", placeholder="请输入您的消息并按回车↩")
                clear = gr.ClearButton([fox_say_chat_input, chat_box])

            # 左侧界面功能链接
            fox_say_paper_button.click(fn=fox_say_file_analysis,
                                       inputs=[moonshot_key, pdf_upload], outputs=pdf_text_display)
            pdf_upload.upload(fn=fox_say_image_show, inputs=pdf_upload, outputs=[pdf_image_display, page_num])
            switch_button_1.click(fn=fox_say_image_switch1, inputs=None, outputs=[pdf_image_display, page_num])
            switch_button_2.click(fn=fox_say_image_switch2, inputs=None, outputs=[pdf_image_display, page_num])
            # 右侧界面功能链接
            fox_say_chat_input.submit(fn=fox_say_chat, inputs=[llm_key, fox_say_chat_input, pdf_text_display,
                                                               chat_box, checkbox, checkbox2, max_new_tokens2,
                                                               top_p2, temperature2],
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
                paper_find_chat.like(None)
                with gr.Row():
                    # 创建一个Textbox组件作为输入栏
                    fox_find_chat_input = gr.Textbox(label="", placeholder="请输入您的消息并按回车↩")
                clear3 = gr.ClearButton([fox_find_chat_input, paper_find_chat,
                                         keyword_search, baidu_relevance, consensus])
        # 界面功能链接
        keyword_search.submit(fn=fox_find_data, inputs=[llm_key, keyword_search],
                              outputs=[baidu_relevance, baidu_reference, consensus])
        # 将处理函数绑定到submit_button组件
        fox_find_chat_input.submit(fn=fox_find_chat, inputs=[llm_key, fox_find_chat_input, paper_find_chat],
                                   outputs=[fox_find_chat_input, paper_find_chat])

    with gr.Tab("狐写"):
        with gr.Row():
            with gr.Column(scale=1):
                fox_write_input = gr.Textbox(label="你想让大狐狸写什么样的综述🔬？", placeholder="请输入您的消息并按回车↩")
                upload_file = File(label="上传你想要一起分析的论文👀", file_count="multiple")
                upload_file_button = gr.Button(value="上传文件")
                # clear4 = gr.ClearButton([fox_write_input, paper_summary_chat, upload_file])
                with gr.Accordion("Parameters", open=False):
                    with gr.Column():
                        max_new_tokens3 = Slider(minimum=2048, maximum=8192, value=4096, step=1, label='Max new tokens')
                        top_p3 = Slider(minimum=0.01, maximum=1, value=0.7, step=0.01, label='Top_p')
                        temperature3 = Slider(minimum=0.01, maximum=1, value=0.8, step=0.01, label='Temperature')
            with gr.Column(scale=5):
                with gr.Tab("Vector Database"):
                    paper_summary_chat = gr.Textbox(label="来看看大狐狸从本地知识库找数据写的综述，写的不好还请见谅。😣",
                                                    lines=20, max_lines=20, show_copy_button=True)
                with gr.Tab("Arxiv"):
                    paper_arxiv_chat = gr.Textbox(label="来看看大狐狸从arxiv找数据写的综述，写的不好还请见谅。😣",
                                                  lines=20, max_lines=20, show_copy_button=True)
        upload_file_button.click(fn=fox_write_upload, inputs=[moonshot_key, upload_file], outputs=None)
        fox_write_input.submit(fn=fox_write, inputs=[llm_key, fox_write_input, max_new_tokens3, top_p3, temperature3],
                               outputs=[paper_summary_chat])
        fox_write_input.submit(fn=fox_write_extra, inputs=fox_write_input, outputs=paper_arxiv_chat)

# 启动界面
webbrowser.open("http://localhost:7888")
demo.queue().launch(server_name="0.0.0.0", server_port=7888, share=False)
