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
        print(f"{self._get_timestamp()} Starting research process...")
        await asyncio.sleep(1)
        print(f"{self._get_timestamp()} Searching through academic papers...")
        await asyncio.sleep(1)
        print(f"{self._get_timestamp()} Analyzing web results...")
        await asyncio.sleep(1)
        print(f"{self._get_timestamp()} Extracting key information...")
        await asyncio.sleep(1)
        print(f"{self._get_timestamp()} Synthesizing findings...")
        await asyncio.sleep(1)
        print(f"{self._get_timestamp()} Finalizing report...")
        return "Final Report: Analysis of the research topic completed successfully."

    def _get_timestamp(self):
        return datetime.now().strftime("[%H:%M:%S]")

class OutputCapture:
    def __init__(self, textbox: gr.Textbox):
        self.textbox = textbox
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        self.original_stdout.write(text)
        if hasattr(self.textbox, 'value'):
            current = self.textbox.value if self.textbox.value else ""
            self.textbox.value = current + text
            
    def flush(self):
        self.original_stdout.flush()

async def run_test(progress=gr.Progress()):
    # Initialize output textbox
    textbox = gr.Textbox()
    textbox.value = f"Starting test run at {datetime.now().strftime('%H:%M:%S')}\n{'='*50}\n"
    
    # Set up output capture
    capture = OutputCapture(textbox)
    sys.stdout = capture
    sys.stderr = capture
    
    try:
        # Create and run mock researcher
        researcher = MockResearcher(query="test query", report_type="test")
        report = await researcher.conduct_research()
        
        # Add final report with formatting
        textbox.value += f"\n{'='*50}\n"
        textbox.value += f"FINAL REPORT:\n{report}\n"
        textbox.value += f"{'='*50}\n"
        textbox.value += f"Test completed at {datetime.now().strftime('%H:%M:%S')}\n"
        
        return textbox.value
        
    finally:
        sys.stdout = capture.original_stdout
        sys.stderr = capture.original_stderr

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