import gradio as gr
import requests

BACKEND_URL = "http://localhost:8000"

def query_backend(query):
    try:
        response = requests.post(
            f"{BACKEND_URL}/research",
            json={"query": query}  # Properly format the request body
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["report"]
    except requests.RequestException as e:
        return f"Error making request: {str(e)}"

with gr.Blocks() as research_interface:    
    with gr.Tab("Run Query"):
        with gr.Row():
            query_input = gr.Text(label="Research Query")
        with gr.Row():
            btn = gr.Button("Research")
        with gr.Row():
            out = gr.Textbox(label="Output Research Report")
        
        btn.click(fn=query_backend, inputs=[query_input], outputs=out, show_progress=True)

if __name__ == "__main__":
    research_interface.launch(server_port=7900)