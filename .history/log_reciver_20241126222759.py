from flask import Flask, request, Response
import datetime
import json

app = Flask(__name__)
log_messages = []

@app.route('/')
def home():
    html = """
    <html>
        <head>
            <title>Real-time Logs</title>
            <script>
                function refreshLogs() {
                    fetch('/logs')
                        .then(response => response.text())
                        .then(data => {
                            document.getElementById('logs').innerHTML = data;
                        });
                }
                setInterval(refreshLogs, 1000);
            </script>
            <style>
                pre {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    padding: 10px;
                    background-color: #f5f5f5;
                }
            </style>
        </head>
        <body>
            <h1>Real-time Logs</h1>
            <pre id="logs"></pre>
        </body>
    </html>
    """
    return html

@app.route('/log', methods=['POST'])
def receive_log():
    try:
        # Try to parse as JSON first
        content = request.get_json(silent=True)
        if content:
            log_message = str(content)
        else:
            # If not JSON, get raw data
            log_message = request.get_data(as_text=True)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {log_message}"
        log_messages.append(full_message)
        return "OK"
    except Exception as e:
        print(f"Error processing log: {e}")
        return "Error", 500

@app.route('/logs')
def get_logs():
    return "<br>".join(reversed(log_messages[-100:]))  # Keep last 100 messages, newest first

if __name__ == '__main__':
    app.run(host='localhost', port=8700, debug=True)