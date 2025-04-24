import imaplib
import email
import re
import threading
import time
from flask import Flask, jsonify
import os

IMAP_SERVER = 'ssl0.ovh.net'
EMAIL_ACCOUNT = os.environ.get('EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

latest_code = ""

def fetch_email_code():
    global latest_code
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            mail.select("inbox")

            status, messages = mail.search(None, '(UNSEEN)')
            email_ids = messages[0].split()

            for e_id in email_ids:
                status, msg_data = mail.fetch(e_id, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()

                # 🔍 Filtre par contenu Udemy
                if "Use the code below to log in to your Udemy account" in body:
                    codes = re.findall(r'\b\d{6}\b', body)
                    if codes:
                        latest_code = codes[0]
                        print(f"Nouveau code: {latest_code}")
        except Exception as e:
            print("Erreur:", e)

        time.sleep(10)

app = Flask(__name__)

@app.route('/code')
def get_code():
    return jsonify({"code": latest_code})

if __name__ == '__main__':
    t = threading.Thread(target=fetch_email_code)
    port = int(os.environ.get("PORT", 10000))
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=port)
