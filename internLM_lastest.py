import requests
import json

url = 'https://internlm-chat.intern-ai.org.cn/puyu/api/v1/chat/completions'
header = {
    'Content-Type':
        'application/json',
    "Authorization":
        "Bearer eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI0MDA3MzgyOCIsInJvbCI6IlJPTEVfUkVHSVNURVIiLC"
        "Jpc3MiOiJPcGVuWExhYiIsImlhdCI6MTcxODEwNTUwNCwiY2xpZW50SWQiOiJlYm1ydm9kNnlvMG5semFlazF5cCIsInBob25lI"
        "joiMTgwNjE0Mjg4MDEiLCJ1dWlkIjoiZWM1ODY0NWMtZWQ4NS00MjFkLWFiYTktYzVmN2EzOGI5NjVmIiwiZW1haWwiOiJiaWdf"
        "d2hpdGVfZm94QHFxLmNvbSIsImV4cCI6MTczMzY1NzUwNH0.8ddtMAsEvDMvhYeJHOTe2Zki8KdYZyI-yoMvTwbgBAeMWCSXv78"
        "Kc-zQ87W_PPBbSzdWvBrX0MGpB2ZDpt06Tw"
}


def fox_find_chat(query, results):
    data = {
        "model": "internlm2-latest",
        "messages": [
            {
                "role": "user",
                "text": query +
                        "你是一名专业的学术研究助手，你的任务是帮助用户寻找相关论文。"
                        "你将会接收到一系列从向量数据库中检索出的论文信息，"
                        "每条信息都包含以下字段：'Title', 'Authors', 'Abstract', 'DOI'。"
                        "这些论文信息是基于用户查询自动检索得到的，并且已经按照相关性排序。"
                        + str(results) +
                        "你的任务是根据这些论文信息，选取内容合适的部分回答用户问题，请不要全选，也不要只选取一两个。"
                        "语言应该适合学术交流，清晰、准确、客观。"
                        "对每篇论文的推荐和解说，应当包含个人的见解和点评，而不是罗列其内容。"

            }
        ],
        "temperature": 0.8,
        "top_p": 0.9
    }

    res = requests.post(url, headers=header, data=json.dumps(data))
    print(res.status_code)
    print(res.json())
    print(res.json()["choices"][0]["message"]["content"])
    return res.json()["choices"][0]["message"]["content"]


def fox_write(query, results):
    data = {
        "model": "internlm2-latest",
        "messages": [
            {
                "role": "user",
                "text": query +
                        "你是一名专业的学术研究助手，你的任务是帮助用户撰写基于相关学术论文的综述。"
                        "你将会接收到一系列从向量数据库中检索出的论文信息，"
                        "每条信息都包含但不限于以下字段：'Title', 'Authors', 'Abstract', 'DOI'。"
                        "这些论文信息是基于用户查询自动检索得到的，并且已经按照相关性排序。"
                        + str(results) +
                        "你的任务是根据这些论文信息，撰写一篇全面、准确且连贯的综述，涵盖关键发现、研究主题、趋势以及任何其他相关的重要信息。"
                        "综述应该是对所提供论文的精华总结，同时也要确保信息的准确性和完整性。"
                        "请遵循以下步骤来撰写综述："
                        "1. 仔细阅读并理解每篇论文的标题、作者、摘要、DOI和出版年份。"
                        "2. 分析论文之间的联系和差异，识别核心主题和研究趋势。"
                        "3. 撰写综述，确保综述的结构清晰，内容有逻辑性，语言流畅。"
                        "4. 在综述中引用具体的研究成果时，请注明作者和出版年份，以增加综述的权威性。"
                        "5. 如果有额外的见解或分析，可以在综述中适当提出，但要确保这些内容是基于所提供论文信息的合理推断。"
                        "综述要求："
                        "- 综述应该是对学术论文的综合总结，而不是单纯的论文列表。"
                        "- 综述应该包含对研究领域的深入分析和对未来研究方向的展望。"
                        "- 综述应该是有机结合多篇论文信息的产物，而不是孤立地介绍每篇论文。"
                        "- 综述的语言应该适合学术交流，清晰、准确、客观。"
            }
        ],
        "temperature": 0.8,
        "top_p": 0.9
    }

    res = requests.post(url, headers=header, data=json.dumps(data))
    print(res.status_code)
    print(res.json())
    print(res.json()["choices"][0]["message"]["content"])
    return res.json()["choices"][0]["message"]["content"]