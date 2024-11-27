from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Run Python Script as a Web App</h1>
    <form action="/run" method="post">
        <label for="args">Enter Arguments for main.py:</label>
        <input type="text" id="args" name="args" placeholder="Enter arguments (optional)">
        <button type="submit">Run</button>
    </form>
    """

@app.route('/run', methods=['POST'])
def run_script():
    # Get arguments for the script
    args = request.form.get('args', '')

    # Construct the command
    command = f"python main.py {args}"

    try:
        # Run the main.py script with the provided arguments
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
