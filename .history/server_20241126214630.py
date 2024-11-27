from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gpt_researcher import GPTResearcher
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
load_dotenv()

class QueryRequest(BaseModel):
    query: str

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORT_TYPE = "research_report"

@app.post("/research")
async def research(request: QueryRequest):
    researcher = GPTResearcher(query=request.query, report_type=REPORT_TYPE)
    report = await researcher.conduct_research()
    return {"report": report}

from gpt_researcher import GPTResearcher
import nest_asyncio

nest_asyncio.apply()

QUERY = "What are the best ways to use a loss functions when fine tuning an LLM model?"
REPORT_TYPE = "research_report"
async def main():
    researcher = GPTResearcher(query=QUERY, report_type=REPORT_TYPE)
    report = await researcher.conduct_research()
    return report


if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    # report = asyncio.run(main())
    print(report)
