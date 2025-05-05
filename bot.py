import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes, ConversationHandler
)

# Load .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Produk
produk_list = [
    {"id": "1", "nama": "✨ Premium 1 Bulan", "harga": 54000},
    {"id": "2", "nama": "🌟 Premium 3 Bulan", "harga": 200000},
    {"id": "3", "nama": "💎 Premium 6 Bulan", "harga": 400000},
    {"id": "4", "nama": "🏆 Premium 12 Bulan", "harga": 5000000}
]

# Metode pembayaran
metode_pembayaran = [
    {"nama": "QRIS", "detail": "https://link-qris-kamu"},
    {"nama": "DANA", "detail": "08558827668 a.n @serpagengs"},
    {"nama": "Gopay", "detail": "083170123771 a.n @serpagengs"},
    {"nama": "Bank BCA", "detail": "5940804673 a.n @serpagengs"}
]

# State Conversation
(
    PILIH_BULAN, KONFIRMASI, METODE_BAYAR, KIRIM_BUKTI,
    INPUT_NOHP, INPUT_OTP, INPUT_VERIFIKASI
) = range(7)

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = (
        "👑 𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝑺𝒓𝒑𝒂𝑷𝒓𝒆𝒎 👑\n\n"
        "✨ 𝐓𝐄𝐋𝐄𝐏𝐑𝐄𝐌 𝐌𝐔𝐑𝐀𝐇 & 𝐓𝐄𝐑𝐏𝐄𝐑𝐂𝐀𝐘𝐀 ✨\n\n"
        "🛒 𝘔𝘢𝘶 𝘣𝘦𝘭𝘪 𝘛𝘌𝘓𝘌𝘗𝘙𝘌𝘔 𝘥𝘦𝘯𝘨𝘢𝘯 𝘩𝘢𝘳𝘨𝘢 𝘣𝘦𝘳𝘴𝘢𝘩𝘢𝘣𝘢𝘵?\n"
        "✅ 𝙃𝙖𝙧𝙜𝙖 𝙈𝙪𝙧𝙖𝙝\n"
        "✅ 𝙋𝙧𝙤𝙨𝙚𝙨 𝘾𝙚𝙥𝙖𝙩\n"
        "✅ 𝙏𝙖𝙣𝙥𝙖 𝙍𝙞𝙗𝙚𝙩\n"
        "✅ 𝙎𝙪𝙙𝙖𝙝 𝙏𝙚𝙧𝙗𝙪𝙠𝙩𝙞 𝙏𝙧𝙪𝙨𝙩𝙚𝙙\n\n"
        "📩 𝑶𝒓𝒅𝒆𝒓 𝒔𝒆𝒌𝒂𝒓𝒂𝒏𝒈, 𝒋𝒂𝒏𝒈𝒂𝒏 𝒕𝒖𝒏𝒈𝒈𝒖 𝒃𝒆𝒔𝒐𝒌!\n"
    )
    teks += "📦 Daftar Produk:\n\n"
    for p in produk_list:
        teks += f"{p['id']}. {p['nama']} - Rp {p['harga']:,} ✨\n"

    keyboard = [
        [InlineKeyboardButton("🛒 Beli Disini", callback_data="beli")],
        [InlineKeyboardButton("📞 CS", url="t.me/serpagengs"),
         InlineKeyboardButton("📣 Testi", url="t.me/srpatesti")]
    ]
    await update.message.reply_text(teks, reply_markup=InlineKeyboardMarkup(keyboard))
    return PILIH_BULAN

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "beli":
        keyboard = [[InlineKeyboardButton(p["nama"], callback_data=f"beli_{p['id']}")] for p in produk_list]
        keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="start")])
        await query.edit_message_text("Pilih paket premium yang ingin dibeli:", reply_markup=InlineKeyboardMarkup(keyboard))
        return KONFIRMASI

    elif data == "cs" or data == "testi":
        return PILIH_BULAN

    elif data == "start":
        return await start(update, context)

    elif data.startswith("beli_"):
        produk_id = data.split("_")[1]
        produk = next((p for p in produk_list if p["id"] == produk_id), None)
        if not produk:
            await query.edit_message_text("Produk tidak ditemukan.")
            return ConversationHandler.END
        user_data_store[query.from_user.id] = {"produk": produk}
        text = f"🛍️ {produk['nama']}\nHarga: Rp {produk['harga']:,}"
        buttons = [
            [InlineKeyboardButton("✅ Konfirmasi", callback_data="konfirmasi_produk")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="beli")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        return METODE_BAYAR

    elif data == "konfirmasi_produk":
        buttons = [[InlineKeyboardButton(p["nama"], callback_data=f"metode_{i}")] for i, p in enumerate(metode_pembayaran)]
        buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="beli")])
        await query.edit_message_text("Pilih metode pembayaran:", reply_markup=InlineKeyboardMarkup(buttons))
        return METODE_BAYAR

    elif data.startswith("metode_"):
        idx = int(data.split("_")[1])
        metode = metode_pembayaran[idx]
        user_data_store[query.from_user.id]["metode"] = metode
        buttons = [[InlineKeyboardButton("📤 Kirim Bukti TF", callback_data="kirim_bukti")]]
        await query.edit_message_text(f"{metode['nama']}:\n{metode['detail']}", reply_markup=InlineKeyboardMarkup(buttons))
        return KIRIM_BUKTI

    elif data == "kirim_bukti":
        await query.edit_message_text("Silakan kirim bukti transfer berupa foto.")
        return KIRIM_BUKTI

    elif data.startswith("owner_"):
        return await handle_owner_response(update, context)

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        user_data_store[user_id]["bukti"] = file_id
        produk = user_data_store[user_id]["produk"]
        metode = user_data_store[user_id]["metode"]
        caption = f"📥 Bukti TF dari @{update.message.from_user.username or user_id}\nProduk: {produk['nama']}\nMetode: {metode['nama']}"
        buttons = [
            [InlineKeyboardButton("✅ Konfirmasi", callback_data=f"owner_konfirmasi_{user_id}")],
            [InlineKeyboardButton("❌ Tolak", callback_data=f"owner_tolak_{user_id}")]
        ]
        await context.bot.send_photo(chat_id=OWNER_ID, photo=file_id, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        await update.message.reply_text("Bukti berhasil dikirim. Tunggu konfirmasi admin ya.")
        return INPUT_NOHP
    else:
        await update.message.reply_text("Hanya foto yang diterima.")
        return KIRIM_BUKTI

async def handle_owner_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, uid = query.data.split("_")[1:]
    uid = int(uid)

    if action == "konfirmasi":
        await context.bot.send_message(chat_id=uid, text="✅ Pembayaran kamu dikonfirmasi.\nSilakan kirim nomor HP.")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"Konfirmasi dikirim ke @{uid}")
        return INPUT_NOHP
    else:
        await context.bot.send_message(chat_id=uid, text="❌ Bukti transfer ditolak. Kirim ulang ya.")
        return KIRIM_BUKTI

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if "nohp" not in user_data_store[uid]:
        user_data_store[uid]["nohp"] = text
        await update.message.reply_text("✅ Nomor HP diterima. Silakan kirim OTP yang Anda terima.")
        return INPUT_OTP

    if "otp" not in user_data_store[uid]:
        user_data_store[uid]["otp"] = text
        await update.message.reply_text("✅ OTP diterima. Menunggu verifikasi.")
        return INPUT_VERIFIKASI

    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PILIH_BULAN: [CallbackQueryHandler(button_handler)],
            KONFIRMASI: [CallbackQueryHandler(button_handler)],
            METODE_BAYAR: [CallbackQueryHandler(button_handler)],
            KIRIM_BUKTI: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.PHOTO, handle_media)
            ],
            INPUT_NOHP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            INPUT_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            INPUT_VERIFIKASI: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
