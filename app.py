import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("google-generativeai paketi eksik! Lütfen 'pip install google-generativeai' komutunu çalıştırın.")


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY .env dosyasında tanımlı değil!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro-vision")


product_catalog = [
    {
        "title": "TESAMMANS Büyük Halı",
        "description": "Çok renkli desenleriyle odanıza canlılık katacak, büyük boyutlu bir halı."
    },
    {
        "title": "LOHALS Jüt Halı",
        "description": "Doğal jüt malzemesiyle evinize sıcaklık ve doğallık getirin."
    },
    
]

def format_catalog(catalog):
    return "\n".join([f"{p['title']}: {p['description']}" for p in catalog])

app = Flask(__name__)
CORS(app)  

@app.route("/gemini-analyze", methods=["POST"])
def gemini_analyze():
    if 'image' not in request.files or 'prompt' not in request.form:
        return jsonify({"error": "Eksik veri: 'image' ve 'prompt' gereklidir."}), 400

    try:
        image_file = request.files['image']
        prompt = request.form['prompt']
        image = Image.open(image_file.stream)

        catalog_text = format_catalog(product_catalog)

        full_prompt = f"""
Sen bir iç mimarlık danışmanısın. Kullanıcı bir ürün görseli yükledi ve sana şunu sordu:

\"{prompt}\"

Aşağıda ürün kataloğumuz var. Eğer bu ürün katalogdaki bir ürüne benziyorsa, benzerliğini ve hangi ortamlarda iyi duracağını açıkla. Eğer benzemiyorsa genel fikir ver:

Ürün kataloğu:
{catalog_text}
"""

        response = model.generate_content([
            full_prompt,
            image
        ])

        return jsonify({"result": response.text})

    except Exception as e:
        
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500

if __name__ == "__main__":
    
    app.run(debug=True)