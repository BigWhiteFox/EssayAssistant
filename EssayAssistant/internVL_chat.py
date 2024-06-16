from openai import OpenAI
import base64
import requests


# OpenAI API Key
api_key = "YOUR_OPENAI_API_KEY"

# Replace with your actual API URL
base_url = "http://0.0.0.0:23333/v1"
client = OpenAI(api_key=api_key, base_url=base_url)
model_name = client.models.list().data[0].id


def chat(max2, p, k, tem, text_input, image_input=None):
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
                            "text": "你将扮演一位心理疗愈师，通过轻松的对话帮助疲惫的学生们缓解压力。"
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
            "max_tokens": max2,
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
                            "text": "你将扮演一位心理疗愈师，通过轻松的对话帮助疲惫的学生们缓解压力。"
                                    "学生们可能会在每个问题之后上传不同类型的图片，请你耐心地查看并给予回应。"
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
            "max_tokens": max2,
            "top_p": p,
            "top_k": k,
            "temperature": tem,
            "stream": False,
        }

        response = requests.post(url="http://0.0.0.0:23333/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']