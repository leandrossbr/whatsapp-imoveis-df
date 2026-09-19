from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    
    print("\n" + "="*60)
    print(f"📥 WEBHOOK RECEBIDO - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("="*60 + "\n")
    
    # Extrai info básica se for mensagem
    if data and "data" in data:
        msg = data["data"]
        if "message" in msg:
            m = msg["message"]
            from_num = msg.get("key", {}).get("remoteJid", "desconhecido")
            text = ""
            if "conversation" in m:
                text = m["conversation"]
            elif "extendedTextMessage" in m:
                text = m["extendedTextMessage"].get("text", "")
            
            if text:
                print(f"💬 De: {from_num}")
                print(f"📝 Texto: {text}")
    
    return jsonify({"status": "ok", "received": True}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "webhook-teste"}), 200

if __name__ == "__main__":
    print("🚀 Webhook teste rodando em http://0.0.0.0:5000")
    print("📋 Configure no Evolution: http://host.docker.internal:5000/webhook")
    print("🔍 Eventos: messages.upsert")
    app.run(host="0.0.0.0", port=5000, debug=True)