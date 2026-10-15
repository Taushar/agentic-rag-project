from dotenv import load_dotenv
from pathlib import Path
from langchain_tavily import TavilySearch
 
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
 
try:
    search = TavilySearch(max_results=3)
    result = search.invoke({"query": "Python LangGraph documentation"})
 
    print("Result type:", type(result).__name__)
    print("Result:", result)
 
except Exception as error:
    print("Error type:", type(error).__name__)
    print("Error:", str(error))