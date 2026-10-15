import argparse
 
from config import DOCUMENTS_DIR
from app.ingestion.loaders import load_file, load_webpage
from app.retrieval.store import index_documents
from app.graph.workflow import run_agent
 
 
def ingest_documents():
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
 
    documents = []
 
    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
        ".html",
        ".htm"
    }
 
    for path in DOCUMENTS_DIR.rglob("*"):
        if not path.is_file():
            continue
 
        if path.suffix.lower() not in supported_extensions:
            continue
 
        print(f"Loading: {path.name}")
 
        try:
            loaded = load_file(str(path))
            documents.extend(loaded)
        except Exception as error:
            print(f"Could not load {path.name}: {error}")
 
    if not documents:
        print("No readable documents found.")
        return
 
    total = index_documents(documents)
    print(f"Indexed {total} chunks.")
 
 
def ingest_url(url):
    try:
        documents = load_webpage(url)
        total = index_documents(documents)
        print(f"Indexed {total} chunks from {url}")
    except Exception as error:
        print(f"Could not ingest URL: {error}")
 
 
def ask_question(question):
    result = run_agent(question)
 
    print("\nANSWER")
    print(result.get("answer", "No answer generated."))
 
    print("\nSOURCES")
 
    sources = result.get("sources", [])
 
    if not sources:
        print("No sources available.")
    else:
        for source in sources:
            print(f"[{source['label']}] {source['source']}")
 
    print("\nDEBUG")
    print(f"Search query: {result.get('search_query', '')}")
    print(f"Retrieval attempts: {result.get('retrieval_attempts', 0)}")
    print(f"Evidence grade: {result.get('evidence_grade', 'unknown')}")
    print(f"Web results: {len(result.get('web_results', []))}")
 
 
def main():
    parser = argparse.ArgumentParser(
        description="Agentic RAG Assistant"
    )
 
    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )
 
    subparsers.add_parser("ingest")
 
    url_parser = subparsers.add_parser("add-url")
    url_parser.add_argument("url")
 
    ask_parser = subparsers.add_parser("ask")
    ask_parser.add_argument(
        "question",
        nargs="+"
    )
 
    args = parser.parse_args()
 
    if args.command == "ingest":
        ingest_documents()
 
    elif args.command == "add-url":
        ingest_url(args.url)
 
    elif args.command == "ask":
        ask_question(" ".join(args.question))
 
 
if __name__ == "__main__":
    main()