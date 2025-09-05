import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from info import URL, BOT_USERNAME, BIN_CHANNEL, CHANNEL, PROTECT_CONTENT, FSUB, MAX_FILES
from database.users_db import db
from web.utils.file_properties import get_hash
from utils import get_size
from plugins.avbot import av_verification, is_user_allowed, is_user_joined
from Script import script

# ✅ শুধু প্রাইভেট ইউজারদের জন্য অনুমতি
PRIME_USERS = [5926160191]  # <-- এখানে আপনার Prime Users এর আইডি দিন

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio), group=4)
async def private_receive_handler(c: Client, m: Message):
    user_id = m.from_user.id

    # 🔒 Prime User Check
    if user_id not in PRIME_USERS:
        return await m.reply_photo(
            photo="https://i.postimg.cc/mrT4tt5b/IMG-20250905-160239-566.jpg",
            caption=(
                "🚫 **ᴘᴇʀꜱᴏɴᴀʟ ʙᴏᴛ ɴᴏᴛɪᴄᴇ**\n\n"
                "ʏᴏᴜ ᴀʀᴇ ᴀᴛᴛᴇᴍᴘᴛɪɴɢ ᴛᴏ ᴜꜱᴇ ᴀ ʙᴏᴛ ᴛʜᴀᴛ ɪꜱ **ʀᴇꜱᴇʀᴠᴇᴅ ꜰᴏʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇ ᴏɴʟʏ.**\n\n"
                "ʙᴜᴛ ᴅᴏɴ'ᴛ ᴡᴏʀʀʏ ❤️\n"
                "ᴡᴇ ʜᴀᴠᴇ ᴀ **ᴘᴜʙʟɪᴄ ᴠᴇʀꜱɪᴏɴ** ꜰᴏʀ ʏᴏᴜ!\n\n"
                "👉 Use this public bot for your needs:\n"
                "@File_To_Link_Prime_Bot"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🚀 Go To Public Bot", url="https://t.me/File_To_Link_Prime_Bot")]]
            ),
            parse_mode="Markdown"
        )

    # ✅ Force subscription check
    if FSUB and not await is_user_joined(c, m):
        return

    # 🔒 User Ban Check
    is_banned = await db.is_user_blocked(user_id)
    if is_banned:
        await m.reply(
            "🚫 **Yᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ.**\n\n"
            "🔄 **Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪғ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪꜱ ɪꜱ ᴀ ᴍɪꜱᴛᴀᴋᴇ.**\n\n@Prime_Support_Group"
        )
        return

    # ⏳ Free User File Limit
    if not await db.has_premium_access(user_id):
        is_allowed, remaining_time = await is_user_allowed(user_id)
        if not is_allowed:
            await m.reply_text(
                f"🚫 **Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ꜱᴇɴᴛ {MAX_FILES} ғɪʟᴇꜱ!**\n"
                f"Pʟᴇᴀꜱᴇ **{remaining_time} Sᴇᴄᴏɴᴅꜱ** ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ।",
                quote=True
            )
            return

    # 📂 File details
    file_id = m.document or m.video or m.audio
    file_name = file_id.file_name if file_id.file_name else f"PʀɪᴍᴇXBᴏᴛꜱ_{int(time.time())}.mkv"
    file_size = get_size(file_id.file_size)

    if not await db.has_premium_access(user_id):
        verified = await av_verification(c, m)
        if not verified:
            return

    try:
        forwarded = await m.forward(chat_id=BIN_CHANNEL)
        hash_str = get_hash(forwarded)

        stream = f"{URL}watch/{forwarded.id}/PʀɪᴍᴇXBᴏᴛꜱ_{int(time.time())}.mkv?hash={hash_str}"
        download = f"{URL}{forwarded.id}?hash={hash_str}"
        file_link = f"https://t.me/{BOT_USERNAME}?start=file_{forwarded.id}"
        share_link = f"https://t.me/share/url?url={file_link}"

        # ✅ Save file in MongoDB
        await db.files.insert_one({
            "user_id": user_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_id": forwarded.id,
            "hash": hash_str,
            "timestamp": time.time()
        })

        await m.reply_text(
            script.CAPTION_TXT.format(
                CHANNEL,
                file_name,
                file_size,
                stream,
                download,
                file_link
            ),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ꜱᴛʀᴇᴀᴍ •", url=stream),
                    InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download)
                ],
                [
                    InlineKeyboardButton("• ɢᴇᴛ ғɪʟᴇ •", url=file_link),
                    InlineKeyboardButton("• ꜱʜᴀʀᴇ •", url=share_link)
                ],
                [
                    InlineKeyboardButton("• ᴅᴇʟᴇᴛᴇ ғɪʟᴇ •", callback_data=f"deletefile_{forwarded.id}"),
                    InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close_data")
                ]
            ])
        )

    except FloodWait as e:
        await asyncio.sleep(e.value)
        await c.send_message(
            BIN_CHANNEL,
            f"⚠️ FloodWait: {e.value}s from {m.from_user.first_name}"
        )
