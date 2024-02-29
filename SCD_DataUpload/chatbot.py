from langchain.document_loaders import TextLoader
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

loader = TextLoader("./SCD Docs/SCD-Tej.txt")
data = loader.load()

# us_loader = UnstructuredURLLoader(urls=["https://www.cdc.gov/ncbddd/sicklecell/healthyliving-prevent-infection.html","https://www.cdc.gov/ncbddd/sicklecell/betterhealthtoolkit/caring-for-common-complications.html"])
# us_data = us_loader.load()
# print(len(us_data))

splitter1 = CharacterTextSplitter(separator='\n',
                                    chunk_size= 200,
                                    chunk_overlap = 0)
splitter2 = RecursiveCharacterTextSplitter(separators=['\n\n','\n','.',' '],
                                    chunk_size= 200,
                                    chunk_overlap = 0)

chunks = splitter2.split_text(data[0].page_content)
len(chunks)
# print(len(chunks))

# Getting embeddings for chunks
encoder = SentenceTransformer("all-mpnet-base-v2")
vectors = encoder.encode(chunks[:6])
dim = vectors.shape[1]
# print(dim)

# Store embeddings for chunks in Vector DB
index_scd = faiss.IndexFlatL2(dim)
index_scd.add(vectors)

# Vector embeddings for search_query
search_query = "what is sickle cell?"
search_vec = encoder.encode(search_query)
search_vec = np.arrary(search_vec).reshape(1,-1)

distances,I = index_scd.search(search_vec, k=10)



