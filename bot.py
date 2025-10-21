from telebot import TeleBot, types
import requests
import json
import time
import threading

# ================= CONFIG =================
BOT_TOKEN = "8341825906:AAHfwbdjEP5Jbcs2mkN_ge9HDSnWMqjldOU"
BOT_USERNAME = "osint_info48bot"
bot = TeleBot(BOT_TOKEN)

# ================= CHANNELS & GROUPS =================
PUBLIC_CHANNELS = ["@cyberpan018", "@thawndline"]
PRIVATE_GROUP_LINK = "https://t.me/+I9GuRMAdI2o4YTU1"
OFFICIAL_GROUP_ID = -1003043403619
AUTH_USERS = [7123720124, 5851158054]

# ================= APIs =================
API_NUM = "https://t.taitaninfo.workers.dev/?mobile="
API_VEHICLE = "https://app.turtlemintinsurance.com/api/findregistrationresult?registration="
API_UPI = "https://upi-info-j4tnx-p16k.onrender.com/upi_id="
API_FAM = "https://fampay2number.vercel.app/fam"
API_FAM_KEY = "TrailByDipali"
API_INSTA = "https://instagraminfo.xo.je/api.php?username="
API_IP = "https://ip-info-api-tdmk.onrender.com/ip"
API_EMAIL = "https://flipcartstore.serv00.net/API/InstaBets.php"
API_TG = "https://tg-info-neon.vercel.app/user-details"
API_IFSC = "https://ifsc.razorpay.com/"
API_IMEI = "https://legendxdata.site/Api/imei.php?imei_num="
API_ADHAR = "https://karobetahack.danger-vip-key.shop/api.php?key=HeyBro&aadhar="
API_GST = "https://gstlookup.hideme.eu.org/?gstNumber="
API_LIKE = "https://ff-likex.vercel.app/like?uid="
API_PINCODE = "https://api.postalpincode.in/pincode/"

# ================= MEMORY =================
all_chats = set()
verified_users = set()

# ================= UTILS =================
def sanitize_response_dict(d, extra_remove=None):
    extra_remove = extra_remove or []
    if isinstance(d, dict):
        for k in ["api_owner", "developer", "credit"] + extra_remove:
            d.pop(k, None)

def fetch_api(url, params=None, remove_keys=None, retries=3):
    remove_keys = remove_keys or []
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=15)
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                data = resp.json()
                sanitize_response_dict(data, remove_keys)
                data["developer"] = "@Shatirowner"
                return data
            return {"data": resp.text[:3000], "developer": "@Shatirowner"}
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                return {"data": "not find", "developer": "@Shatirowner", "error": str(e)}
        time.sleep(1)

def send_json_reply(chat_id, user_id, data, first_name=None):
    safe_name = (first_name or "User").replace("]", "").replace("[", "")
    mention = f"[{safe_name}](tg://user?id={user_id})"
    text = f"{mention}\n```\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Use Me Here", url=PRIVATE_GROUP_LINK))
    markup.add(types.InlineKeyboardButton("➕ Add Me to Your Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"))

    try:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    except:
        bot.send_message(chat_id, f"{safe_name}\n{json.dumps(data, indent=2, ensure_ascii=False)}", reply_markup=markup)

# ================= DECORATORS =================
def admin_only(func):
    def wrapper(message):
        if message.from_user.id not in AUTH_USERS:
            bot.reply_to(message, "*Admin Only 💀*", parse_mode="Markdown")
            return
        func(message)
    return wrapper

def verified_only(func):
    def wrapper(message):
        if message.chat.type == "private":
            bot.reply_to(message, "❌ This bot only works in groups.\n➡️ Add me to your group to use all commands.",
                         reply_markup=types.InlineKeyboardMarkup().add(
                             types.InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
                         ))
            return
        func(message)
    return wrapper

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start_cmd(message):
    if message.chat.type == "private":
        bot.reply_to(
            message,
            "👋 Hello!\n❌ This bot only works in groups.\n➡️ Add me to your group to use all commands.",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
            )
        )
        return
    all_chats.add(message.chat.id)
    bot.send_message(message.chat.id, "🎉 Bot is active in this group!")

