import os
import re
import logging
import traceback
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash
from openai import OpenAI

# Load environment variables
load_dotenv(dotenv_path="full/path/to/.env")

HF_TOKEN = os.getenv("HF_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")

print("HF_TOKEN:", HF_TOKEN[:10], "********")
print("SECRET_KEY:", SECRET_KEY)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI-compatible client via Hugging Face router
try:
    client = OpenAI(
        base_url="https://router.huggingface.co/novita/v3/openai",
        api_key=HF_TOKEN
    )
    logger.info("✅ Novita OpenAI-compatible client initialized successfully.")
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

        # Send message to LLaMA 3.2 model via Novita
        completion = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct",
            messages=[{"role": "user", "content": user_message}],
            timeout=30
        )

        bot_reply = completion.choices[0].message.content.strip()

        # Format reply for HTML
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
