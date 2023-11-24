import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token.
bot_token = "6376673556:AAFUw21pWQ3vPv1BZLDtl2_Xf23iMEmYFLA"
base_url = f"https://api.telegram.org/bot{bot_token}/"

def get_chat_id(update):
    return update["message"]["chat"]["id"]

def is_valid_url(url):
    return re.match(r'^(http|https)://', url) is not None

def read_msg(update):
    message = update.get("message", {}).get("text")
    start_index = message.find("recordingId=")
    end_index = message.find("&", start_index)
    chat_id = get_chat_id(update)
    if start_index != -1 and end_index != -1:
        recording_id = message[start_index + len("recordingId="):end_index]
        print(recording_id)
        video_url = f"https://static.smpopular.com/production/uploading/recordings/{recording_id}/master.mp4"
        send_video(chat_id, video_url)
    else:
        send_msg(chat_id, "Invalid or missing recording ID. Please provide a valid link.")

def send_msg(chat_id, text):
    if chat_id:
        parameter = {
            "chat_id": chat_id,
            "text": text if text else "This URL will not exist. Please check it."
        }
        requests.post(base_url + "sendMessage", data=parameter)

def send_video(chat_id, video_url):
    if chat_id:
        parameter = {
            "chat_id": chat_id,
        }
        r = requests.get(video_url)  
        with open(r'./audio.m4a', 'wb') as f:
            f.write(r.content)
        files = {
            "audio": open(r'./audio.m4a', 'rb')
        }
        resp = requests.post(base_url + "sendAudio", data=parameter, files=files)
        
@app.route("/webhook", methods=["POST","GET"])
def webhook():
    if request.method == "POST":
        update = request.json
        read_msg(update)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
