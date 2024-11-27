import gradio as gr
import asyncio
import sys
from datetime import datetime
from time import time

class MockResearcher:
    def __init__(self, query: str, report_type: str):
        self.query = query
        self.report_type = report_type

    async def conduct_research(self):
        yield f"{self._get_timestamp()} Starting research process...\n"
        await asyncio.sleep(1)
        yield f"{self._get_timestamp()} Searching through academic papers...\n"
        await asyncio.sleep(1)
        yield f"{self._get_timestamp()} Analyzing web results...\n"
        await asyncio.sleep(1)
        yield f"{self._get_timestamp()} Extracting key information...\n"
        await asyncio.sleep(1)
        yield f"{self._get_timestamp()} Synthesizing findings...\n"
        await asyncio.sleep(1)
        yield f"{self._get_timestamp()} Finalizing report...\n"
        yield "\n" + "="*50 + "\n"
        yield "Final Report: Analysis of the research topic completed successfully.\n"
        yield "="*50 + "\n"

    def _get_timestamp(self):
        return datetime.now().strftime("[%H:%M:%S]")

async def run_test(progress=gr.Progress()):
    current_output = f"Starting test run at {datetime.now().strftime('%H:%M:%S')}\n{'='*50}\n"
    yield current_output
    
    researcher = MockResearcher(query="test query", report_type="test")
    async for update in researcher.conduct_research():
        current_output += update
        yield current_output
    
    current_output += f"Test completed at {datetime.now().strftime('%H:%M:%S')}\n"
    yield current_output

def create_interface():
    with gr.Blocks() as interface:
        with gr.Row():
            with gr.Column():
                start_btn = gr.Button("Run Test", variant="primary")
                clear_btn = gr.Button("Clear Output", variant="secondary")
        
        with gr.Row():
            output = gr.Textbox(
                label="Test Progress and Results",
                lines=20,
                max_lines=30,
                show_copy_button=True,
                interactive=False,
                autoscroll=True
            )
            
        start_btn.click(
            fn=run_test,
            outputs=output,
            show_progress=True
        )
        
        clear_btn.click(
            fn=lambda: "",
            outputs=output
        )
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(server_port=7900)