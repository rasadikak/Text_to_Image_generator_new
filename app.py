from flask import Flask, render_template, request
import requests
import json
import os

app = Flask(__name__)

config_error = None


try:
    with open("config.json") as config_file:
        config = json.load(config_file)
        API_KEY = config.get("API_KEY")
    if not API_KEY:
        config_error = "❌ API Key is missing! Add it to config.json."
except FileNotFoundError:
    config_error = "❌ config.json file not found!"
except json.JSONDecodeError:
    config_error = "❌ config.json is not valid JSON!"

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {API_KEY}"}

@app.route('/', methods=['POST', 'GET'])
def index():
    # show config error immediately if any
    if config_error:
        return render_template("index.html", error_msg=config_error)

    if request.method == 'POST':
        prompt = request.form['prompt']

        if not prompt.strip():
            return render_template("index.html", error_msg="⚠️ Enter a prompt")

        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

            if response.status_code == 200 and "image" in response.headers['Content-Type']:
                if not os.path.exists("static"):
                    os.makedirs("static")

                image_url = "static/generated_image.jpg"
                with open(image_url, "wb") as file:
                    file.write(response.content)

                return render_template("index.html", image_url=image_url, prompt=prompt)
            else:
                return render_template("index.html", error_msg=f"❌ API Error: {response.status_code}")

        except Exception as e:
            return render_template("index.html", error_msg=f"❌ Something went wrong: {e}")

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)