import requests
import json
import os

CONFIG_FILE = "user_config.json"

class TelegramNotifier:
    def __init__(self):
        self.token = None
        self.chat_id = None
        self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.token = data.get('telegram_token')
                    self.chat_id = data.get('telegram_chat_id')
            except:
                pass

    def save_config(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'telegram_token': token, 'telegram_chat_id': chat_id}, f)

    def send_message(self, message):
        if not self.token or not self.chat_id:
            return False, "Token veya Chat ID eksik."

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                return True, "Mesaj iletildi!"
            else:
                return False, f"Hata: {response.text}"
        except Exception as e:
            return False, f"Bağlantı Hatası: {str(e)}"

    def send_alert(self, ticker, action, price, reason):
        emoji = "🟢" if action == "BUY" else "🔴"
        msg = (
            f"{emoji} **SİNYAL: {ticker}**\n"
            f"**İşlem:** {action}\n"
            f"**Fiyat:** ${price}\n"
            f"**Neden:** {reason}\n"
            f"-------------------\n"
            f"🤖 *VisionFinance-Pro*"
        )
        return self.send_message(msg)
