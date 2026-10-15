 
import hashlib
import chromadb
import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_K
)
 
client=chromadb.PersistentClient(path=str(CHROMA_DIR))
collection=client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space":"cosine"}
)
 
splitter=RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    add_start_index=True
)
 
def embed_texts(texts):
    response=ollama.embed(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return response["embeddings"]
 
def make_chunks(documents):
    chunks=[]
    for document in documents:
        pieces=splitter.create_documents(
            texts=[document["text"]],
            metadatas=[document["metadata"]]
        )
        for index,piece in enumerate(pieces):
            metadata=dict(piece.metadata)
            metadata["chunk_index"]=index
            metadata["start_index"]=int(
                metadata.get("start_index",0)
            )
            chunks.append({
                "text":piece.page_content,
                "metadata":metadata
            })
    return chunks
 
def index_documents(documents):
    chunks=make_chunks(documents)
    if not chunks:
        return 0
 
    batch_size=16
    total=0
 
    for start in range(0,len(chunks),batch_size):
        batch=chunks[start:start+batch_size]
        texts=[item["text"] for item in batch]
        embeddings=embed_texts(texts)
        ids=[]
        metadatas=[]
 
        for item in batch:
            identity=(
                str(item["metadata"].get("source",""))
                +str(item["metadata"].get("page",""))
                +str(item["metadata"]["chunk_index"])
                +item["text"]
            )
            ids.append(
                hashlib.sha256(identity.encode("utf-8")).hexdigest()
            )
            metadatas.append(item["metadata"])
 
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        total+=len(batch)
 
    return total
 
def search_documents(query,k=RETRIEVAL_K):
    if collection.count()==0:
        return []
 
    query_embedding=embed_texts([query])[0]
    result=collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k,collection.count()),
        include=["documents","metadatas","distances"]
    )
 
    matches=[]
    for index,text in enumerate(result["documents"][0]):
        matches.append({
            "text":text,
            "metadata":result["metadatas"][0][index],
            "distance":result["distances"][0][index]
        })
    return matches
 