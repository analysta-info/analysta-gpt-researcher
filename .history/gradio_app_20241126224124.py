import gradio as gr
from gpt_researcher import GPTResearcher
import asyncio
from dotenv import load_dotenv
import sys
from io import StringIO
import threading
import queue
import time

load_dotenv()

if globals().get('run_gpt_researcher'):          
    run_gpt_researcher.close()

REPORT_TYPE = "research_report"

class OutputCapture:
    def __init__(self, textbox: gr.Textbox):
        self.textbox = textbox
        self.queue = queue.Queue()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        self.original_stdout.write(text)  # Still write to original stdout
        self.queue.put(text)
        
    def flush(self):
        self.original_stdout.flush()

async def update_output(capture: OutputCapture, textbox: gr.Textbox):
    """Update the textbox with captured output"""
    while True:
        try:
            # Get all current messages from queue
            while not capture.queue.empty():
                text = capture.queue.get_nowait()
                current = textbox.value if textbox.value else ""
                textbox.value = current + text
            await asyncio.sleep(0.1)  # Small delay to prevent excessive updates
        except queue.Empty:
            continue

async def research_report(query: str, textbox: gr.Textbox):
    # Set up output capture
    capture = OutputCapture(textbox)
    sys.stdout = capture
    sys.stderr = capture
    
    try:
        # Start the output updater
        updater_task = asyncio.create_task(update_output(capture, textbox))
        
        # Create and run researcher
        researcher = GPTResearcher(query=query, report_type=REPORT_TYPE)
        report = await researcher.conduct_research()
        
        # Cancel the updater task
        updater_task.cancel()
        
        # Restore original stdout/stderr
        sys.stdout = capture.original_stdout
        sys.stderr = capture.original_stderr
        
        # Get any remaining output from queue
        while not capture.queue.empty():
            text = capture.queue.get_nowait()
            current = textbox.value if textbox.value else ""
            textbox.value = current + text
        
        # Add final report with clear separation
        textbox.value += "\n\n" + "="*50 + "\nFINAL REPORT:\n" + "="*50 + "\n\n" + report
        
        return textbox.value
        
    except Exception as e:
        sys.stdout = capture.original_stdout
        sys.stderr = capture.original_stderr
        error_msg = f"\nError during research: {str(e)}\n"
        textbox.value += error_msg
        return textbox.value

def run_gpt_on_query(query):
    # Create a new event loop for this thread
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    try:
        # Initialize output textbox
        textbox = gr.Textbox()
        textbox.value = f"Starting research for query: {query}\n{'='*50}\n"
        
        # Run the research
        result = new_loop.run_until_complete(research_report(query, textbox))
        return result
    finally:
        new_loop.close()

with gr.Blocks() as run_gpt_researcher:    
    with gr.Tab("Run Query"):
        with gr.Row():
            query_input = gr.Text(
                label="Research Query",
                placeholder="Enter your research question here..."
            )
        with gr.Row():
            btn = gr.Button("Start Research", variant="primary")
        with gr.Row():
            out = gr.Textbox(
                label="Research Progress and Results",
                lines=20,
                max_lines=30,
                show_copy_button=True,
                autoscroll=True
            )
        
        btn.click(
            fn=run_gpt_on_query,
            inputs=[query_input],
            outputs=out,
            show_progress=True
        )

        # Add a clear button
        clear_btn = gr.Button("Clear Output", variant="secondary")
        clear_btn.click(lambda: "", outputs=[out])

run_gpt_researcher.launch(server_port=7900, show_error=True)