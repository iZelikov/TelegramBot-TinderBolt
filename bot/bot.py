from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *
from secrets import *

# Создайте файл secrets.py и добавьте туда ваши токены:
"""
GPT_TOKEN = 'Ваш_токен_от_GPT'
GPT_BASE_URL = 'Base_url_для_вашего_GPT'
BOT_TOKEN = 'Ваш_токен_от_TelegramBot'
"""


# тут будем писать наш код :)
async def hello(update, context):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'date':
        await date_dialog(update, context)
    elif dialog.mode == 'message':
        await message_dialog(update, context)
    elif dialog.mode == 'profile':
        await profile_dialog(update, context)
    elif dialog.mode == 'opener':
        await opener_dialog(update, context)
    else:
        first_name = update.message.chat.first_name
        user_name = '@'+update.message.chat.username

        name = first_name or user_name
        text = update.message.text
        await send_photo(update, context, 'avatar_main')
        await send_text(update, context, f'Привет *{name}*')
        await send_text(update, context, f'Вы только что написали: _{text}_')
        await send_text(update, context, f'Вместо этого лучше выберите одну из команд в *Меню*')


async def hello_buttons(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_text(update, context, f'Зафиксировано нажатие на кнопку *{query.upper()}*')


async def start(update, context):
    dialog.mode = 'main'
    text = load_message('main')
    await send_photo(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'главное меню бота',
        'profile': 'генерация Tinder-профля 😎',
        'opener': 'сообщение для знакомства 🥰',
        'message': 'переписка от вашего имени 😈',
        'date': 'переписка со звездами 🔥',
        'gpt': 'задать вопрос чату GPT 🧠'
    })


async def gpt(update, context):
    dialog.mode = 'gpt'
    dialog.prompt = None
    text = load_message('gpt')
    await send_photo(update, context, 'gpt')
    await send_text(update, context, text)


async def gpt_dialog(update, context):
    if dialog.prompt is None:
        dialog.prompt = load_prompt('gpt')
    query_text = update.message.text
    my_message = await send_text(update, context, '_GPT отвечает..._')
    answer = await chatgpt.send_question(dialog.prompt, query_text)
    dialog.prompt += '\nВопрос пользователя:\n' + query_text + '\nОтвет системы:\n' + answer
    await  my_message.edit_text(answer)


async def date(update, context):
    dialog.mode = 'date'
    text = load_message('date')
    await send_photo(update, context, 'date')
    await send_text_buttons(update, context, text, {
        'date_grande': 'Ариана Гранде',
        'date_robbie': 'Марго Робби',
        'date_zendaya': 'Зендея',
        'date_gosling': 'Райан Гослинг',
        'date_hardy': 'Том Харди'
    })


async def date_buttons(update, context):
    query = update.callback_query.data
    dialog.prompt = load_prompt(query)
    chatgpt.set_prompt(dialog.prompt)
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, 'Отличный выбор! Начинайте соблазнение в чате!')


async def date_dialog(update, context):
    query_text = update.message.text
    my_message = await send_text(update, context, '_звезда думает..._')
    answer = await chatgpt.add_message(query_text)
    await  my_message.edit_text(answer)


async def message(update, context):
    dialog.mode = 'message'
    text = load_message('message')
    await send_photo(update, context, 'message')
    await send_text_buttons(update, context, text, {
        'message_next': 'Следующее сообщение',
        'message_date': 'Пригласить на свидание',
    })
    dialog.list.clear()


async def message_buttons(update, context):
    query = update.callback_query.data
    dialog.prompt = load_prompt(query)
    chatgpt.set_prompt(dialog.prompt)
    user_chat_history = "\n\n".join(dialog.list)
    await update.callback_query.answer()
    my_message = await send_text(update, context, '_ИИ пишет ответ..._')
    answer = await chatgpt.add_message(user_chat_history)
    dialog.list.append(answer)
    await my_message.edit_text(answer)


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def profile(update, context):
    dialog.mode = 'profile'
    text = load_message('profile')
    await send_photo(update, context, 'profile')
    await send_text(update, context, text)
    dialog.count = 0
    dialog.user.clear()
    await send_text(update, context, dialog.profile_questions[dialog.count][1])


async def profile_dialog(update, context):
    if dialog.count < len(dialog.profile_questions):
        text = update.message.text
        dialog.user[dialog.profile_questions[dialog.count][0]] = text
        dialog.count += 1
        if dialog.count < len(dialog.profile_questions):
            await send_text(update, context, dialog.profile_questions[dialog.count][1])
        else:
            dialog.mode = 'main'
            user_info = dialog_user_info_to_str(dialog.user)
            dialog.prompt = load_prompt('profile')
            chatgpt.set_prompt(dialog.prompt)
            my_message = await send_text(update, context, '_Генерируем профиль..._')
            answer = await chatgpt.add_message(user_info)
            await my_message.edit_text(answer)


async def opener(update, context):
    dialog.mode = 'opener'
    text = load_message('opener')
    await send_photo(update, context, 'opener')
    await send_text(update, context, text)
    dialog.count = 0
    dialog.user.clear()
    await send_text(update, context, dialog.opener_questions[dialog.count][1])


async def opener_dialog(update, context):
    if dialog.count < len(dialog.opener_questions):
        text = update.message.text
        dialog.user[dialog.opener_questions[dialog.count][0]] = text
        dialog.count += 1
        if dialog.count < len(dialog.opener_questions):
            await send_text(update, context, dialog.opener_questions[dialog.count][1])
        else:
            dialog.mode = 'main'
            user_info = dialog_user_info_to_str(dialog.user)
            dialog.prompt = load_prompt('opener')
            chatgpt.set_prompt(dialog.prompt)
            my_message = await send_text(update, context, '_Генерируем опенер..._')
            answer = await chatgpt.add_message(user_info)
            await my_message.edit_text(answer)


dialog = Dialog()
dialog.mode = 'main'
dialog.prompt = None
dialog.list = []
dialog.count = 0
dialog.user = {}
dialog.profile_questions = [
    ('name', 'Как вас зовут?'),
    ('age', 'Сколько вам лет?'),
    ('occupation', 'кем вы работаете?'),
    ('hobby', 'У вас есть хобби?'),
    ('annoys', 'Что вас раздражает в людях?'),
    ('goals', 'Цели знакомства?'),
]

dialog.opener_questions = [
    ('name', 'Имя девушки?'),
    ('age', 'Сколько ей лет?'),
    ('handsome', 'Оцените внешность: 1-10 баллов?'),
    ('occupation', 'Кем она работает?'),
    ('city', 'Из какого она города?'),
    ('goals', 'Цели знакомства?'),
]

chatgpt = ChatGptService(GPT_BASE_URL, GPT_TOKEN)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('date', date))
app.add_handler(CommandHandler('message', message))
app.add_handler(CommandHandler('profile', profile))
app.add_handler(CommandHandler('opener', opener))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CallbackQueryHandler(date_buttons, pattern='^date_.*'))
app.add_handler(CallbackQueryHandler(message_buttons, pattern='^message_.*'))
app.add_handler(CallbackQueryHandler(hello_buttons))

app.run_polling()
