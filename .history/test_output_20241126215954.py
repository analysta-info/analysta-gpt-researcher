import asyncio
import pytest
import gradio as gr
from time import time
import sys
from typing import List

# Mock researcher class to simulate delayed outputs
class MockResearcher:
    def __init__(self, query: str, report_type: str):
        self.query = query
        self.report_type = report_type

    async def conduct_research(self):
        print("Starting research process...")
        await asyncio.sleep(1)
        print("Gathering information...")
        await asyncio.sleep(1)
        print("Processing data...")
        await asyncio.sleep(1)
        print("Finalizing report...")
        return "Final Report Content"

class OutputCapture:
    def __init__(self, textbox: gr.Textbox):
        self.textbox = textbox
        self.captured_outputs: List[str] = []
        self.timestamps: List[float] = []
        self.original_stdout = sys.stdout
        
    def write(self, text):
        self.original_stdout.write(text)
        self.captured_outputs.append(text)
        self.timestamps.append(time())
        if hasattr(self, 'textbox') and self.textbox is not None:
            current = self.textbox.value if self.textbox.value else ""
            self.textbox.value = current + text
        
    def flush(self):
        self.original_stdout.flush()

async def test_output(textbox: gr.Textbox):
    # Set up output capture
    capture = OutputCapture(textbox)
    sys.stdout = capture
    
    try:
        # Create and run mock researcher
        researcher = MockResearcher(query="test query", report_type="test")
        report = await researcher.conduct_research()
        
        # Add final report
        textbox.value += "\n\nFinal Report:\n" + report
        
        # Analyze timing between outputs
        time_differences = []
        for i in range(1, len(capture.timestamps)):
            diff = capture.timestamps[i] - capture.timestamps[i-1]
            time_differences.append(diff)
        
        # Create timing report
        timing_report = "\n\nTiming Analysis:\n"
        timing_report += "==================\n"
        for i, diff in enumerate(time_differences):
            timing_report += f"Time between output {i+1} and {i+2}: {diff:.2f} seconds\n"
        
        textbox.value += timing_report
        
        return textbox.value
        
    finally:
        sys.stdout = capture.original_stdout

@pytest.mark.asyncio
async def test_real_time_output():
    # Initialize a mock textbox
    textbox = gr.Textbox()
    textbox.value = ""
    
    # Run the test
    start_time = time()
    result = await test_output(textbox)
    total_time = time() - start_time
    
    # Verify the output contains all expected messages
    expected_messages = [
        "Starting research process...",
        "Gathering information...",
        "Processing data...",
        "Finalizing report..."
    ]
    
    for msg in expected_messages:
        assert msg in result, f"Missing expected message: {msg}"
    
    # Verify total time is approximately 4 seconds (3 delays + processing time)
    assert 3.5 < total_time < 4.5, f"Unexpected total time: {total_time}"
    
    return result

if __name__ == "__main__":
    # Run the test and print results
    async def main():
        textbox = gr.Textbox()
        result = await test_output(textbox)
        print("\nFull test output:")
        print("================")
        print(result)
    
    asyncio.run(main())