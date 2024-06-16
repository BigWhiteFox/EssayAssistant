from openai import OpenAI
import base64
import requests


# OpenAI API Key
api_key = "YOUR_OPENAI_API_KEY"

# Replace with your actual API URL
base_url = "http://0.0.0.0:23333/v1"
client = OpenAI(api_key=api_key, base_url=base_url)
model_name = client.models.list().data[0].id


def read_paper(max1, p, k, tem, text_input, image_input=None):
    if image_input is None:
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
                            "text": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                                    "你的任务是提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"
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
            "max_tokens": max1,
            "top_p": p,
            "top_k": k,
            "temperature": tem,
            "stream": False,
        }

        response = requests.post(url="http://0.0.0.0:23333/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    else:
        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Path to your image
        image_path = image_input

        # Getting the base64 string
        base64_image = encode_image(image_path)

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
                            "text": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                                    "在每个问题的末尾，学生提供了一张可能揭示其疑问来源或理解难点的论文截图。"
                                    "你的任务是结合论文相关截图，提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_input
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
            "max_tokens": max1,
            "top_p": p,
            "top_k": k,
            "temperature": tem,
            "stream": False,
        }

        response = requests.post(url="http://0.0.0.0:23333/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']


def read_paper_combine_with_analysis(max1, p, k, tem, text_input, analysis_input, image_input=None):
    if image_input is None:
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
                            "text": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                                    "在你面前是一篇人工智能生成的论文摘要，学生针对这篇论文提出了一些问题。"
                                    + analysis_input +
                                    "你的任务是结合论文摘要，提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"

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
            "max_tokens": max1,
            "top_p": p,
            "top_k": k,
            "temperature": tem,
            "stream": False,
        }

        response = requests.post(url="http://0.0.0.0:23333/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    else:

        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Path to your image
        image_path = image_input

        # Getting the base64 string
        base64_image = encode_image(image_path)

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
                            "text": "你扮演一位博学的教授，你的角色是耐心解答学生的疑问。"
                                    "在你面前是一篇人工智能生成的论文摘要，学生针对这篇论文提出了一些问题。"
                                    + analysis_input +
                                    "在每个问题的末尾，学生提供了一张可能揭示其疑问来源或理解难点的论文截图。"
                                    "你的任务是结合论文摘要和相关截图，提供深入、全面且易于理解的答案，以便帮助学生解决疑问。"

                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_input
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
            "max_tokens": max1,
            "top_p": p,
            "top_k": k,
            "temperature": tem,
            "stream": False,
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
