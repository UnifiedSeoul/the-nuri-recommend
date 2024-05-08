# 설치
# pip install xmltodict
# pip install transformers
# pip install --ignore-installed sentence-transformers==2.7.0
# pip install tf-keras

import pymysql
import lxml
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import math
import xmltodict, json
from datetime import datetime
from pytz import timezone
import pickle
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os
from collections import OrderedDict


def getJobList():
    host = 'thenuridatabase.cdagciaaigw0.ap-northeast-2.rds.amazonaws.com'
    port = 3306
    user = 'admin'
    password = 'nuri1234'
    database = 'thenuri'

    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8"
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM thenuri.job_info")

    result = cursor.fetchall()
    jobData = pd.DataFrame(result)
    connection.close()
    return jobData

# 임시 공고 전처리
def extractZipCode(text):
    zipCode = text.split()
    return zipCode[0]

def embeddingJobList(jobs):
    print('\nstart embeddingJobList...\n')
    # # 서울 공고 추출을 위한 우편 번호 추가 (01000~01200)
    # jobs['zip_code'] = jobs['place_detail_address'].apply(extract_zipCode)
    
    # # 오늘 날짜 이전의 마감 공고 제거
    # today = datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d')

    # seoul_jobs = jobs.loc[(jobs['zip_code'].str.startswith('0')) & (jobs['to_acceptance_date'] >= today)]
    # seoul_jobs.reset_index(drop=True, inplace=True)

    # 공고 제목을 영어로 번역
    recruitment_title = list(jobs['recruitment_title'])
    pipe_trans = pipeline("translation", model="circulus/kobart-trans-ko-en-v2", max_length=200)
    
    print('\n...translating...\n')
    translated_title_pipe = pipe_trans(recruitment_title)

    translated_title = [title['translation_text'] for title in translated_title_pipe if 'translation_text' in title]

    # 공고 제목 토큰화 및 벡터화
    MODEL_ID = 'sentence-transformers/all-MiniLM-L6-v2'
    model = SentenceTransformer(MODEL_ID)
    
    print('\n...encoding...\n')
    title_embeddings = model.encode(translated_title)

    # 로컬에 저장
    print('\n...saving...\n')
    file_dir = os.path.dirname(__file__)
    title_embedding_pos = os.path.join(file_dir, 'data', 'TitleEmbedding.npy')
    np.save(title_embedding_pos, title_embeddings)
    
    jobs_pos = os.path.join(file_dir, 'data', 'Jobs.csv')
    jobs.to_csv(jobs_pos, index=None)

    embedding_model_pos = os.path.join(file_dir, 'model', 'EmbeddingModel.pkl')
    with open(embedding_model_pos, 'wb') as f:
        pickle.dump(model, f)

    translation_model_pos = os.path.join(file_dir, 'model', 'TranslationModel.pkl')
    with open(translation_model_pos, 'wb') as f:
        pickle.dump(pipe_trans, f)

def getRecommendation(user_info):
    # 추천 시작
    # 입력 받은 유저 정보 토큰화 및 벡터화
    
    file_dir = os.path.dirname(__file__)
    title_embedding_pos = os.path.join(file_dir, 'data', 'TitleEmbedding.npy')
    TitleEmbedding = np.load(title_embedding_pos)
    
    # jobs_pos = os.path.join(file_dir, 'data', 'Jobs.csv')
    # Jobs = pd.read_csv(jobs_pos)

    embedding_model_pos = os.path.join(file_dir, 'model', 'EmbeddingModel.pkl')
    with open(embedding_model_pos, 'rb') as f:
        EmbeddingModel = pickle.load(f)
        
    translation_model_pos = os.path.join(file_dir, 'model', 'TranslationModel.pkl')
    with open(translation_model_pos, 'rb') as f:
        TranslationModel = pickle.load(f)
    
    trans_input = TranslationModel(user_info)
    encode_input = trans_input[0]['translation_text']
    embedding_input = EmbeddingModel.encode(encode_input)

    # 코사인 유사도 측정
    cos_sim = []
    for i, emb in enumerate(TitleEmbedding):
        cos_sim.append((i, util.cos_sim(embedding_input, emb)[0].item()))

    cos_sim = sorted(cos_sim, key=lambda x:-x[1])
    cos_sim = [x for x in cos_sim if x[1] >= 0]
    # top_1 = cos_sim[0][0]

    # job_id_list = Jobs['job_id'].to_list()
    # print(Jobs.loc[Jobs.index==top_1, ['company_name', 'recruitment_title']])
    return cos_sim[:30]

def recommendation(data):
    results = []
    for d in data:
        print(d)
        input_recommend = d['jobPlace'] + " " + d['jobSpecific']
        rec_arr = getRecommendation(input_recommend)
        results += rec_arr
    
    results = sorted(results, key=lambda x:-x[1])
    # print(results)
    results = [x[0] for x in results]
    results = list(OrderedDict.fromkeys(x for x in results))
    
    
    file_dir = os.path.dirname(__file__)
    jobs_pos = os.path.join(file_dir, 'data', 'Jobs.csv')
    Jobs = pd.read_csv(jobs_pos)
    job_id_list = Jobs['job_id'].to_list()
    
    ret = [job_id_list[x] for x in results]
    print(ret)
    return ret