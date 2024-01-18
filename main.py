import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token.
bot_token = "6376673556:AAFUw21pWQ3vPv1BZLDtl2_Xf23iMEmYFLA"
base_url = f"https://api.telegram.org/bot{bot_token}/"

def get_chat_id(update):
    return update["message"]["chat"]["id"]

# def is_valid_url(url):
#     return re.match(r'^(http|https)://', url) is not None

def extract_main_link(input_data):
    A = input_data
    match = re.search(r'https://tmx28\.app\.goo\.gl/\w+', input_data)
    if match:
        link = match.group()
    else:
        link = input_data
    try:
        return requests.head(link, allow_redirects=True).url
    except Exception as e:
        return A
        
def read_msg(update):
    messages = update.get("message", {}).get("text")
    print(messages)
    message= extract_main_link(messages)
    print(message)
    url_pattern = re.compile(r'https?://\S+')
    urls = re.findall(url_pattern, message)
    for url in urls:
        print(url)
    start_index = message.find("recordingId=")
    end_index = message.find("&", start_index)
    chat_id = get_chat_id(update)
    if start_index != -1 and end_index != -1:
        recording_id = message[start_index + len("recordingId="):end_index]
        print(recording_id)
        video_url = f"https://static.smpopular.com/production/uploading/recordings/{recording_id}/master.mp4"
        html_text = requests.get(url).text
        url_to_check = 'https://improxy.smpopular.com/tools/im/560/production/uploading/recordings'
        # Check if the specific URL format is present in the HTML content
        if url_to_check in html_text:
            print("The webpage contains the specified URL format. It's likely a video.")
            send_video(chat_id, video_url)
        else:
            print("The webpage does not contain the specified URL format. It's likely an audio.")
            send_audio(chat_id, video_url)
    else:
        send_msg(chat_id, "123Invalid or missing recording ID. Please provide a valid link.")

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
        files = {
            "video": requests.get(video_url).content
        }
        requests.post(base_url + "sendVideo", data=parameter, files=files)
        
def send_audio(chat_id, video_url):
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
