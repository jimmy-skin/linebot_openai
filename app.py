from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 訊息計數器
openai_message_count = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global openai_message_count  # 使用全域變數

    user_input = event.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            temperature=0.5,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位專業的星座師，請使用繁體中文回應，提供有深度又貼近日常生活的星座分析與建議。"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        reply_text = response['choices'][0]['message']['content'].strip()
        openai_message_count += 1  # 計數器加一

    except Exception as e:
        reply_text = '發生錯誤，請稍後再試！'

    # 回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# 可選：建立一個路由讓你查看目前累計的回應次數
@app.route('/count', methods=['GET'])
def get_count():
    return f"目前已傳送 {openai_message_count} 則 OpenAI 回應訊息。"

if __name__ == '__main__':
    app.run()
