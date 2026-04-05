import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
TELEGRAM_TOKEN = "8724845773:AAE7yBdsnQTXIDjf6TgCThXJBNFz5HXuNYk"
client = OpenAI()

# Dictionary to store user's selection state
user_data = {}

# Expanded Languages List (11 Languages)
LANGUAGES = {
    "🇲🇲 Burmese": "Burmese",
    "🇺🇸 English": "English",
    "🇨🇳 Chinese": "Chinese",
    "🇹🇭 Thai": "Thai",
    "🇯🇵 Japanese": "Japanese",
    "🇰🇷 Korean": "Korean",
    "🇻🇳 Vietnamese": "Vietnamese",
    "🇲🇾 Malay": "Malay",
    "🇫🇷 French": "French",
    "🇩🇪 German": "German",
    "🇷🇺 Russian": "Russian"
}

def get_lang_keyboard():
    keys = list(LANGUAGES.keys())
    # Arrange buttons in 3 columns for better layout
    keyboard = []
    for i in range(0, len(keys), 3):
        row = [KeyboardButton(k) for k in keys[i:i+3]]
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the language selection process with a professional welcome message."""
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "selecting_source"}
    
    welcome_text = (
        "🌐 *SWB-Translator မှ ကြိုဆိုပါတယ်!* 🌐\n\n"
        "ကျွန်တော်ကတော့ ကမ္ဘာတစ်ဝှမ်းရှိ ဘာသာစကားများကို အပြန်အလှန် "
        "အကောင်းဆုံး ဘာသာပြန်ပေးမယ့် Bot တစ်ခုဖြစ်ပါတယ်။\n\n"
        "📍 အရင်ဆုံး ဘယ်ဘာသာစကား *မှ* ပြန်မှာလဲဆိုတာကို ရွေးပေးပါ။ (Source Language)"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_lang_keyboard(), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection and translation."""
    user_text = update.message.text
    user_id = update.effective_user.id

    if not user_text:
        return

    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {"step": "selecting_source"}

    state = user_data[user_id]

    # Step 1: Selecting Source Language
    if state["step"] == "selecting_source":
        if user_text in LANGUAGES:
            user_data[user_id]["source"] = LANGUAGES[user_text]
            user_data[user_id]["source_label"] = user_text
            user_data[user_id]["step"] = "selecting_target"
            await update.message.reply_text(
                f"✅ Source: *{user_text}*\n\n📍 အခု ဘယ်ဘာသာစကား *သို့* ပြန်မှာလဲဆိုတာကို ရွေးပေးပါ။ (Target Language)",
                reply_markup=get_lang_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("ကျေးဇူးပြု၍ အောက်က ခလုတ်ထဲမှ ဘာသာစကားတစ်ခုကို ရွေးပေးပါ။", reply_markup=get_lang_keyboard())
        return

    # Step 2: Selecting Target Language
    if state["step"] == "selecting_target":
        if user_text in LANGUAGES:
            if LANGUAGES[user_text] == state["source"]:
                await update.message.reply_text("⚠️ Source နဲ့ Target ဘာသာစကား တူလို့မရပါဘူး။ အခြားတစ်ခု ထပ်ရွေးပေးပါ။")
                return
            
            user_data[user_id]["target"] = LANGUAGES[user_text]
            user_data[user_id]["target_label"] = user_text
            user_data[user_id]["step"] = "ready"
            
            ready_keyboard = ReplyKeyboardMarkup([
                [KeyboardButton("🔄 ဘာသာစကား ပြန်ပြောင်းရန်")],
                [KeyboardButton("🔄 Source နဲ့ Target ပြောင်းရန်")]
            ], resize_keyboard=True)
            
            await update.message.reply_text(
                f"✨ *{state['source_label']}* ➔ *{user_text}* ✨\n\n"
                "ဘာသာပြန်ဖို့ အဆင်သင့်ဖြစ်ပါပြီ။ ဘာသာပြန်ချင်တဲ့ စာသားကို အခု ပေးပို့နိုင်ပါပြီ။",
                reply_markup=ready_keyboard,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("ကျေးဇူးပြု၍ အောက်က ခလုတ်ထဲမှ ဘာသာစကားတစ်ခုကို ရွေးပေးပါ။", reply_markup=get_lang_keyboard())
        return

    # Handle Special Buttons
    if user_text == "🔄 ဘာသာစကား ပြန်ပြောင်းရန်":
        await start(update, context)
        return
    
    if user_text == "🔄 Source နဲ့ Target ပြောင်းရန်":
        old_source = user_data[user_id]["source"]
        old_source_label = user_data[user_id]["source_label"]
        user_data[user_id]["source"] = user_data[user_id]["target"]
        user_data[user_id]["source_label"] = user_data[user_id]["target_label"]
        user_data[user_id]["target"] = old_source
        user_data[user_id]["target_label"] = old_source_label
        
        await update.message.reply_text(
            f"✅ အခု *{user_data[user_id]['source_label']}* ➔ *{user_data[user_id]['target_label']}* သို့ ပြောင်းလဲလိုက်ပါပြီ။\n\n"
            "ဘာသာပြန်ချင်တဲ့ စာသားကို ပေးပို့နိုင်ပါပြီ။",
            parse_mode="Markdown"
        )
        return

    # Step 3: Translation
    if state["step"] == "ready":
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        translated_text = await translate_text_ai(user_text, state["source"], state["target"])
        await update.message.reply_text(translated_text)
    else:
        await start(update, context)

async def translate_text_ai(text: str, source: str, target: str) -> str:
    """Translate text using OpenAI GPT-4.1-mini."""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": (
                    f"You are a professional translator. Translate the following text from {source} to {target}. "
                    "Provide only the translated text without any explanations or notes. "
                    "Ensure the translation is natural, accurate, and culturally appropriate."
                )},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "စိတ်မရှိပါနဲ့၊ ဘာသာပြန်တဲ့နေရာမှာ အမှားတစ်ခုရှိသွားလို့ပါ။ ခဏနေမှ ပြန်ကြိုးစားကြည့်ပေးပါ။"

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting with more languages and better welcome message...")
    application.run_polling()
