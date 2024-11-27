from flask import Flask, request, Response
import datetime
import json
import re
from ansi2html import Ansi2HTMLConverter

app = Flask(__name__)
log_messages = []
conv = Ansi2HTMLConverter()

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
                body {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: monospace;
                    padding: 20px;
                }
                h1 {
                    color: #ffffff;
                }
                .log-container {
                    background-color: #2d2d2d;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }
                .log-entry {
                    margin: 5px 0;
                    padding: 5px;
                    border-bottom: 1px solid #3d3d3d;
                }
                .INFO { color: #4ec9b0; }
                .WARNING { color: #dcdcaa; }
                .ERROR { color: #f44747; }
                .DEBUG { color: #569cd6; }
                .CRITICAL { color: #ff0000; }
            </style>
        </head>
        <body>
            <h1>Real-time Logs</h1>
            <div class="log-container">
                <div id="logs"></div>
            </div>
        </body>
    </html>
    """
    return html

@app.route('/log', methods=['POST'])
def receive_log():
    try:
        log_message = request.get_data(as_text=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract log level from the message
        level_match = re.search(r'(INFO|WARNING|ERROR|DEBUG|CRITICAL)', log_message)
        level = level_match.group(1) if level_match else "INFO"
        
        # Convert ANSI colors to HTML
        html_message = conv.convert(log_message, full=False)
        
        full_message = f'<div class="log-entry {level}">{html_message}</div>'
        log_messages.append(full_message)
        return "OK"
    except Exception as e:
        print(f"Error processing log: {e}")
        return "Error", 500

@app.route('/logs')
def get_logs():
    return "".join(reversed(log_messages[-100:]))  # Keep last 100 messages, newest first

if __name__ == '__main__':
    app.run(host='localhost', port=8700, debug=True)