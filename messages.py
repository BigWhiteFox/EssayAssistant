from zhipuai import ZhipuAI
import appbuilder
import os
import gradio as gr
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def fox_chat_chat(key, message, image_path=None, temperature=0.2, top_p=0.8, max_tokens=1024):
    client = ZhipuAI(api_key=key)  # 填写您自己的APIKey
    if image_path is None:
        # 注意以下示例正确运行依赖的条件包括：
        # 1. 在百度智能云千帆AppBuilder官网使用AppBuilderClient创建应用且应用已发布
        # 2. 密钥正确有效
        # 3. 密钥需要与发布应用正确对应，即需要使用发布应用的账户下的密钥

        # 配置密钥与应用ID
        os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-cQuNNcvY1DmVHPfPB9qpS/3706e064cd789835e398f1a5aa57f90d6657c3b9"
        app_id = "1e2a9e12-e740-413a-88ec-af2d5cc3e8f1"

        # 初始化Agent
        builder = appbuilder.AppBuilderClient(app_id)

        # 创建会话ID
        conversation_id = builder.create_conversation()

        # 执行对话
        msg = builder.run(conversation_id, query=message)
        print("助手回答内容：", msg.content.answer)
        return msg.content.answer
    else:
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="glm-4v",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "system",
                    "content": "你将扮演一位心理疗愈师，通过幽默风趣的对话帮助疲惫的学生缓解压力。"
                               "每个问题之后会附上一张图片，请你耐心地查看并给予幽默风趣的回应。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            # stream=True,  # 是否开启流式输出
            temperature=temperature,  # 随机性，取值范围[0,1]，值越大表示输出的随机性越小
            top_p=top_p,  # nucleus sampling的top_p值，取值范围[0,1]，值越大表示输出的随机性越小
            max_tokens=max_tokens,  # 生成文本的最大长度
        )
        return response.choices[0].message.content


def fox_say_read_paper(key, message, image_path=None, temperature=0.2, top_p=0.8, max_tokens=1024):
    client = ZhipuAI(api_key=key)  # 填写您自己的APIKey
    if image_path is None:
        response = client.chat.completions.create(
            model="glm-4-0520",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "system",
                    "content": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                               "你的任务是提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            # stream=True,  # 是否开启流式输出
            temperature=temperature,  # 随机性，取值范围[0,1]，值越大表示输出的随机性越小
            top_p=top_p,  # nucleus sampling的top_p值，取值范围[0,1]，值越大表示输出的随机性越小
            max_tokens=max_tokens,  # 生成文本的最大长度
        )
        return response.choices[0].message.content
    else:
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="glm-4v",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "system",
                    "content": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                               "在每个问题的末尾，学生提供了一张可能揭示其疑问来源或理解难点的论文截图。"
                               "你的任务是结合论文相关截图，提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            # stream=True,  # 是否开启流式输出
            temperature=temperature,  # 随机性，取值范围[0,1]，值越大表示输出的随机性越小
            top_p=top_p,  # nucleus sampling的top_p值，取值范围[0,1]，值越大表示输出的随机性越小
            max_tokens=max_tokens,  # 生成文本的最大长度
        )
        return response.choices[0].message.content


