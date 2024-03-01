from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from pinecone import Pinecone, ServerlessSpec
from tqdm.notebook import tqdm
import langchain
import openai
from openai import OpenAI
import string
from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import string
from tqdm.notebook import tqdm
from pinecone import Pinecone, ServerlessSpec

# Your Pinecone API key
api_key = "97497599-5ea9-4b33-ac6b-9f04930ad9885"
#openai API Keys
openai_key = 'sk-fGVWLsCUvDN7zsMcyHaiT3BlbkFJuIwO1ONZRbxYtcsnXBGMT'

# Initialize Pinecone and openai client
pc = Pinecone(api_key=api_key)
client = openai.OpenAI(api_key=openai_key)

file_name = '/content/machine-learning.pdf'
index_name = 'scd'
namespace = 'ns1'

loader = UnstructuredPDFLoader(file_name)
text = loader.load()

# Explicitly convert text to string
text = str(text)

# Create a RecursiveCharacterTextSplitter instance
splitter = RecursiveCharacterTextSplitter(separators=['\n\n', '\n', '.', ','],
        chunk_size=750,
        chunk_overlap=50)

# Use the splitter's method to split text into chunks
text_chunks = splitter.split_text(text)

# Convert the list of texts into a DataFrame
df = pd.DataFrame(text_chunks, columns=['text'])
# print(df.head())

# Function to remove punctuation and new lines
# Move the func to utils.py
def preprocess_text(text):
    return text.translate(str.maketrans('', '', string.punctuation)).replace('\n', ' ')

# Function to get the embeddings of the text using OpenAI text-embedding-ada-002 model
def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   embedding = client.embeddings.create(input=[text], model=model)
   return embedding.data[0].embedding
   
# Assuming df is your DataFrame and 'text_preprocessed' is the column with preprocessed texts
# Note: This operation might take some time depending on the number of texts due to API response times
# df['embedding'] = df['text_preprocessed'].apply(get_embedding)
# df['embedding'] = [get_embedding(text) for text in tqdm(df['text_preprocessed'])]

index = pc.Index(name=index_name)

def upsert_vector_embeddings_to_pinecone(text_embeddings):
    for text in tqdm(df['text_preprocessed']):
        embedding = get_embedding(text)
        index.upsert(
        vectors=[
            {
                "id": f"vec{i}",
                "values": embedding,
                "metadata": {"genre": "machine learning","text": text}
            }
        ],
        namespace= namespace
)


# Convert the list of texts into a DataFrame
df = pd.DataFrame(text_chunks, columns=['text'])
# Apply preprocessing
df['text_preprocessed'] = df['text'].apply(preprocess_text)

upsert_vector_embeddings_to_pinecone(df['text_preprocessed'])

# To update vales in pinecone db
# for i,text in enumerate(tqdm(df['text_preprocessed'])):
#     index.update(id=f"vec{i}", set_metadata={"text": text},namespace="ns1")