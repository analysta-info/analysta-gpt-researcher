from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Run CLI as Web App</h1>
    <form action="/run" method="post">
        <label for="command">Enter Command:</label>
        <input type="text" id="command" name="command" required>
        <button type="submit">Run</button>
    </form>
    """

@app.route('/run', methods=['POST'])
def run_command():
    command = request.form.get('command')
    if not command:
        return jsonify({"error": "No command provided"}), 400

    try:
        # Run the command and capture output
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response = {
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        response = {"error": str(e)}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
