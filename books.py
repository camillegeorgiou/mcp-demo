import os
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from dotenv import load_dotenv

load_dotenv()
ES_URL = os.getenv("ES_URL")
ES_API_KEY = os.getenv("ES_API_KEY")
INDEX_NAME = "books"

KAGGLE_DATASET = "abdallahwagih/books-dataset"
DATA_DIR = "data"

os.environ["KAGGLE_CONFIG_DIR"] = os.path.join(os.getcwd(), ".kaggle")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

print(f"Downloading dataset: {KAGGLE_DATASET} to {DATA_DIR}")
exit_code = os.system(f'kaggle datasets download -d {KAGGLE_DATASET} -p {DATA_DIR} --unzip')

if exit_code != 0:
    raise RuntimeError("Kaggle download failed. Make sure kaggle CLI is configured correctly.")

csv_path = os.path.join(DATA_DIR, "data.csv")
if not os.path.exists(csv_path):
    raise FileNotFoundError("data.csv not found after unzip.")

df = pd.read_csv(csv_path)

es = Elasticsearch(ES_URL, api_key=ES_API_KEY)
if not es.ping():
    raise Exception("Failed to connect to Elasticsearch.")
print("Connected to Elasticsearch.")

if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME)
    print(f"Created index: {INDEX_NAME}")

def generate_actions(dataframe):
    for idx, row in dataframe.iterrows():
        yield {
            "_index": INDEX_NAME,
            "_id": idx,
            "_source": row.dropna().to_dict()
        }

bulk(es, generate_actions(df))
doc_count = es.count(index=INDEX_NAME)['count']
print(f"Indexed {doc_count} documents into '{INDEX_NAME}' index.")