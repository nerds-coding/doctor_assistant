from flask import Flask, request, jsonify, render_template
from speech_to_text import DoctorAssistant

app = Flask(__name__)

# Instantiate the DoctorAssistant class
assistant = DoctorAssistant()


@app.route("/")
def index():
    return render_template("index.html")


# Route to handle speech processing
@app.route("/process", methods=["POST"])
def process_speech():
    data = request.json
    command = data.get("command", "")
    response = assistant.process_command(command)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
