import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from database import set_language, get_language
from languages import texts
from movies import movies

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = [(os.getenv("CHANNEL_USERNAME"), os.getenv("CHANNEL_LINK"))]
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ✅ Obuna tekshirish
async def check_subscriptions(user_id):
    for channel, _ in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

# ✅ Obuna tugmasi
def subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 Venus Kino", url="https://t.me/venuskino/5")]
    ])

# ✅ Til tanlash menyusi
def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])
    
# log qilish
def log_user(message: types.Message):
    user = message.from_user
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    username = f"@{user.username}" if user.username else "@yoq"
    line = f"Ism: {user.first_name} | Username: {username} | ID: {user.id} | Sana: {timestamp}\n"
    with open("users.txt", "a", encoding="utf-8") as f:
        f.write(line)

# ✅ /start komandasi
@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscriptions(user_id):
        await message.answer("📢 Iltimos, botimizdan foydalanish uchun kanalimizga obuna bo‘ling:", reply_markup=subscription_keyboard())
        return
    await message.answer("🇺🇿 Tilni tanlang / Выберите язык / Choose language", reply_markup=language_keyboard())

# ✅ Til tanlash callback
@dp.callback_query(F.data.startswith("lang_"))
async def handle_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    set_language(user_id, lang)
    await callback.message.answer(texts["language_selected"][lang])
    await callback.message.answer(texts["send_movie_code"][lang])

# ✅ Admin video yuborsa file_id qaytariladi
@dp.message(F.video)
async def get_file_id(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        file_id = message.video.file_id
        await message.answer(f"🎥 Kino fayl kodi:\n<code>{file_id}</code>")
    else:
        await message.answer("⛔ Siz admin emassiz.")

# ✅ /users komandasi (adminlar uchun)
@dp.message(F.text == "/users")
async def show_users(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ Bu buyruq faqat adminlar uchun!")

    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            data = f.read()
        if not data:
            await message.answer("📂 Hozircha hech kim botdan foydalanmagan.")
        else:
            await message.answer(f"📋 Foydalanuvchilar ro‘yxati:\n\n{data[:4090]}")
    except FileNotFoundError:
        await message.answer("❌ users.txt topilmadi.")

# ✅ Kino kodi yuborilganda
@dp.message(F.text)
async def handle_movie_code(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscriptions(user_id):
        await message.answer("📢 Iltimos, kanalga obuna bo‘ling:", reply_markup=subscription_keyboard())
        return

    log_user(message)
    lang = get_language(user_id)
    code = message.text.lower()

    
    

if code in movies:
    await message.answer(f"🎬 {movies[code]['title']}")
    await bot.send_video(
        chat_id=message.chat.id,
        video=movies[code]['file_id'],
        protect_content=True
    )

        await bot.send_video(chat_id=message.chat.id, video=movies[code]['file_id'])  # ✅ to‘g‘ri


    else:
        await message.answer("❌ Bunday kino topilmadi.")

#  Botni ishga tushurish
async def main():
    print("muammo bor✅")
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())
