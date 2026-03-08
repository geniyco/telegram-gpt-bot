from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from credentials import TELEGRAM_TOKEN
from bot import start, gpt_cmd, talk_cmd, button_handler, handle_text, quiz_cmd, translate_cmd, handle_photo, image_analysis_cmd
import logging
from credentials import TELEGRAM_TOKEN

async def set_commands(app):
    commands = [
        BotCommand("start", "🏠 Головне меню"),
        BotCommand("random", "🎲 Випадковий факт"),
        BotCommand("gpt", "🤖 Питання ChatGPT"),
        BotCommand("talk", "👤 Діалог з особистістю"),
        BotCommand("quiz", "❓ Квіз (вікторина)"),
        BotCommand("translate", "🇺🇸 Перекладач"),
        BotCommand("image", "🖼 Розпізнавання фото")
    ]
    await app.bot.set_my_commands(commands)
if __name__ == '__main__':

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.post_init = set_commands


    from bot import start, gpt_cmd, talk_cmd, quiz_cmd, translate_cmd, random_fact, button_handler, handle_text

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_fact))
    app.add_handler(CommandHandler("gpt", gpt_cmd))
    app.add_handler(CommandHandler("talk", talk_cmd))
    app.add_handler(CommandHandler("quiz", quiz_cmd))
    app.add_handler(CommandHandler("translate", translate_cmd))
    app.add_handler(CommandHandler("image", image_analysis_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("🚀 Бот запущений з повним меню команд!")
    app.run_polling()