from flask import Flask, request, render_template, jsonify
import requests
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json['message']
    rasa_response = requests.post(
        'http://localhost:5005/webhooks/rest/webhook',
        json={"message": user_message}
    )
    messages = rasa_response.json()
    if messages:
        return jsonify({"reply": messages[0]['text']})
    else:
        return jsonify({"reply": "Oprosti, nisem te razumela."})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
