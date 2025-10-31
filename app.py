from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ✅ Webhook Verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Invalid verification", 403


# ✅ Receiving Messages
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    if data and data.get("entry"):
        try:
            message = data['entry'][0]['changes'][0]['value']
            if "messages" in message:
                msg = message['messages'][0]
                phone_number = msg['from']

                # Check if button clicked or text typed
                if msg.get("type") == "interactive":
                    button_reply = msg["interactive"]["button_reply"]["id"]
                    handle_button(phone_number, button_reply)
                elif msg.get("type") == "text":
                    send_welcome(phone_number)
        except Exception as e:
            print("Error:", e)

    return jsonify({"status": "received"}), 200


# ✅ Send Welcome Message with Buttons
def send_welcome(to):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "👋 *Welcome to MOMO MAFIYA!* \nWhat would you like to do today?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "book_order", "title": "🛍️ Book Order"}},
                    {"type": "reply", "reply": {"id": "menu", "title": "📜 Menu & Prices"}},
                    {"type": "reply", "reply": {"id": "location", "title": "📍 Location"}},
                    {"type": "reply", "reply": {"id": "offers", "title": "🎁 Offers"}}
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=data)


# ✅ Handle Button Clicks
def handle_button(to, button_id):
    if button_id == "book_order":
        send_text(to, "🛒 Please type your order like:\n\n_2 Veg Momos + 1 Fries_\nWe’ll confirm your total and delivery time soon.")
    elif button_id == "menu":
        send_text(to, "🍱 *MOMO MAFIYA MENU*\n\n🥟 Veg Momos — ₹60\n🍗 Chicken Momos — ₹80\n🍟 Fries — ₹50\n🍹 Drinks — ₹30")
    elif button_id == "location":
        send_text(to, "📍 *MOMO MAFIYA Stall*\nढेकहा तिराहा, Rewa (M.P.)\n⏰ 12PM – 10PM\n📞 8359091978")
    elif button_id == "offers":
        send_text(to, "🎉 *Today’s Offer:*\nBuy 2 Momos, Get 1 Fries FREE! 🥳")


# ✅ Send Text Message
def send_text(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)


# ✅ Run Server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
