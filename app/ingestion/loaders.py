from pathlib import Path
from urllib.parse import urlparse
import requests
import fitz
from docx import Document
from bs4 import BeautifulSoup
 
SUPPORTED_EXTENSIONS={".pdf",".docx",".txt",".md",".html",".htm"}
 
def load_pdf(path):
    results=[]
    with fitz.open(path) as pdf:
        for page_number,page in enumerate(pdf,start=1):
            text=page.get_text("text").strip()
            if text:
                results.append({
                    "text":text,
                    "metadata":{
                        "source":str(path),
                        "page":page_number,
                        "source_type":"pdf"
                    }
                })
    return results
 
def load_docx(path):
    document=Document(path)
    paragraphs=[p.text.strip() for p in document.paragraphs if p.text.strip()]
    text="\n".join(paragraphs)
    if not text:
        return []
    return [{
        "text":text,
        "metadata":{
            "source":str(path),
            "source_type":"docx"
        }
    }]
 
def load_text(path):
    text=path.read_text(encoding="utf-8",errors="replace").strip()
    if not text:
        return []
    return [{
        "text":text,
        "metadata":{
            "source":str(path),
            "source_type":path.suffix.lower().lstrip(".")
        }
    }]
 
def load_html(path):
    html=path.read_text(encoding="utf-8",errors="replace")
    soup=BeautifulSoup(html,"html.parser")
    for element in soup(["script","style","nav","footer"]):
        element.decompose()
    text=soup.get_text(separator="\n",strip=True)
    if not text:
        return []
    return [{
        "text":text,
        "metadata":{
            "source":str(path),
            "source_type":"html"
        }
    }]
 
def load_file(file_path):
    path=Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    extension=path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")
    if extension==".pdf":
        return load_pdf(path)
    if extension==".docx":
        return load_docx(path)
    if extension in {".html",".htm"}:
        return load_html(path)
    return load_text(path)
 
def load_webpage(url):
    parsed=urlparse(url)
    if parsed.scheme not in {"http","https"} or not parsed.hostname:
        raise ValueError("Provide a valid HTTP or HTTPS URL.")
    response=requests.get(
        url,
        headers={"User-Agent":"AgenticRAGAssistant/1.0"},
        timeout=20
    )
    response.raise_for_status()
    soup=BeautifulSoup(response.text,"html.parser")
    for element in soup(["script","style","nav","footer"]):
        element.decompose()
    title=soup.title.get_text(strip=True) if soup.title else url
    text=soup.get_text(separator="\n",strip=True)
    if not text:
        raise ValueError("No readable text found on the webpage.")
    return [{
        "text":text,
        "metadata":{
            "source":url,
            "title":title,
            "source_type":"web"
        }
    }]