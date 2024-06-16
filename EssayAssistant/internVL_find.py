from openai import OpenAI
import requests

# OpenAI API Key
api_key = "YOUR_OPENAI_API_KEY"

# Replace with your actual API URL
base_url = "http://0.0.0.0:23333/v1"
client = OpenAI(api_key=api_key, base_url=base_url)
model_name = client.models.list().data[0].id


def summary_paper(text_input):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "您将收到一篇文章的标题和对应的摘要。"
                                "请仔细阅读这些信息，将其提炼成一个简短且精准的句子，以概括文章的主要内容。"
                                "确保您的回答只包含一句话，并且尽可能简洁明了。"
                                "此外，如果原文是英文，请用英文回答，如果是中文，请用中文回答。"
                                "现在，请根据提供的标题和摘要生成一句话概要。"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_input
                    }
                ]
            }
        ],
    }

    response = requests.post(url="http://0.0.0.0:23333/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']


def chat_paper(text_input, relevance_data, reference_data):
    relevance_data_str = "".join(str(item) for item in relevance_data)
    reference_data_str = "".join(str(item) for item in reference_data)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "您将扮演一位博学的教授，致力于协助学生发现与其研究兴趣相关的学术论文。"
                                "您的任务是仔细审查以下列出的论文信息，这些信息是根据学生的关键词查询生成的。"
                                "每篇论文的信息都按照固定的格式组织，包括论文标题、论文关键词和论文摘要。"
                                "请根据这些信息，为学生提供详尽的回答，解决其对论文的任何疑问。"
                                + relevance_data_str +
                                reference_data_str +
                                "请根据所提供的数据，回答学生关于论文的查询。"
                                "请确保在回答问题时，结合所提供的英文语料和中文语料，并使用中文回答。"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_input
                    }
                ]
            }
        ],
    }

    response = requests.post(url="http://0.0.0.0:23333/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']


"""
# 创建 Gradio 界面
iface = gr.Interface(
    fn=read_paper,
    inputs=[gr.Textbox(label="Text Input"), gr.Image(label="Image Input")],
    outputs=gr.Textbox(label="Result"),
    title="Paper Reading Interface"
)

# 启动界面
iface.launch()"""
