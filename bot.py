import os
import sys
import subprocess
import logging
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# Load environment
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Produk & Metode Pembayaran
produk_list = [
    {"id": "1", "nama": "✨ Premium 1 Bulan", "harga": 54000},
    {"id": "2", "nama": "🌟 Premium 3 Bulan", "harga": 200000},
    {"id": "3", "nama": "💎 Premium 6 Bulan", "harga": 400000},
    {"id": "4", "nama": "🏆 Premium 12 Bulan", "harga": 5000000}
]

metode_pembayaran = [
    {"nama": "QRIS", "detail": "https://link-qris-kamu"},
    {"nama": "DANA", "detail": "08558827668 a.n @serpagengs"},
    {"nama": "Gopay", "detail": "083170123771 a.n @serpagengs"},
    {"nama": "Bank BCA", "detail": "5940804673 a.n @serpagengs"}
]

# States
(
    PILIH_BULAN, KONFIRMASI, METODE_BAYAR, KIRIM_BUKTI,
    INPUT_NOHP, INPUT_OTP, INPUT_VERIFIKASI
) = range(7)

user_data_store = {}

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = (
        "👑 𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝑺𝒓𝒑𝒂𝑷𝒓𝒆𝒎 👑\n\n"
        "✨ 𝐓𝐄𝐋𝐄𝐏𝐑𝐄𝐌 𝐌𝐔𝐑𝐀𝐇 & 𝐓𝐄𝐑𝐏𝐄𝐑𝐂𝐀𝐘𝐀 ✨\n\n"
        "📦 Daftar Produk:\n\n"
    )
    for p in produk_list:
        teks += f"{p['id']}. {p['nama']} - Rp {p['harga']:,} ✨\n"

    keyboard = [
        [InlineKeyboardButton("🛒 Beli Disini", callback_data="beli")],
        [InlineKeyboardButton("📞 CS", url="https://t.me/serpagengs"),
         InlineKeyboardButton("📣 Testi", url="https://t.me/srpatesti")]
    ]
    await update.message.reply_text(teks, reply_markup=InlineKeyboardMarkup(keyboard))
    return PILIH_BULAN

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Kamu tidak punya akses ke perintah ini.")
        return
    keyboard = [
        [InlineKeyboardButton("🔁 Restart Bot", callback_data="restart_bot"),
         InlineKeyboardButton("⬇️ Git Pull", callback_data="git_pull")]
    ]
    await update.message.reply_text("🛠 Menu Owner:", reply_markup=InlineKeyboardMarkup(keyboard))

async def owner_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != OWNER_ID:
        await query.edit_message_text("❌ Kamu tidak punya izin.")
        return

    if query.data == "restart_bot":
        await query.edit_message_text("🔁 Bot akan direstart...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif query.data == "git_pull":
        try:
            result = subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT).decode()
            await query.edit_message_text(f"✅ Git Pull Sukses:\n```\n{result}\n```", parse_mode="Markdown")
        except subprocess.CalledProcessError as e:
            await query.edit_message_text(f"❌ Git Pull Gagal:\n```\n{e.output.decode()}\n```", parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "beli":
        keyboard = [[InlineKeyboardButton(p["nama"], callback_data=f"beli_{p['id']}")] for p in produk_list]
        keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="start")])
        await query.edit_message_text("Pilih paket premium:", reply_markup=InlineKeyboardMarkup(keyboard))
        return KONFIRMASI

    elif data.startswith("beli_"):
        produk_id = data.split("_")[1]
        produk = next((p for p in produk_list if p["id"] == produk_id), None)
        if not produk:
            await query.edit_message_text("Produk tidak ditemukan.")
            return ConversationHandler.END
        user_data_store[query.from_user.id] = {"produk": produk}
        buttons = [
            [InlineKeyboardButton("✅ Konfirmasi", callback_data="konfirmasi_produk")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="beli")]
        ]
        await query.edit_message_text(f"🛍️ {produk['nama']}\nHarga: Rp {produk['harga']:,}", reply_markup=InlineKeyboardMarkup(buttons))
        return METODE_BAYAR

    elif data == "konfirmasi_produk":
        buttons = [[InlineKeyboardButton(p["nama"], callback_data=f"metode_{i}")] for i, p in enumerate(metode_pembayaran)]
        await query.edit_message_text("Pilih metode pembayaran:", reply_markup=InlineKeyboardMarkup(buttons))
        return KIRIM_BUKTI

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

    elif data.startswith("owner_konfirmasi_"):
        uid = int(data.split("_")[-1])
        await context.bot.send_message(uid, "✅ Terima Kasih Pembayaran dikonfirmasi.\nSilakan kirim nomor HP.")
        await query.edit_message_text("Konfirmasi dikirim.")
        return INPUT_NOHP

    elif data.startswith("owner_tolak_"):
        uid = int(data.split("_")[-1])
        await context.bot.send_message(uid, "❌ Bukti ditolak. Kirim ulang.")
        await query.edit_message_text("Tolak konfirmasi dikirim.")
        return KIRIM_BUKTI

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        user_data_store[user_id]["bukti"] = file_id
        produk = user_data_store[user_id]["produk"]
        metode = user_data_store[user_id]["metode"]
        caption = f"📥 Bukti TF dari @{update.message.from_user.username or user_id}\nProduk: {produk['nama']}\nMetode: {metode['nama']}"
        buttons = [[
            InlineKeyboardButton("✅ Konfirmasi", callback_data=f"owner_konfirmasi_{user_id}"),
            InlineKeyboardButton("❌ Tolak", callback_data=f"owner_tolak_{user_id}")
        ]]
        await context.bot.send_photo(chat_id=OWNER_ID, photo=file_id, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        await update.message.reply_text("Bukti berhasil dikirim. Tunggu konfirmasi admin ya kak.")
        return INPUT_NOHP
    else:
        await update.message.reply_text("Hanya gambar yang diterima.")
        return KIRIM_BUKTI

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if "nohp" not in user_data_store[uid]:
        user_data_store[uid]["nohp"] = text
        await update.message.reply_text("✅ Nomor HP diterima, sekarang kirim OTP (gunakan spasi).")
        return INPUT_OTP
    elif "otp" not in user_data_store[uid]:
        user_data_store[uid]["otp"] = text
        await update.message.reply_text("✅ OTP diterima, kirim verifikasi 2 langkah (atau ketik 'skip').")
        return INPUT_VERIFIKASI
    else:
        user_data_store[uid]["verifikasi"] = text
        await update.message.reply_text("Terima kasih atas pembelianmu. Tunggu proses aktivasi ya kak.")
        return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PILIH_BULAN: [CallbackQueryHandler(button_handler)],
            KONFIRMASI: [CallbackQueryHandler(button_handler)],
            METODE_BAYAR: [CallbackQueryHandler(button_handler)],
            KIRIM_BUKTI: [CallbackQueryHandler(button_handler), MessageHandler(filters.PHOTO, handle_media)],
            INPUT_NOHP: [MessageHandler(filters.TEXT, handle_text)],
            INPUT_OTP: [MessageHandler(filters.TEXT, handle_text)],
            INPUT_VERIFIKASI: [MessageHandler(filters.TEXT, handle_text)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("owner", owner_panel))
    app.add_handler(CallbackQueryHandler(owner_callback, pattern="^(restart_bot|git_pull)$"))

    print("Bot is running...")
    app.run_polling()