def fox_say_read_paper_combine_with_analysis(key, message, analysis_input, image_path=None,
                                             temperature=0.2, top_p=0.8, max_tokens=1024):
    client = ZhipuAI(api_key=key)
    if image_path is None:
        response = client.chat.completions.create(
            model="glm-4-0520",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "system",
                    "content": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                               "在你面前是一篇人工智能生成的论文摘要，学生针对这篇论文提出了一些问题。"
                               + analysis_input +
                               "你的任务是结合论文摘要，提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            # stream=True,  # 是否开启流式输出
            temperature=temperature,  # 随机性，取值范围[0,1]，值越大表示输出的随机性越小
            top_p=top_p,  # nucleus sampling的top_p值，取值范围[0,1]，值越大表示输出的随机性越小
            max_tokens=max_tokens,  # 生成文本的最大长度
        )
        return response.choices[0].message.content
    else:
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="glm-4v",  # 填写需要调用的模型名称
            messages=[
                {
                    "role": "system",
                    "content": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                               "在你面前是一篇人工智能生成的论文摘要，学生针对这篇论文提出了一些问题。"
                               + analysis_input +
                               "在每个问题的末尾，学生提供了一张可能揭示其疑问来源或理解难点的论文截图。"
                               "你的任务是结合论文摘要和相关截图，提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            # stream=True,  # 是否开启流式输出
            temperature=temperature,  # 随机性，取值范围[0,1]，值越大表示输出的随机性越小
            top_p=top_p,  # nucleus sampling的top_p值，取值范围[0,1]，值越大表示输出的随机性越小
            max_tokens=max_tokens,  # 生成文本的最大长度
        )
        return response.choices[0].message.content


def summary_paper(key, message):
    client = ZhipuAI(api_key=key)
    response = client.chat.completions.create(
        model="glm-4-flash",  # 填写需要调用的模型名称
        messages=[
            {
                "role": "system",
                "content": "您将收到一篇文章的标题和对应的摘要。"
                           "请仔细阅读这些信息，将其提炼成一个简短且精准的句子，以概括文章的主要内容。"
                           "确保您的回答只包含一句话，并且尽可能简洁明了。"
                           "此外，如果原文是英文，请用英文回答，如果是中文，请用中文回答。"
                           "现在，请根据提供的标题和摘要生成一句话概要。"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        stream=False,  # 是否开启流式输出
    )
    return response.choices[0].message.content


def fox_find_chat(key, message, results, temperature=0.2, top_p=0.8, max_tokens=1024):
    client = ZhipuAI(api_key=key)
    response = client.chat.completions.create(
        model="glm-4-0520",  # 填写需要调用的模型名称
        messages=[
            {
                "role": "system",
                "content": "你是一名专业的学术研究助手，你的任务是帮助用户寻找相关论文。"
                           "你将会接收到一系列从向量数据库中检索出的论文信息，"
                           "每条信息都包含以下字段：'Title', 'Authors', 'Abstract', 'DOI'。"
                           "这些论文信息是基于用户查询自动检索得到的，并且已经按照相关性排序。"
                           + str(results) +
                           "你的任务是根据这些论文信息，选取内容合适的部分回答用户问题，请不要全选，也不要只选取一两个。"
                           "语言应该适合学术交流，清晰、准确、客观。"
                           "对每篇论文的推荐和解说，应当包含个人的见解和点评，而不是罗列其内容。"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        # stream=True,  # 是否开启流式输出
        temperature=temperature,  # 随机性，取值范围[0,1]，值越大表示输出的随机性越小
        top_p=top_p,  # nucleus sampling的top_p值，取值范围[0,1]，值越大表示输出的随机性越小
        max_tokens=max_tokens,  # 生成文本的最大长度
    )
    return response.choices[0].message.content


def fox_write_chat(key, message, results, temperature=0.2, top_p=0.8, max_tokens=4096):
    client = ZhipuAI(api_key=key)
    response = client.chat.completions.create(
        model="glm-4-0520",  # 填写需要调用的模型名称
        messages=[
            {
                "role": "system",
                "content": "你是一名专业的学术研究助手，你的任务是帮助用户总结相关论文的共性，并叙说对应论文的特点，如技术细节等。"
                           "你将会接收到一系列从向量数据库中检索出的论文信息，"
                           "每条信息都包含但不限于以下字段：'Title', 'Authors', 'Abstract', 'DOI'。"
                           "这些论文信息是基于用户查询自动检索得到的，并且已经按照相关性排序。"
                           + str(results) +
                           "你的回答应当根据这些论文信息，并且全面、准确且连贯，涵盖关键发现、研究主题、趋势以及任何其他相关的重要信息。"
                           "此外，你还需要知道：综述应该是对所提供论文的精华总结，同时也要确保信息的准确性和完整性。"
                           "如果有需要，请遵循以下步骤来撰写综述："
                           "1. 仔细阅读并理解每篇论文的标题、作者、摘要、DOI和出版年份。"
                           "2. 分析论文之间的联系和差异，识别核心主题和研究趋势。"
                           "3. 撰写综述，确保综述的结构清晰，内容有逻辑性，语言流畅。"
                           "4. 在综述中引用具体的研究成果时，请注明作者和出版年份，以增加综述的权威性。"
                           "5. 如果有额外的见解或分析，可以在综述中适当提出，但要确保这些内容是基于所提供论文信息的合理推断。"
                           "如果有需要，你应当知道综述要求："
                           "- 综述应该是对学术论文的综合总结，而不是单纯的论文列表。"
                           "- 综述应该包含对研究领域的深入分析和对未来研究方向的展望。"
                           "- 综述应该是有机结合多篇论文信息的产物，而不是孤立地介绍每篇论文。"
                           "- 综述的语言应该适合学术交流，清晰、准确、客观。"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        stream=True,  # 是否开启流式输出
        temperature=temperature,  # 随机性，取值范围[0,1]，值越大表示输出的随机性越小
        top_p=top_p,  # nucleus sampling的top_p值，取值范围[0,1]，值越大表示输出的随机性越小
        max_tokens=max_tokens,  # 生成文本的最大长度
    )
    return response


def fox_write_arxiv(message):
    # 配置密钥与应用ID
    os.environ["APPBUILDER_TOKEN"] = "bce-v3/ALTAK-cQuNNcvY1DmVHPfPB9qpS/3706e064cd789835e398f1a5aa57f90d6657c3b9"
    app_id = "0dd7ed8a-f977-4ac6-a3eb-c5ec1b955c6c"

    # 初始化Agent
    builder = appbuilder.AppBuilderClient(app_id)

    # 创建会话ID
    conversation_id = builder.create_conversation()

    # 执行对话
    msg = builder.run(conversation_id, query=message, stream=True)
    print("助手回答内容：", msg)
    return msg


# 定义一个简单的函数，它接受两个输入并返回一个输出
# def process_inputs(input1, input2):
#     # 在这里处理输入，例如进行一些计算或数据操作
#     response = fox_chat_chat(input1, input2)
#     collected_messages = []
#     for idx, chunk in enumerate(response):
#         chunk_message = chunk.choices[0].delta
#         if not chunk_message.content: continue
#         collected_messages.append(chunk_message)  # save the message
#         yield ''.join([m.content for m in collected_messages])
#
#
# # 创建 Gradio 界面
# iface = gr.Interface(
#     fn=process_inputs,  # 指定处理函数
#     inputs=["text", "text"],  # 指定两个输入框，类型为文本
#     outputs="chatbot",  # 指定一个输出框，类型为文本
#     title="简单的输入输出界面",  # 界面的标题
#     description="请输入两个文本，然后查看结果"  # 界面的描述
# )
#
# # 启动界面
# iface.launch()
