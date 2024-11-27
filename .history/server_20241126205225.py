from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gpt_researcher import GPTResearcher
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Gradio app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORT_TYPE = "research_report"

@app.post("/research")
async def research(query: str):
    researcher = GPTResearcher(query=query, report_type=REPORT_TYPE)
    report = await researcher.conduct_research()
    return {"report": report}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)