from dotenv import load_dotenv

load_dotenv()

from backend.server.server import app

import asyncio
from gpt_researcher import GPTResearcher
import nest_asyncio

nest_asyncio.apply()

QUERY = "What are the best ways to use a loss functions when fine tuning an LLM model?"
REPORT_TYPE = "research_report"
async def main():
    researcher = GPTResearcher(query=QUERY, report_type=REPORT_TYPE)
    report = await researcher.conduct_research()
    return report

report = asyncio.run(main())
print(report)



if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=8000)
    
