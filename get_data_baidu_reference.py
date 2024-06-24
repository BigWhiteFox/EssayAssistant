from urllib.parse import urlencode, quote
import requests
from bs4 import BeautifulSoup
import pandas as pd
import gradio as gr
from internVL_find import summary_paper


def translate(text):
    # 查询参数字典
    params = {'wd': f'{text}'}

    # 对查询参数进行百分号编码
    encoded_params = urlencode(params, quote_via=quote)

    return (f'https://xueshu.baidu.com/s?{encoded_params}&pn={0}&tn=SE_baiduxueshu_c1gjeupa&'
            f'ie=utf-8&sort=sc_cited&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&sc_hit=1')


def extract_data_reference(n, text):
    href_list = []
    for page in range(n):
        url = translate(f'{text}')
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        post_list = soup.find_all('h3', class_='t c_font')

        # 检查当前页是否有数据
        if not post_list:
            break

        # 提取所有<a>标签的href属性
        for h3_tag in post_list:
            a_tags = h3_tag.find_all('a')
            for a_tag in a_tags:
                href = a_tag.get('href')
                href_list.append(href)

        # 准备下一页的URL
        next_page_url = url.replace(f'pn={page * 10}', f'pn={(page + 1) * 10}')

    return href_list


def scrape_publications_reference(href_list):
    # 初始化DataFrame
    df = pd.DataFrame(columns=['Title', 'URL', 'Authors', 'Abstract', 'Keywords', 'DOI', 'Reference', 'Year'])

    # 遍历href_list中的每个URL
    for i, href in enumerate(href_list):
        r2 = requests.get(href)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        post_list2 = soup2.find_all('div', class_='main-info')

        # 提取标题
        title = post_list2[0].h3.a.text.strip() \
                if post_list2[0].h3.a else "暂无"

        # 提取作者
        authors = [author.text.strip() for author in post_list2[0].find('div', class_='author_wr').find_all('a')] \
                  if post_list2[0].find('div', class_='author_wr') else []

        # 提取摘要
        abstract = post_list2[0].find('p', class_='abstract').text.strip() \
                   if post_list2[0].find('p', class_='abstract') else "暂无"

        # 提取年份
        year_tag = post_list2[0].find('div', class_='year_wr')
        year = year_tag.find('p', class_='kw_main').text.strip() \
               if year_tag and year_tag.find('p', class_='kw_main') else "暂无"

        # 提取关键词
        keywords = post_list2[0].find('p', class_='kw_main').text.strip() \
                   if post_list2[0].find('p', class_='kw_main') else "暂无"
        # 替换\n为空格
        keywords = keywords.replace('\n', ' ')

        # 提取DOI
        doi_tag = post_list2[0].find('div', class_='doi_wr')
        doi = doi_tag.find('p', class_='kw_main').text.strip() \
              if doi_tag and doi_tag.find('p', class_='kw_main') else "暂无"

        # 提取被引量
        reference = post_list2[0].find('div', class_='ref_wr').find('a', class_='sc_cite_cont').text.strip() \
                    if post_list2[0].find('div', class_='ref_wr') else "暂无"

        # 添加到DataFrame
        df.loc[i] = [title, href, ', '.join(authors)
                    if authors else "暂无", abstract, keywords, doi, reference, year]

    return df


# 定义一个函数来格式化输出
# 定义一个函数来格式化输出特定的列
def format_specific_columns_reference(row, columns):
    formatted_string = ""
    for col in columns:
        formatted_string += f"{col}: {row[col]}  "
    # print("大模型输入的是：\n", formatted_string)
    # print("大模型输出的是：\n", fold_paper(formatted_string.strip()))
    return summary_paper(formatted_string.strip())


def get_specific_columns_reference(data):
    llm_data = data[['Title', 'Keywords', 'Abstract']]
    # print('llm_data:\n', llm_data)
    data_list = []
    for i in range(len(llm_data)):
        formatted_string = ""
        for col in ['Title', 'Keywords', 'Abstract']:
            formatted_string += f"{col}: {llm_data.iloc[i][col]}  "
        # print("大模型输入的是：\n", formatted_string)
        # print(f"第{i}个formatted_string:\n", formatted_string)
        data_list.append(formatted_string.strip())
        # print(f"第{i}个data_list:\n", data_list)
    return data_list


def summarize_data_reference(data):
    fold_data = data[['Title', 'Keywords', 'Abstract', 'Authors', 'Year', 'DOI', 'URL', 'Reference']]
    abstract = []
    for i in range(len(fold_data)):
        abstract.append(format_specific_columns_reference(fold_data.iloc[i], ['Title', 'Abstract']))
        # 应用格式化函数并输出特定的列
        # print(f"第{i}次abstract输出:\n", abstract)

    fold_data['Abstract'] = abstract
    fold_data.rename(columns={'Abstract': 'LLM Summary'}, inplace=True)
    return fold_data

# 假设您想要提取前1页的数据
href_list_want = extract_data_reference(1, 'CNN')
# print(href_list)
row_data = scrape_publications_reference(href_list_want)
# 打印DataFrame
# print(df.shape[0])
new_data = summarize_data_reference(row_data)


