import gradio as gr
import asyncio
from gpt_researcher import GPTResearcher

if globals().get('run_gpt_researcher'):          
    run_gpt_researcher.close()

REPORT_TYPE = "research_report"

async def research_report(query):
    researcher = GPTResearcher(query=query, report_type=REPORT_TYPE)
    report = await researcher.conduct_research()
    return report


async def run_gpt_on_query(query):
    report = asyncio.run(research_report(query))
    return report

with gr.Blocks() as run_gpt_researcher:    
    with gr.Tab("Run Query"):
        with gr.Row():
            query_input = gr.Text(label="Research Query")
        with gr.Row():
            # query_input.submit(fn=run_gpt_on_query, inputs=[query_input], outputs=report, show_progress=True)  # This handles Ctrl+Enter
            btn = gr.Button("Research")  # Optional button for mouse users
        with gr.Row():
            out = gr.Textbox(label="Output Research Report", )
        
        btn.click(fn=run_gpt_on_query, inputs=[query_input], outputs=out, show_progress=True)

        # with gr.Row():
        

run_gpt_researcher.launch(server_port=7900)

