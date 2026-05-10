from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

bot = Bot(token="8370082744:AAEbWKe5ax70u_27M0sUlGG2r1cSmQoypgI")
dp = Dispatcher(bot)

queue = []
pairs = {}
agreed = set()
likes = {}

# /start + правила
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ Я согласен", callback_data="agree"),
        types.InlineKeyboardButton("❌ Выйти", callback_data="exit")
    )

    await message.answer(
        "👋 Добро пожаловать в VIP Chat\n\n"
        "📜 Правила:\n"
        "❗ Не отправляй деньги\n"
        "❗ Не переходи по ссылкам\n"
        "❗ Не делись личными данными\n"
        "❗ Уважай других\n\n"
        "⚠️ Нарушение = блокировка\n\n"
        "Нажми «Я согласен», чтобы продолжить",
        reply_markup=keyboard
    )

# согласие
@dp.callback_query_handler(lambda c: c.data == "agree")
async def agree(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    agreed.add(user_id)

    await bot.send_message(
        user_id,
        "🎉 Отлично!\n\n"
        "💬 Теперь ты можешь искать собеседника\n"
        "👉 Используй /next"
    )

# выход
@dp.callback_query_handler(lambda c: c.data == "exit")
async def exit_user(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, "👋 Пока!")
    

# NEXT — поиск собеседника
@dp.message_handler(commands=['next'])
async def next_chat(message: types.Message):
    user_id = message.from_user.id

    if user_id not in agreed:
        await message.answer("⚠️ Сначала нажми /start и согласись с правилами")
        return

    # разрыв старого чата
    partner = pairs.get(user_id)
    if partner:
        await bot.send_message(partner, "❌ Собеседник вышел из чата")
        del pairs[partner]
        del pairs[user_id]

    # поиск
    if queue:
        partner = queue.pop(0)

        pairs[user_id] = partner
        pairs[partner] = user_id

        await bot.send_message(user_id, "💬 Собеседник найден! Общайтесь")
        await bot.send_message(partner, "💬 Собеседник найден! Общайтесь")

    else:
        queue.append(user_id)
        await message.answer("🔍 Ищем собеседника...\n⏳ Вы в очереди")

# STOP
@dp.message_handler(commands=['stop'])
async def stop_chat(message: types.Message):
    user_id = message.from_user.id

    partner = pairs.get(user_id)

    if partner:
        await bot.send_message(partner, "❌ Собеседник завершил чат")
        del pairs[partner]
        del pairs[user_id]

    if user_id in queue:
        queue.remove(user_id)

    await message.answer("⛔ Вы вышли из VIP Chat")

# лайк система (простая)
@dp.message_handler(commands=['like'])
async def like(message: types.Message):
    user_id = message.from_user.id
    partner = pairs.get(user_id)

    if not partner:
        await message.answer("⚠️ Ты не в чате")
        return

    likes.setdefault(user_id, set()).add(partner)

    if user_id in likes.get(partner, set()):
        await bot.send_message(user_id, "💖 Mutual Match!")
        await bot.send_message(partner, "💖 Mutual Match!")
    else:
        await message.answer("❤️ Лайк отправлен")

executor.start_polling(dp)
