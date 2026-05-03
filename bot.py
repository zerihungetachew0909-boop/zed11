import os
import logging
import pdfplumber
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# Store user PDFs
user_pdfs = {}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 Mee jalqaba PDF faayilaa keessan ergaa (hanga 10)"
    )
    user_pdfs[update.effective_user.id] = []

# HANDLE PDF UPLOAD
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_pdfs:
        user_pdfs[user_id] = []

    if len(user_pdfs[user_id]) >= 10:
        await update.message.reply_text("⚠️ PDF 10 guuttee jirta. Amma maqaa galchi.")
        return

    file = await update.message.document.get_file()
    file_path = f"{user_id}_{len(user_pdfs[user_id])}.pdf"
    await file.download_to_drive(file_path)

    user_pdfs[user_id].append(file_path)

    await update.message.reply_text("✅ PDF galmeeffame")

    if len(user_pdfs[user_id]) == 10:
        await update.message.reply_text("🔍 Amma maqaa barbaaddu galchi")

# HANDLE NAME SEARCH
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.message.text.lower()

    if user_id not in user_pdfs or len(user_pdfs[user_id]) == 0:
        await update.message.reply_text("📄 Mee dura PDF ergi")
        return

    found = False

    for pdf_file in user_pdfs[user_id]:
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and name in text.lower():
                        found = True
                        break
            if found:
                break
        except:
            continue

    if found:
        await update.message.reply_text("✅ Passportiin keessan baheeraa")
    else:
        await update.message.reply_text("❌ Passportiin keessan hin bane")

# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()