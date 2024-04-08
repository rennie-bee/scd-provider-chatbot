from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from pinecone import Pinecone, ServerlessSpec
from tqdm.notebook import tqdm
import langchain
import openai
from openai import OpenAI
import string
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader, OnlinePDFLoader
# from unstructured.documents.elements import Element
from unstructured.cleaners.core import clean_extra_whitespace
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
from tqdm.notebook import tqdm
from pinecone import Pinecone, ServerlessSpec
import argparse
from util import scd_utils
import nltk
import numpy
# nltk.download('punkt')
# import boto3

# # Initialize the S3 client
# s3 = boto3.client('s3')

# # Specify the bucket name and file key
# bucket_name = 'your_bucket_name'
# file_key = 'your_file_key'

# # Read the file from S3
# try:
#     response = s3.get_object(Bucket=bucket_name, Key=file_key)
#     file_content = response['Body'].read().decode('utf-8')
#     # Process the file content as needed
#     print(file_content)
# except Exception as e:
#     print(f"Error reading file from S3: {e}")

# Your Pinecone API key
api_key = "bd8f871a-819e-42c8-a6ac-81c14948fefd"
#openai API Keys
openai_key = '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'

parser = argparse.ArgumentParser(description='SCD')
parser.add_argument('--file_path', type=str, default='/Users/stlp/Desktop/scd-provider-chatbot/sample-files/sickle-cell-disease-report NIH.pdf',
                    help='the data path of file to be converted to vector embbedings')
parser.add_argument('--genre', type=str, default='scd',
                    help='the genre of file to be converted to vector embbedings')
parser.add_argument('--index_name', type=str, default='scd001',
                    help='the data path of file to be converted to vector embbedings')
parser.add_argument('--namespace', type=str, default='ns001',
                    help='the data path of file to be converted to vector embbedings')

# Initialize Pinecone and openai client
pc = Pinecone(api_key=api_key)
client = openai.OpenAI(api_key=openai_key)

args = parser.parse_args()

file_path = args.file_path
try:
    file_name = file_path.split('/')[-1]
except Exception as e:
    print("An error occurred:", e)

index_name = args.index_name
namespace = args.namespace
genre = args.genre

doc_type = file_path.split('.')[-1]

if doc_type == scd_utils.DocumentType.pdf.name:
    loader = UnstructuredPDFLoader(file_path, mode="elements" , post_processors=[clean_extra_whitespace],
)

docs = loader.load()
# print(docs)
# print(len(docs))
concat_text = {}
for text in docs:
    pg_no = text.metadata["page_number"]
    if pg_no in concat_text:
        concat_text[pg_no] += text.page_content
    else:
        concat_text[pg_no] = text.page_content

    # print(concat_text.keys().sort())

if doc_type == scd_utils.DocumentType.txt.name:
    loader = TextLoader(file_path)
    text = loader.load()
    text_page_content = text[0].page_content

# Create a RecursiveCharacterTextSplitter instance
splitter = RecursiveCharacterTextSplitter(separators=['\n\n', '\n', '.', ','],
        chunk_size=750,
        chunk_overlap=50)

splitter2 = RecursiveCharacterTextSplitter.from_tiktoken_encoder(model_name="gpt-3.5-turbo",
    chunk_size=750,
    chunk_overlap=50,
)

# Function to remove punctuation and new lines
# Move the func to utils.py
def preprocess_text(text):
    text = text.replace('\n', ' ')
    text = text.translate(str.maketrans('', '', string.punctuation))
    # print(text)
    return text

# print(doc_typye)
text_chunks = []
pg_no_arr = []

for key in concat_text.keys():
    text_per_pg = concat_text[key]
    # Explicitly convert text to string
    text_page_content_str = str(text_per_pg)
    # text_page_content_str = preprocess_text(text_page_content_str)
    # Use the splitter's method to split text into chunks
    text_chunks += splitter2.split_text(text_page_content_str)
    pg_no_arr += [key] * (len(text_chunks)-len(pg_no_arr))

# Convert the list of texts into a DataFrame
df = pd.DataFrame(zip(text_chunks,pg_no_arr), columns=['text','pg_no'])
# print(df.head())
# print(dfhead)


# Function to get the embeddings of the text using OpenAI text-embedding-ada-002 model
def get_embedding(text, model="text-embedding-ada-002"):
#    text = text.replace("\n", " ")
   embedding = client.embeddings.create(input=[text], model=model)
   return embedding.data[0].embedding
   
# Assuming df is your DataFrame and 'text_preprocessed' is the column with preprocessed texts
# Note: This operation might take some time depending on the number of texts due to API response times
# df['embedding'] = df['text_preprocessed'].apply(get_embedding)
# df['embedding'] = [get_embedding(text) for text in tqdm(df['text_preprocessed'])]
index = pc.Index(name=index_name)

def upsert_vector_embeddings_to_pinecone(text_embeddings, genre, filename):
    for i,text in enumerate(df['text_preprocessed']):
        pg_no = df.at[i,'pg_no']
        embedding = get_embedding(text)
        index.upsert(
        vectors=[
            {
                "id": f"{filename}{i}",
                "values": embedding,
                "metadata": {"genre": genre,"text": text,"pg_no":pg_no}
            }
        ],
        namespace= namespace
        )
        # print(text)
        # print(embedding)


# Apply preprocessing
df['text_preprocessed'] = df['text'].apply(preprocess_text)
# print(df.head())
# print(heda)
upsert_vector_embeddings_to_pinecone(df['text_preprocessed'],genre,file_name)
print("upsert_vector_embeddings_to_pinecone successful")
# To update vales in pinecone db
# for i,text in enumerate(tqdm(df['text_preprocessed'])):
#     index.update(id=f"vec{i}", set_metadata={"text": text},namespace="ns1")