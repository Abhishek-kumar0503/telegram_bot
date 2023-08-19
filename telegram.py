#correct
import requests
import re

base_url = "https://api.telegram.org/bot6376673556:AAFUw21pWQ3vPv1BZLDtl2_Xf23iMEmYFLA"

def get_chat_id(update):
    return update["message"]["chat"]["id"]

def read_msg(offset):
    parameter = {
        "offset": offset
    }
    resp = requests.get(base_url + "/getUpdates", params=parameter)
    data = resp.json()

    print(data)
    for result in data.get("result", []):
        message = result.get("message", {}).get("text")
        chat_id = get_chat_id(result)
        if message and is_valid_url(message):
            response = requests.get(message)
            message_text = response.url
            recording_id = re.search(r'recordingId=(\d+)', message_text)
            if recording_id:
                v = recording_id.group(1)
                send_msg(chat_id, f"https://static.smpopular.com/production/uploading/recordings/{v}/master.mp4")
        else:
            send_msg(chat_id, "Invalid or missing recording ID. Please provide a valid link.")

    if "result" in data and data["result"]:
        return data["result"][-1]["update_id"] + 1

def send_msg(chat_id, text):
    if chat_id:
        parameter = {
            "chat_id": chat_id,
            "text": text if text else "This url will not exist please check it"
        }
        resp = requests.post(base_url + "/sendMessage", json=parameter)

def is_valid_url(url):
    return re.match(r'^https?://', url) is not None


offset = 0
while True:
    offset = read_msg(offset)
