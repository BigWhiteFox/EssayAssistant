from openai import OpenAI
from pathlib import Path

# 替换为你的 OpenAI API 密钥和正确的 base_url
api_key = "sk-yourkey"
base_url = "https://api.moonshot.cn/v1"

client = OpenAI(api_key=api_key, base_url=base_url)


def paper_analysis(file):
    file_object = client.files.create(file=Path(file.name), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text

    messages = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你是一名负责向学生解读论文的教授。"
                       "你会为学生提供安全，有帮助，准确的回答。同时，你会努力做到尽可能的简单易懂并足够深入。"
                       "Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {
            "role": "system",
            "content": file_content,
        },
        {"role": "user", "content": "请你帮我分析一下这篇论文的内容，你需要从以下角度分析并尽可能的回答问题，此外，字数尽可能多。"
                                    "1. 文章概述：这篇文章的主要研究内容是什么？文章采用了什么方法？研究发现了什么？得出了什么结论？"
                                    "2. 研究背景：为什么要进行这项研究？研究背景是什么？现有的研究有哪些不足或空白？"
                                    "3. 研究目标及价值：这项研究的具体目标是什么？研究的潜在影响和价值是什么？"
                                    "4. 研究方法与手段：研究采用了哪些方法和技术？这些方法是否有创新之处？实验设计和数据收集是如何进行的？"
                                    "5. 研究结果：研究的主要结果是什么？这些结果是如何展示的（图表、数据等）？结果是否支持研究假设？"
                                    "6. 讨论：研究结果与预期是否一致？结果的意义和影响是什么？是否有任何意外的发现？研究的局限性和不足是什么？"
                                    "7. 研究结论：研究得出了哪些主要结论？这些结论对领域的发展有何贡献？"
                                    "8. 研究的创新性及缺点：研究的创新点是什么？研究有哪些不足之处？"
                                    "9. 未来研究方向：基于这项研究，未来的研究方向是什么？有哪些未解决的问题或新的研究机会？"},
    ]

    response = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
        stream=True,
    )
    return response


def upload_file_data(file):
    file_object = client.files.create(file=Path(file.name), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text

    messages = [
        {
            "role": "system",
            "content": "你负责分析上传的论文并按照模板返回相应信息，如果没有则填暂无。"
                       "模板格式如下所示："
                       "Title:  , Abstract:  , Journal:  , Doi:  , Authors: ",
        },
        {
            "role": "system",
            "content": file_content,
        },
        {"role": "user", "content": "请你帮我分析一下上传的论文并按照模板回答，不需要其它额外的任何信息, 也不需要输出换行符，谢谢。"},
    ]

    response = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
        stream=False,
    )
    return response.choices[0].message.content

