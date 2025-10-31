from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return challenge, 200
    else:
        print("❌ Verification failed.")
        return "Invalid verification", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    if data and data.get("entry"):
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            phone_number = message['from']
            user_text = message['text']['body'].lower()
            reply_text = process_message(user_text)
            send_message(phone_number, reply_text)
        except Exception as e:
            print("Error:", e)
    return jsonify({"status": "received"}), 200

def process_message(text):
    if "menu" in text:
        return "🍱 MOMO MAFIYA MENU:\n🥟 Veg Momos ₹60\n🍗 Chicken Momos ₹80\n🍟 Fries ₹50\n🍹 Drinks ₹30\n\nType item name to order."
    elif "order" in text:
        return "🛍️ Please type your order like:\n'2 Veg Momos + 1 Fries'\nWe’ll confirm it soon!"
    elif "offer" in text:
        return "🎁 Offer: Buy 2 Momos, Get 1 Fries Free!"
    elif "location" in text:
        return "📍 MOMO MAFIYA\nढेकहा तिराहा, Rewa (M.P.)\n⏰ 12PM–10PM\n📞 8359091978"
    else:
        return "👋 Welcome to *MOMO MAFIYA!*\nType:\n1️⃣ Menu\n2️⃣ Order\n3️⃣ Offers\n4️⃣ Location"

def send_message(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
