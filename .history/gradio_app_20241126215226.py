import gradio as gr
from gpt_researcher import GPTResearcher
import asyncio
from dotenv import load_dotenv
import logging
import queue
import threading
from typing import Optional
import sys
from datetime import datetime

load_dotenv()

if globals().get('run_gpt_researcher'):          
    run_gpt_researcher.close()

REPORT_TYPE = "research_report"

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)

class Progress:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.handler = QueueHandler(self.log_queue)
        self.handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                            datefmt='%H:%M:%S')
        )
        
        # Add handler to root logger
        logging.getLogger().addHandler(self.handler)
        logging.getLogger().setLevel(logging.INFO)

    def update_text(self, textbox: Optional[gr.Textbox] = None):
        while True:
            try:
                msg = self.log_queue.get_nowait()
                if textbox is not None:
                    current_text = textbox.value or ""
                    textbox.value = current_text + "\n" + msg
                    yield textbox.value
            except queue.Empty:
                break

async def research_report(query, progress: Progress, textbox: gr.Textbox):
    try:
        researcher = GPTResearcher(query=query, report_type=REPORT_TYPE)
        report = await researcher.conduct_research()
        
        # Add final report to the output
        current_text = textbox.value or ""
        textbox.value = current_text + "\n\nFINAL REPORT:\n" + "="*50 + "\n" + report
        return textbox.value
    except Exception as e:
        error_msg = f"\nError during research: {str(e)}"
        current_text = textbox.value or ""
        textbox.value = current_text + error_msg
        return textbox.value

def run_gpt_on_query(query, progress=gr.Progress()):
    # Create Progress instance for logging
    prog = Progress()
    
    # Create a new event loop for this thread
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    
    try:
        # Initialize output textbox
        textbox = gr.Textbox()
        textbox.value = f"Starting research for query: {query}\n{'='*50}\n"
        
        # Run the research
        result = new_loop.run_until_complete(research_report(query, prog, textbox))
        
        # Get any remaining logs
        for update in prog.update_text(textbox):
            progress(0.5, desc="Processing...")
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"
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

# Launch the app
run_gpt_researcher.launch(
    server_port=7900,
    show_error=True,
    favicon_path=None
)