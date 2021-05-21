import os
import math
import json
import time
import shutil
import heroku3
import requests

from pyrogram import filters
from pyrogram import Client as trojanz
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import Script
from plugins.helpers import humanbytes
from database.filters_mdb import filter_stats
from database.users_mdb import add_user, find_user, all_users


@trojanz.on_message(filters.command(["id"]) & (filters.private | filters.group))
async def showid(client, message):
    chat_type = message.chat.type

    if chat_type == "private":
        user_id = message.chat.id
        await message.reply_text(
            f"Your ID : `{user_id}`",
            parse_mode="md",
            quote=True
        )
    elif (chat_type == "group") or (chat_type == "supergroup"):
        user_id = message.from_user.id
        chat_id = message.chat.id
        if message.reply_to_message:
            reply_id = f"Replied User ID : `{message.reply_to_message.from_user.id}`"
        else:
            reply_id = ""
        await message.reply_text(
            f"Your ID : `{user_id}`\nThis Group ID : `{chat_id}`\n\n{reply_id}",
            parse_mode="md",
            quote=True
        )   


@trojanz.on_message(filters.command(["info"]) & (filters.private | filters.group))
async def showinfo(client, message):
    try:
        cmd, id = message.text.split(" ", 1)
    except:
        id = False
        pass

    if id:
        if (len(id) == 10 or len(id) == 9):
            try:
                checkid = int(id)
            except:
                await message.reply_text("__Enter a valid USER ID__", quote=True, parse_mode="md")
                return
        else:
            await message.reply_text("__Enter a valid USER ID__", quote=True, parse_mode="md")
            return           

        if Config.SAVE_USER == "yes":
            name, username, dcid = await find_user(str(id))
        else:
            try:
                user = await client.get_users(int(id))
                name = str(user.first_name + (user.last_name or ""))
                username = user.username
                dcid = user.dc_id
            except:
                name = False
                pass

        if not name:
            await message.reply_text("__USER Details not found!!__", quote=True, parse_mode="md")
            return
    else:
        if message.reply_to_message:
            name = str(message.reply_to_message.from_user.first_name\
                    + (message.reply_to_message.from_user.last_name or ""))
            id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
            dcid = message.reply_to_message.from_user.dc_id
        else:
            name = str(message.from_user.first_name\
                    + (message.from_user.last_name or ""))
            id = message.from_user.id
            username = message.from_user.username
            dcid = message.from_user.dc_id
    
    if not str(username) == "None":
        user_name = f"@{username}"
    else:
        user_name = "none"

    await message.reply_text(
        f"<b>⚡𝙽𝙰𝙼𝙴</b> : {name}\n\n"
        f"<b>⚡𝚄𝚂𝙴𝚁 𝙸𝙳</b> : <code>{id}</code>\n\n"
        f"<b>⚡𝚄𝚂𝙴𝚁𝙽𝙰𝙼𝙴</b> : {user_name}\n\n"
        f"<b>⚡𝙿𝙴𝚁𝙼𝙰𝙽𝙴𝙽𝚃 𝙻𝙸𝙽𝙺</b> : <a href='tg://user?id={id}'>ᴄʟɪᴄᴋ ʜᴇʀᴇ!</a>\n\n"
        f"<b>⚡𝙳𝙲 𝙸𝙳</b> : {dcid}\n\n",
        quote=True,
        parse_mode="html"
    )