# ================= VERIFY CALLBACK =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("verify:"))
def handle_verify(call):
    user_id = int(call.data.split(":")[1])
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ This button is for another user.")
        return

    # Check if user joined all channels
    for ch in PUBLIC_CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                bot.answer_callback_query(call.id, "⚠️ You still need to join all channels.")
                return
        except:
            bot.answer_callback_query(call.id, "⚠️ You still need to join all channels.")
            return

    verified_users.add(user_id)
    bot.answer_callback_query(call.id, "✅ Verified successfully!")

    # Send confirmation message to user
    verified_msg = bot.send_message(
        user_id,
        "✅ You are successfully verified! Enjoy now using all commands.",
        parse_mode="Markdown"
    )

    # Send notification in official group
    bot.send_message(
        OFFICIAL_GROUP_ID,
        f"✅ [{call.from_user.first_name}](tg://user?id={user_id}) has successfully verified and joined all channels!",
        parse_mode="Markdown"
    )

    # Delete join request & verified message after 5 seconds
    def delete_messages():
        time.sleep(5)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        try:
            bot.delete_message(user_id, verified_msg.message_id)
        except:
            pass

    threading.Thread(target=delete_messages).start()

# ================= GROUP COMMANDS =================
@bot.message_handler(commands=[
    "num","veh","upiinfo","fam","insta","ip","email","tg","ifsc","adhar","imei","bomber","family",
    "gst","like","pincode"
])
@verified_only
def handle_group_commands(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    chat_id = message.chat.id

    command = message.text.split()[0][1:].lower()
    args = " ".join(message.text.split()[1:])
    if not args:
        bot.reply_to(message, f"Usage: /{command} <argument>")
        return

    data = {}
    try:
        if command == "gst":
            data = fetch_api(API_GST + args, remove_keys=["join"])
        elif command == "like":
            data = fetch_api(API_LIKE + args, remove_keys=["telegram"])
        elif command == "pincode":
            data = fetch_api(API_PINCODE + args)
        elif command == "num":
            data = fetch_api(API_NUM + args)
        elif command == "veh":
            data = fetch_api(API_VEHICLE + args)
        elif command == "upiinfo":
            data = fetch_api(API_UPI + args)
        elif command == "fam":
            data = fetch_api(API_FAM, {"upi_id": args, "key": API_FAM_KEY})
        elif command == "insta":
            data = fetch_api(API_INSTA + args)
        elif command == "ip":
            data = fetch_api(API_IP + args)
        elif command == "email":
            data = fetch_api(API_EMAIL, {"email": args})
        elif command == "tg":
            data = fetch_api(API_TG, {"user": args})
        elif command == "ifsc":
            data = fetch_api(API_IFSC + args)
        elif command == "adhar":
            data = fetch_api(API_ADHAR + args)
        elif command == "imei":
            data = fetch_api(API_IMEI + args)
        elif command == "family":
            data = fetch_api(API_ADHAR + args)
        elif command == "bomber":
            data = fetch_api(API_NUM + args)
            data["note"] = "⚠️ Bombing/harassment disabled"
            sanitize_response_dict(data)
            data["developer"] = "@Shatirowner"
    except:
        data = {"data": "not find", "developer": "@Shatirowner"}

    send_json_reply(chat_id, user_id, data, first_name=first_name)

# ================= BROADCAST SYSTEM =================
@bot.message_handler(commands=["broadcast"])
@admin_only
def handle_broadcast(message):
    text_parts = message.text.split(" ", 1)
    if len(text_parts) < 2:
        bot.reply_to(message, "📢 Usage: /broadcast <your message>")
        return

    broadcast_text = text_parts[1]
    sent, failed = 0, 0

    for chat_id in list(all_chats):
        try:
            bot.send_message(chat_id, f"📢 *Broadcast:*\n{broadcast_text}", parse_mode="Markdown")
            sent += 1
            time.sleep(0.2)
        except:
            failed += 1

    bot.reply_to(message, f"✅ Broadcast sent to {sent} chats.\n❌ Failed: {failed}")

# ================= UNKNOWN COMMAND =================
@bot.message_handler(func=lambda m: True)
def unknown_command_handler(message):
    if message.chat.type == "private":
        bot.reply_to(
            message,
            "❌ This bot only works in groups.\n➡️ Add me to your group to use all commands.",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
            )
        )
        return

    all_chats.add(message.chat.id)
    if message.text and message.text.startswith("/"):
        help_text = (
            "Available commands:\n"
            "📱 /num <mobile_number>\n"
            "🚗 /veh <vehicle_number>\n"
            "💸 /upiinfo <upi_id>\n"
            "🏦 /fam <upi_id>\n"
            "👨‍👩‍👧‍👦 /family <aadhar_number>\n"
            "📸 /insta <username>\n"
            "🌐 /ip <ip_address>\n"
            "📧 /email <email>\n"
            "📨 /tg <userchat id>\n"
            "🏦 /ifsc <ifsc_code>\n"
            "🆔 /adhar <aadhaar_number>\n"
            "📱 /imei <imei_number>\n"
            "📊 /gst <gst_number>\n"
            "❤️ /like <ind> <uid>\n"
            "📍 /pincode { INDIAN POST Bank\n"
        )
        bot.reply_to(message, help_text)

# ================= RUN BOT =================
if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling()
