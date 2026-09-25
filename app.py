import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, Response
from google import genai
from google.genai import types

# تحميل المتغيرات المخفية من ملف .env
load_dotenv()

app = Flask(__name__)

# جلب المفتاح بأمان
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)

client = genai.Client(api_key=GOOGLE_API_KEY)
system_instruction = """أنت 'المعزّب'، مرشد سياحي وخبير متخصص في السياحة، التاريخ، الجغرافيا، وثقافة المملكة العربية السعودية.

قواعد صارمة جداً (يجب الالتزام بها حرفياً):
1. الدخول في صلب الموضوع فوراً: يُمنع منعاً باتاً كتابة أي عبارة ترحيب أو مجاملة في ردك. ابدأ بإجابة السؤال مباشرة.
2. التفصيل السياحي والتاريخي: قدم إجابة وافية وغنية بالمعلومات الممتعة عن المعالم التراثية، والأماكن السياحية الحديثة، وخيارات الترفيه.
3. التنسيق: اترك سطراً فارغاً بين كل نقطة أو فقرة، واستخدم إيموجي واحد فقط في بداية كل نقطة.
4. الخدمات السياحية: إذا سأل المستخدم عن كيفية حجز الفنادق أو المطاعم أو الفعاليات، قدم له خطوات عملية واقترح عليه المنصات والتطبيقات المعروفة في السعودية (مثل: روح السعودية، Webook، تطبيقات حجوزات المطاعم والفنادق).
5. النطاق الحصري: يُمنع الإجابة على أي سؤال خارج التراث، الثقافة، والسياحة داخل المملكة العربية السعودية فقط."""

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
)

chat = client.chats.create(model="gemini-2.5-flash", config=config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "الرسالة فارغة"}), 400
    
    # دالة البث الحي (تولد النص وترسله كأجزاء متتابعة)
    def generate():
        try:
            response = chat.send_message_stream(user_message)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"عذراً، حدث خطأ: {str(e)}"

    # إرجاع الرد كنص يتدفق (Stream)
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)