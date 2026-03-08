from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from gpt import gpt_service
from util import load_message, load_prompt, get_image_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gpt_service.message_list.clear()
    msg = update.message if update.message else update.callback_query.message
    await msg.reply_photo(photo=open(get_image_path('avatar_main.jpg'), 'rb'), caption=load_message('main'))

async def gpt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'gpt'
    gpt_service.set_prompt(load_prompt('gpt'))
    await update.message.reply_photo(photo=open(get_image_path('gpt.jpg'), 'rb'), caption=load_message('gpt'))

async def talk_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ніцше 🧠", callback_data='talk_nietzsche')],
        [InlineKeyboardButton("Хокінг 🌌", callback_data='talk_hawking')],
        [InlineKeyboardButton("Кобейн 🎸", callback_data='talk_cobain')],
        [InlineKeyboardButton("Толкін 🧙‍♂️", callback_data='talk_tolkien')]
    ]
    await update.message.reply_photo(photo=open(get_image_path('talk.jpg'), 'rb'), caption=load_message('talk'), reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # Повернення в головне меню
    if data == 'start':
        await start(update, context)

    # Логіка персонажів (Talk)
    elif data.startswith('talk_'):
        context.user_data['mode'] = 'talk'
        # ОЧИЩЕННЯ: Викликаємо set_prompt, який видаляє минулі повідомлення
        gpt_service.set_prompt(load_prompt(data))

        await query.message.reply_photo(
            photo=open(get_image_path(f"{data}.jpg"), 'rb'),
            caption="Курт на зв'язку. Про що поговоримо?"
        )

    # Логіка перекладача (вибір мови)
    elif data.startswith('lang_'):
        context.user_data['mode'] = 'translate'
        context.user_data['target_lang'] = "English" if "en" in data else "German"
        lang_str = "англійську 🇺🇸" if "en" in data else "німецьку 🇩🇪"
        await query.message.reply_text(f"Чудово! Напишіть текст, і я перекладу його на {lang_str}")

    # Логіка квізу (вибір теми та генерація питання)
    elif data.startswith('quiz_'):
        context.user_data['mode'] = 'quiz'
        topic = "програмування" if "prog" in data else "історію"

        # 1. Встановлюємо системний промпт (правила гри)
        gpt_service.set_prompt(load_prompt('quiz'))

        # 2. Додаємо конкретну інструкцію для генерації питання (ОСЬ ЦЕЙ РЯДОК):
        gpt_service.add_message(
            f"Напиши одне цікаве коротке питання про {topic} з трьома варіантами відповіді (A, B, C). Не пиши відповідь одразу.")

        # 3. Отримуємо питання від GPT-5-mini
        question = await gpt_service.send_message_list()

        # 4. Надсилаємо результат користувачу
        await query.message.reply_text(f"✨ Тема: {topic.capitalize()}\n\n{question}")
    elif data == 'random':
        from bot import random_fact  # імпортуємо, щоб уникнути циклічності, якщо треба
        await random_fact(update, context)

# --- ОБРОБНИК ТЕКСТУ (ОНОВЛЕНИЙ) ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    user_text = update.message.text

    # 1. Режим ПЕРЕКЛАДАЧА (згідно з ТЗ)
    if mode == 'translate':
        target_lang = context.user_data.get('lang', 'English')

        # Скидаємо промпт для кожного перекладу
        gpt_service.set_prompt(f"Ти професійний перекладач. Переклади текст на {target_lang}. Пиши ТІЛЬКИ переклад.")
        gpt_service.add_message(user_text)

        ans = await gpt_service.send_message_list()

        # Кнопки згідно з ТЗ: зміна мови та закінчити (повернення в /start)
        keyboard = [
            [InlineKeyboardButton("Змінити мову 🔄", callback_data='translate_cmd')],
            [InlineKeyboardButton("Закінчити ❌", callback_data='start')]
        ]

        await update.message.reply_text(ans, reply_markup=InlineKeyboardMarkup(keyboard))

    # 2. Режим КВІЗУ
    elif mode == 'quiz':
        gpt_service.add_message(
            f"Користувач відповів: '{user_text}'. Це правильно? Напиши 'Так' або 'Ні' і дай коротке пояснення."
        )
        result = await gpt_service.send_message_list()

        keyboard = [
            [InlineKeyboardButton("Наступне питання ➡️", callback_data='quiz_prog')],
            [InlineKeyboardButton("В меню 🏠", callback_data='start')]
        ]
        await update.message.reply_text(result, reply_markup=InlineKeyboardMarkup(keyboard))

    # 3. Режим звичайного GPT або ТАЛК (Персонажі)
    else:
        gpt_service.add_message(user_text)
        ans = await gpt_service.send_message_list()
        await update.message.reply_text(ans)


async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query: await query.answer()

    # 1. Налаштовуємо ШІ через промпт з файлу prompts/random.txt
    gpt_service.set_prompt(load_prompt('random'))
    gpt_service.add_message("Напиши один цікавий короткий факт.")

    # 2. Отримуємо факт від gpt-5-mini
    fact = await gpt_service.send_message_list()

    # 3. Формуємо кнопки
    keyboard = [
        [InlineKeyboardButton("Хочу ще факт 🎲", callback_data='random')],
        [InlineKeyboardButton("В меню 🏠", callback_data='start')]
    ]

    # 4. Відправляємо фото random.jpg та текст із messages/random.txt + сам факт
    msg = query.message if query else update.message
    await msg.reply_photo(
        photo=open(get_image_path('random.jpg'), 'rb'),
        caption=f"{load_message('random')}\n\n{fact}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'translate'
    keyboard = [
        [InlineKeyboardButton("Англійська 🇺🇸", callback_data='lang_en')],
        [InlineKeyboardButton("Німецька 🇩🇪", callback_data='lang_de')],
        [InlineKeyboardButton("В меню 🏠", callback_data='start')]
    ]
    # Використовуємо картинку message.jpg або dog_5.jpg
    await update.message.reply_photo(
        photo=open(get_image_path('message.jpg'), 'rb'),
        caption=load_message('translate'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'quiz'
    context.user_data['score'] = 0
    keyboard = [
        [InlineKeyboardButton("Програмування 💻", callback_data='quiz_prog')],
        [InlineKeyboardButton("Історія 🏛", callback_data='quiz_hist')],
        [InlineKeyboardButton("В меню 🏠", callback_data='start')]
    ]
    await update.message.reply_photo(
        photo=open(get_image_path('quiz.jpg'), 'rb'),
        caption=load_message('quiz'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def image_analysis_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'image'
    await update.message.reply_photo(
        photo=open(get_image_path('gpt.jpg'), 'rb'),
        caption="🖼 **Режим розпізнавання фото**\n\nНадішліть мені будь-яке зображення, і я розповім, що на ньому!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Завантажуємо фото
    file = await update.message.photo[-1].get_file()
    image_bytes = await file.download_as_bytearray()

    status = await update.message.reply_text("🔎 Вивчаю ваше фото...")

    # Викликаємо метод аналізу з gpt.py (який ми прописували раніше)
    description = await gpt_service.send_image_analysis(bytes(image_bytes), "Що на цьому фото?")

    await status.edit_text(description)