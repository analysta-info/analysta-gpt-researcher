from flask import Flask, request, Response
import datetime

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
    log_messages.append(f"{datetime.datetime.now()}: {request.data.decode()}")
    return "OK"

@app.route('/logs')
def get_logs():
    return "<br>".join(log_messages[-100:])  # Keep last 100 messages

if __name__ == '__main__':
    app.run(host='localhost', port=8700)