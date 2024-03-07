from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from pinecone import Pinecone, ServerlessSpec
from tqdm.notebook import tqdm
import langchain
import openai
from openai import OpenAI
import string
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader, OnlinePDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import string
from tqdm.notebook import tqdm
from pinecone import Pinecone, ServerlessSpec
import argparse
from util import scd_utils

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
parser.add_argument('--file_path', type=str, default='',
                    help='the data path of file to be converted to vector embbedings')
parser.add_argument('--genre', type=str, default='',
                    help='the genre of file to be converted to vector embbedings')
parser.add_argument('--index_name', type=str, default='',
                    help='the data path of file to be converted to vector embbedings')
parser.add_argument('--namespace', type=str, default='',
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

index_name = 'scd001' #args.index_name
namespace = 'ns001' #args.namespace
genre = 'scd' #args.genre

doc_type = file_path.split('.')[-1]

if doc_type == scd_utils.DocumentType.pdf.name:
    loader = UnstructuredPDFLoader(file_path)
    text = loader.load()
    text_page_content = text[0].page_content

if doc_type == scd_utils.DocumentType.txt.name:
    loader = TextLoader(file_path)
    text = loader.load()
    text_page_content = text[0].page_content

print(doc_typye)

# Explicitly convert text to string
text_page_content_str = str(text_page_content)

# Create a RecursiveCharacterTextSplitter instance
splitter = RecursiveCharacterTextSplitter(separators=['\n\n', '\n', '.', ','],
        chunk_size=750,
        chunk_overlap=50)

# Use the splitter's method to split text into chunks
text_chunks = splitter.split_text(text_page_content_str)

# Convert the list of texts into a DataFrame
df = pd.DataFrame(text_chunks, columns=['text'])
# print(df.head())

# Function to remove punctuation and new lines
# Move the func to utils.py
def preprocess_text(text):
    text = text.replace('\n', ' ')
    text = text.translate(str.maketrans('', '', string.punctuation))
    # print(text)
    return text

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
        
        embedding = get_embedding(text)
        index.upsert(
        vectors=[
            {
                "id": f"{filename}{i}",
                "values": embedding,
                "metadata": {"genre": genre,"text": text}
            }
        ],
        namespace= namespace
        )
        # print(text)
        # print(embedding)


# Convert the list of texts into a DataFrame
df = pd.DataFrame(text_chunks, columns=['text'])
# Apply preprocessing
df['text_preprocessed'] = df['text'].apply(preprocess_text)
upsert_vector_embeddings_to_pinecone(df['text_preprocessed'],genre,file_name)
print("upsert_vector_embeddings_to_pinecone successful")
# To update vales in pinecone db
# for i,text in enumerate(tqdm(df['text_preprocessed'])):
#     index.update(id=f"vec{i}", set_metadata={"text": text},namespace="ns1")