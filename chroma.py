import pandas as pd
from BCEmbedding import EmbeddingModel
import chromadb
from internLM_lastest import fox_write, fox_find_chat


def BCE_embedding(vectorization_data):
    # list of sentences
    token = "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"
    # init embedding model
    model = EmbeddingModel(model_name_or_path="maidalun1020/bce-embedding-base_v1", use_auth_token=token)

    # extract embeddings
    embeddings = model.encode(vectorization_data)
    return embeddings


def chroma_data(fsm):
    if fsm == 1:
        # CSV 文件的路径
        csv_file_path = 'relevance_data.csv'
    elif fsm == 2:
        # CSV 文件的路径
        csv_file_path = 'reference_data.csv'
    elif fsm == 3:
        # CSV 文件的路径
        csv_file_path = 'consensus_data.csv'

    # 读取 CSV 文件
    df = pd.read_csv(csv_file_path, encoding='utf-8-sig')

    # 获取列名列表
    column_names = df.columns.tolist()

    # 打印列名列表
    print(column_names)

    if fsm == 1:
        df.drop(['Unnamed: 0', 'Paper_url', 'Keywords'], axis=1, inplace=True)
    elif fsm == 2:
        df.drop(['Unnamed: 0', 'Paper_url', 'Keywords'], axis=1, inplace=True)
    elif fsm == 3:
        df.drop(['Unnamed: 0', 'Citation_count', 'URL'], axis=1, inplace=True)

    # 获取列名列表
    column_names = df.columns.tolist()

    # 打印列名列表
    print(column_names)

    # 或者，如果您想要每行数据作为一个单独的列表
    lists_of_rows = [[f"{column_names[i]}: {value}"
                      for i, value in enumerate(row)] for row in zip(*[df[col] for col in column_names])]

    # 将二维列表中的每个子列表转换成一个字符串
    one_dimensional_list = [' '.join(map(str, sublist)) for sublist in lists_of_rows]

    # 使用默认配置初始化数据库
    client = chromadb.PersistentClient(path="D:\Project_for_Python\Data")  # 数据保存在磁盘
    # 创建一个名为 "my_dataset" 的数据集
    dataset = client.get_or_create_collection(name="my_dataset")

    sentences = one_dimensional_list
    embeddings = BCE_embedding(sentences)
    # 自动生成ID

    # ids = [f"id{i + 1}" for i in range(len(sentences))]

    # 自动生成ID并创建统一的元数据
    if fsm == 1:
        ids = [f"relevance{i + 1}" for i in range(len(sentences))]
        metadatas = [{"source": "relevance"} for _ in sentences]
    elif fsm == 2:
        ids = [f"reference{i + 1}" for i in range(len(sentences))]
        metadatas = [{"source": "reference"} for _ in sentences]
    elif fsm == 3:
        ids = [f"consensus{i + 1}" for i in range(len(sentences))]
        metadatas = [{"source": "consensus"} for _ in sentences]

    dataset.upsert(
        documents=sentences,
        embeddings=embeddings,
        metadatas=metadatas,  # 重复元数据列表，以匹配句子数量
        ids=ids
    )


def chroma_file_data(file_list: list):
    # client = chromadb.Client()
    client = chromadb.PersistentClient(path="D:\Project_for_Python\Data")  # 数据保存在磁盘
    # 创建一个名为 "my_dataset" 的数据集
    dataset = client.get_or_create_collection(name="my_dataset")

    sentences = file_list
    embeddings = BCE_embedding(sentences)

    # 自动生成ID并创建统一的元数据
    ids = [f"user{i + 1}" for i in range(len(sentences))]
    metadatas = [{"source": "user"} for _ in sentences]

    dataset.upsert(
        documents=sentences,
        embeddings=embeddings,
        metadatas=metadatas,  # 重复元数据列表，以匹配句子数量
        ids=ids
    )


def chroma_query(query: str):
    client = chromadb.PersistentClient(path="D:\Project_for_Python\Data")  # 数据保存在磁盘
    dataset = client.get_collection(name="my_dataset")
    # dataset = client.get_or_create_collection(name="my_dataset")
    # 使用一个向量进行相似度查询
    query_embedding = BCE_embedding(query)
    results = dataset.query(query_embeddings=query_embedding, n_results=5)
    return fox_find_chat(query, results['documents'])


def chroma_query_write(query: str):
    client = chromadb.PersistentClient(path="D:\Project_for_Python\Data")  # 数据保存在磁盘
    dataset = client.get_collection(name="my_dataset")
    # dataset = client.get_or_create_collection(name="my_dataset")
    # 使用一个向量进行相似度查询
    query_embedding = BCE_embedding(query)
    results = dataset.query(query_embeddings=query_embedding, n_results=15)

    return fox_write(query, results['documents'])
