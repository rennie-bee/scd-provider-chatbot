import os
import pandas as pd
import logging
import string
from io import BytesIO
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.cleaners.core import clean_extra_whitespace
import openai

class EmbeddingProcessor:
    def __init__(self, file_stream, doc_type, api_key, openai_key, index_name):
        self.file_stream = file_stream
        self.doc_type = doc_type
        self.loader = None
        self.concat_text = {}
        self.api_key = api_key
        self.openai_key = openai_key
        self.index_name = index_name
        self.namespace = 'ns001'
        self.genre = 'scd'
        self._setup_clients()

    def _setup_clients(self):
        self.pc = Pinecone(api_key=self.api_key)
        self.client = openai.OpenAI(api_key=self.openai_key)

    def load_and_process_file(self):
        if self.doc_type == 'pdf':
            self.file_stream.seek(0)  # Ensure the stream is at the start
            self.loader = UnstructuredPDFLoader(BytesIO(self.file_stream.read()), mode="elements", post_processors=[clean_extra_whitespace])
        elif self.doc_type == 'txt':
            self.file_stream.seek(0)
            content = self.file_stream.read().decode('utf-8')
            self.loader = TextLoader(BytesIO(content.encode('utf-8')))

        docs = self.loader.load()
        for doc in docs:
            pg_no = doc.metadata.get("page_number", 0)  # Default to page 0 if not available
            if pg_no in self.concat_text:
                self.concat_text[pg_no] += doc.page_content
            else:
                self.concat_text[pg_no] = doc.page_content

    def preprocess_text(self, text):
        text = text.replace('\n', ' ')
        return text.translate(str.maketrans('', '', string.punctuation))

    def generate_embeddings(self):
        text_chunks = []
        pg_no_arr = []
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(model_name="gpt-3.5-turbo", chunk_size=750, chunk_overlap=50)
        for key in self.concat_text.keys():
            text_page_content_str = str(self.concat_text[key])
            text_chunks += splitter.split_text(text_page_content_str)
            pg_no_arr += [key] * (len(text_chunks) - len(pg_no_arr))
        df = pd.DataFrame(zip(text_chunks, pg_no_arr), columns=['text', 'pg_no'])
        df['text_preprocessed'] = df['text'].apply(self.preprocess_text)
        self.upsert_vector_embeddings_to_pinecone(df)

    def upsert_vector_embeddings_to_pinecone(self, df):
        index = self.pc.Index(name=self.index_name)
        for i, text in enumerate(df['text_preprocessed']):
            pg_no = df.at[i, 'pg_no']
            embedding = self.get_embedding(text)
            index.upsert(
                vectors=[{
                    "id": f"doc{i}",
                    "values": embedding,
                    "metadata": {"genre": self.genre, "text": text, "pg_no": pg_no}
                }],
                namespace=self.namespace
            )

    def get_embedding(self, text):
        embedding = self.client.embeddings.create(input=[text], model="text-embedding-ada-002")
        return embedding.data[0].embedding

    def process(self):
        self.load_and_process_file()
        self.generate_embeddings()
        logging.info("Embedding processing and upserting to Pinecone completed successfully.")

