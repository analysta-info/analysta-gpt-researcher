import gradio as gr
import asyncio
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from io import StringIO
from gpt_researcher import GPTResearcher

load_dotenv()

class StreamHandler(logging.Handler):
    def __init__(self, string_buffer):
        super().__init__()
        self.string_buffer = string_buffer

    def emit(self, record):
        msg = self.format(record)
        self.string_buffer.write(msg + '\n')

class OutputCapture:
    def __init__(self):
        self.outputs = []
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.string_buffer = StringIO()
        
        # Setup logging capture
        self.log_handler = StreamHandler(self.string_buffer)
        self.log_handler.setFormatter(
            logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        )
        
        # Capture all relevant loggers
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger('httpx').addHandler(self.log_handler)
        logging.getLogger('gpt_researcher').addHandler(self.log_handler)
        
        # Set logging level to INFO to capture all relevant messages
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('httpx').setLevel(logging.INFO)
        logging.getLogger('gpt_researcher').setLevel(logging.INFO)

    def write(self, text):
        self.original_stdout.write(text)
        self.string_buffer.write(text)
        self.outputs.append(text)

    def flush(self):
        self.original_stdout.flush()

    def get_output(self):
        return self.string_buffer.getvalue()

    def cleanup(self):
        # Remove our custom handler from all loggers
        logging.getLogger().removeHandler(self.log_handler)
        logging.getLogger('httpx').removeHandler(self.log_handler)
        logging.getLogger('gpt_researcher').removeHandler(self.log_handler)

async def run_research(progress=gr.Progress()):
    # Initialize output capture
    output_capture = OutputCapture()
    sys.stdout = output_capture
    sys.stderr = output_capture
    
    try:
        # Setup initial output
        current_output = f"Starting research at {datetime.now().strftime('%H:%M:%S')}\n{'='*50}\n"
        yield current_output
        
        # Run the research
        researcher = GPTResearcher(
            query="What are the best ways to use a loss functions when fine tuning an LLM model?",
            report_type="research_report"
        )
        
        # Create a task for the research
        research_task = asyncio.create_task(researcher.conduct_research())
        
        # While the research is running, periodically check for new output
        while not research_task.done():
            await asyncio.sleep(0.1)  # Small delay to prevent CPU overload
            new_output = output_capture.get_output()
            if new_output != current_output:
                current_output = new_output
                yield current_output
        
        # Get the final report
        report = await research_task
        
        # Add final formatting
        final_output = current_output + "\n" + "="*50 + "\n"
        final_output += "FINAL REPORT:\n" + str(report) + "\n"
        final_output += "="*50 + "\n"
        final_output += f"Research completed at {datetime.now().strftime('%H:%M:%S')}\n"
        
        yield final_output
        
    finally:
        # Restore original stdout/stderr and cleanup logging
        sys.stdout = output_capture.original_stdout
        sys.stderr = output_capture.original_stderr
        output_capture.cleanup()

def create_interface():
    with gr.Blocks() as interface:
        with gr.Row():
            with gr.Column():
                start_btn = gr.Button("Start Research", variant="primary")
                clear_btn = gr.Button("Clear Output", variant="secondary")
        
        with gr.Row():
            output = gr.Textbox(
                label="Research Progress and Results",
                lines=20,
                max_lines=30,
                show_copy_button=True,
                interactive=False,
                autoscroll=True
            )
            
        start_btn.click(
            fn=run_research,
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
    print("Starting Gradio interface...")
    interface.launch(
        server_port=7900,
        quiet=True  # This prevents some of Gradio's default logging
    )