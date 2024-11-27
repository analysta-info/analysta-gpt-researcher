import gradio as gr
import requests

BACKEND_URL = "http://localhost:8000"

def query_backend(query):
    response = requests.post(f"{BACKEND_URL}/research", json={"query": query})
    if response.status_code == 200:
        return response.json()["report"]
    else:
        return f"Error: {response.status_code} - {response.text}"

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