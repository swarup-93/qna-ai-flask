import re
import os
import logging
import traceback
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash
from huggingface_hub import InferenceClient

load_dotenv(dotenv_path="full/path/to/.env")  

HF_TOKEN = os.getenv("HF_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")

print("HF_TOKEN:", HF_TOKEN)
print("SECRET_KEY:", SECRET_KEY)

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Replace with a secure key in production

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Hugging Face Inference Client
try:
    client = InferenceClient(
        model="HuggingFaceH4/zephyr-7b-beta",
        token=HF_TOKEN
    )
    logger.info("✅ Hugging Face client initialized successfully.")
except Exception as e:
    logger.error(f"❌ Failed to initialize client: {e}")
    client = None

@app.route("/chat")
def index():
    return render_template("index.html")

@app.route("/reply", methods=["POST"])
def reply():
    try:
        if client is None:
            flash("❌ Chat service is unavailable. Please try again later.")
            return render_template("index.html")

        user_message = request.form.get("message_input", "").strip()

        if not user_message:
            flash("⚠️ Please enter a message.")
            return render_template("index.html")

        logger.info(f"📝 User: {user_message}")

        # Format the prompt (Zephyr supports instruction-style input)
        prompt = f"<|system|>\nYou are a helpful assistant.\n<|user|>\n{user_message}\n<|assistant|>"

        # Get response from HF API
        response = client.text_generation(
            prompt=prompt,
            max_new_tokens=250,
            do_sample=True,
            temperature=0.7
        )

        bot_reply = response.strip()

        # Format for HTML
        formatted_reply = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", bot_reply)
        formatted_reply = formatted_reply.replace("\n\n", "<br><br>").replace("\n", "<br>")

        flash(f"You: {user_message}")
        flash(f"Assistant: {formatted_reply}")

        return render_template("index.html")

    except Exception as e:
        logger.error(f"💥 Error in /reply: {e}")
        logger.error(traceback.format_exc())
        flash(f"❌ An error occurred: {str(e)}")
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
