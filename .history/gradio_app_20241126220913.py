import gradio as gr
import asyncio
import sys
from datetime import datetime
from dotenv import load_dotenv
from io import StringIO
from gpt_researcher import GPTResearcher

load_dotenv()

class CLIOutputCapture:
    def __init__(self):
        self.outputs = []
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.string_buffer = StringIO()

    def write(self, text):
        self.original_stdout.write(text)
        self.string_buffer.write(text)
        self.outputs.append(text)

    def flush(self):
        self.original_stdout.flush()

    def get_output(self):
        return self.string_buffer.getvalue()

async def run_research(progress=gr.Progress()):
    # Initialize output capture
    output_capture = CLIOutputCapture()
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
        # Restore original stdout/stderr
        sys.stdout = output_capture.original_stdout
        sys.stderr = output_capture.original_stderr

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
    interface.launch(server_port=7900)