@trojanz.on_message((filters.private | filters.group) & filters.command(["status"]))
async def bot_status(client,message):
    if str(message.from_user.id) not in Config.AUTH_USERS:
        return

    chats, filters = await filter_stats()

    if Config.SAVE_USER == "yes":
        users = await all_users()
        userstats = f"> __**{users} users have interacted with your bot!**__\n\n"
    else:
        userstats = ""

    if Config.HEROKU_API_KEY:
        try:
            server = heroku3.from_key(Config.HEROKU_API_KEY)

            user_agent = (
                'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/80.0.3987.149 Mobile Safari/537.36'
            )
            accountid = server.account().id
            headers = {
            'User-Agent': user_agent,
            'Authorization': f'Bearer {Config.HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
            }

            path = "/accounts/" + accountid + "/actions/get-quota"

            request = requests.get("https://api.heroku.com" + path, headers=headers)

            if request.status_code == 200:
                result = request.json()

                total_quota = result['account_quota']
                quota_used = result['quota_used']

                quota_left = total_quota - quota_used
                
                total = math.floor(total_quota/3600)
                used = math.floor(quota_used/3600)
                hours = math.floor(quota_left/3600)
                minutes = math.floor(quota_left/60 % 60)
                days = math.floor(hours/24)

                usedperc = math.floor(quota_used / total_quota * 100)
                leftperc = math.floor(quota_left / total_quota * 100)

                quota_details = f"""

**🤯Heroku Account Status🤔**

🔰 You have **{total} hours** of free dyno quota available each month.

🔰 Dyno hours used this month__ ;
      🔘 **{usd} hours**  ( {usedperc}% )

🔰⚡ Dyno hours remaining this month__ ;
       🔘 **{hours} hours**  ( {leftperc}% )
       🔘 **Approximately {days} days!**


"""
            else:
                quota_details = ""
        except:
            print("Check your Heroku API key")
            quota_details = ""
    else:
        quota_details = ""

    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - Config.BOT_START_TIME))

    try:
        t, u, f = shutil.disk_usage(".")
        total = humanbytes(t)
        used = humanbytes(u)
        free = humanbytes(f)

        disk = "\n**🤹𝐌𝐘 𝐃𝐈𝐒𝐊 𝐃𝐄𝐓𝐀𝐈𝐋𝐒⚡⚡**\n\n" \
            f"🔘 𝚃𝙾𝚃𝙻𝙴 𝚄𝚂𝙴𝙳  :  {used} / {total}\n" \
            f"🔘 𝙵𝚁𝙴𝙴 𝙾𝙵 :  {free}\n\n"
    except:
        disk = ""

    await message.reply_text(
        "**🔰𝐂𝐔𝐑𝐄𝐂𝐓 𝐒𝐓𝐀𝐓𝐔𝐒 𝐎𝐅 𝐔𝐑𝐒 𝐁𝐎𝐓🔰**\n\n"
        f"> 📂𝚃𝙾𝚃𝙻𝙴 **{filters}** 𝙵𝙸𝙻𝚃𝙴𝚁 𝙰𝙲𝚁𝙾𝚂𝙴 **{chats}** 𝙲𝙷𝙰𝚃𝚂\n\n"
        f"{userstats}"
        f"> ⚡𝐁𝐎𝐓'𝐒 𝐔𝐏𝐓𝐈𝐌𝐄: **{uptime}**\n\n"
        f"{quota_details}"
        f"{disk}",
        quote=True,
        parse_mode="md"
    )


@trojanz.on_message(filters.command(["start"]) & filters.private)
async def start(client, message):
    await message.reply_text(
        text=Script.START_MSG.format(message.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⚡𝘾𝙍𝙀𝘼𝙏𝙀𝙍/𝙁𝙐𝙉𝘿𝙀𝙍 🤓", url="https://t.me/Deeks_04_8")],
                    [
                        InlineKeyboardButton("💡 𝙷𝙴𝙻𝙿", callback_data="help_data"),
                        InlineKeyboardButton("🤹 𝙰𝙱𝙾𝚄𝚃 𝙼𝙴", callback_data="about_data"),
                    ],
                    [
                        InlineKeyboardButton(
                            "🎖️ 𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐀𝐋𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 🎖️", url="https://t.me/UNI_MOVIES_BOX")
                    ]
            ]
        ),
        reply_to_message_id=message.message_id
    )
    if Config.SAVE_USER == "yes":
        try:
            await add_user(
                str(message.from_user.id),
                str(message.from_user.username),
                str(message.from_user.first_name + " " + (message.from_user.last_name or "")),
                str(message.from_user.dc_id)
            )
        except:
            pass


@trojanz.on_message(filters.command(["help"]) & filters.private)
async def help(client, message):
    await message.reply_text(
        text=Script.HELP_MSG,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🎖️JOIN OURS ALL CHANNELS🎖️", url="https://t.me/UNI_MOVIES_BOX")],
                 [   InlineKeyboardButton("🤓𝙰𝙱𝙾𝚄𝚃 𝙼𝙴", callback_data="about_data")
                ],
                [
                    InlineKeyboardButton("📽️𝙹𝙾𝙸𝙽 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", url="https://t.me/joinchat/cfs6r6VwHfo2NDk1"),
                    InlineKeyboardButton("🏅𝙹𝙾𝙸𝙽 𝙶𝚁𝙾𝚄𝙿", url="https://t.me/UM_Requests")
                ]
            ]
        ),
        reply_to_message_id=message.message_id
    )


@trojanz.on_message(filters.command(["about"]) & filters.private)
async def about(client, message):
    await message.reply_text(
        text=Script.ABOUT_MSG,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👑𝙵𝚄𝙽𝙳𝙴𝚁/𝙲𝚁𝙴𝙰𝚃𝙴𝚁", url="https://t.me/Deeks_04_8")
                        

                ],
                [
                    InlineKeyboardButton("⏪𝙶𝙾 𝙱𝙰𝙲𝙺", callback_data="help_data"),
                    InlineKeyboardButton("📴 𝙲𝙻𝙾𝚂𝙴 𝙰𝙻𝙻", callback_data="close_data"),
                ]                
            ]
        ),
        reply_to_message_id=message.message_id
    )
