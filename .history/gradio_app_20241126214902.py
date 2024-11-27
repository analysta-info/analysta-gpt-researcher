import gradio as gr
from gpt_researcher import GPTResearcher
import asyncio
from 
if globals().get('run_gpt_researcher'):          
    run_gpt_researcher.close()

REPORT_TYPE = "research_report"

async def research_report(query):
    researcher = GPTResearcher(query=query, report_type=REPORT_TYPE)
    report = await researcher.conduct_research()
    return report

def run_gpt_on_query(query):
    # Create a new event loop for this thread
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
        report = new_loop.run_until_complete(research_report(query))
        return report
    finally:
        new_loop.close()

with gr.Blocks() as run_gpt_researcher:    
    with gr.Tab("Run Query"):
        with gr.Row():
            query_input = gr.Text(label="Research Query")
        with gr.Row():
            btn = gr.Button("Research")
        with gr.Row():
            out = gr.Textbox(label="Output Research Report")
        
        btn.click(fn=run_gpt_on_query, inputs=[query_input], outputs=out, show_progress=True)


run_gpt_researcher.launch(server_port=7900)