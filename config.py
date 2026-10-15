from pathlib import Path
 
BASE_DIR=Path(__file__).resolve().parent
DOCUMENTS_DIR=BASE_DIR/"data"/"documents"
CHROMA_DIR=BASE_DIR/"data"/"chroma"
 
LLM_MODEL="qwen2.5:7b"
EMBEDDING_MODEL="nomic-embed-text"
COLLECTION_NAME="knowledge_base"
 
CHUNK_SIZE=900
CHUNK_OVERLAP=150
RETRIEVAL_K=4