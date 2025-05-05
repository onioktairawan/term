import logging
import os
import subprocess
import sys
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
    {"id": "1", "nama": "✨ Premium 1 Bulan", "harga": 53000},
    {"id": "2", "nama": "🌟 Premium 3 Bulan", "harga": 210000},
    {"id": "3", "nama": "💎 Premium 6 Bulan", "harga": 289000},
    {"id": "4", "nama": "🏆 Premium 12 Bulan", "harga": 389000}
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
    keyboard = [
        [InlineKeyboardButton("🛒 Beli Disini", callback_data="beli")],
        [InlineKeyboardButton("📞 Cs", url="t.me/serpagengs"),
         InlineKeyboardButton("📣 Testi", url="t.me/srpatesti")]
    ]
    await update.message.reply_text("Selamat datang! Silakan pilih layanan.", reply_markup=InlineKeyboardMarkup(keyboard))
    return PILIH_BULAN

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Kamu tidak punya izin.")
        return
    buttons = [
        [InlineKeyboardButton("↺ Restart Bot", callback_data="restart_bot")],
        [InlineKeyboardButton("⬇️ Git Pull", callback_data="git_pull")]
    ]
    await update.message.reply_text("🛠 Admin Panel", reply_markup=InlineKeyboardMarkup(buttons))

async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if user_id != OWNER_ID:
        await query.edit_message_text("❌ Akses ditolak.")
        return
    if query.data == "git_pull":
        try:
            result = subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT).decode()
            await query.edit_message_text(f"✅ Git Pull Success:\n<code>{result}</code>", parse_mode="HTML")
        except subprocess.CalledProcessError as e:
            await query.edit_message_text(f"❌ Git Pull Failed:\n<code>{e.output.decode()}</code>", parse_mode="HTML")
    elif query.data == "restart_bot":
        await query.edit_message_text("♻️ Restarting bot...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "beli":
        keyboard = [[InlineKeyboardButton(p["nama"], callback_data=f"beli_{p['id']}")] for p in produk_list]
        await query.edit_message_text("Pilih paket premium yang ingin dibeli:", reply_markup=InlineKeyboardMarkup(keyboard))
        return KONFIRMASI

    elif data.startswith("beli_"):
        produk_id = data.split("_")[1]
        produk = next((p for p in produk_list if p["id"] == produk_id), None)
        if not produk:
            await query.edit_message_text("Produk tidak ditemukan.")
            return ConversationHandler.END
        user_data_store[query.from_user.id] = {"produk": produk}
        text = f"💼 {produk['nama']}\nHarga: Rp {produk['harga']:,}"
        buttons = [
            [InlineKeyboardButton("✅ Konfirmasi", callback_data="konfirmasi_produk")]
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
        buttons = [[InlineKeyboardButton("📤 Kirim Bukti TF", callback_data="kirim_bukti")]]
        await query.edit_message_text(f"{metode['nama']}:\n{metode['detail']}", reply_markup=InlineKeyboardMarkup(buttons))
        return KIRIM_BUKTI

    elif data == "kirim_bukti":
        await query.edit_message_text("Silakan kirim screenshot bukti transfer.")
        return KIRIM_BUKTI

    elif data.startswith("owner_konfirmasi_"):
        uid = int(data.split("_")[-1])
        await context.bot.send_message(chat_id=uid, text="✅ Pembayaran dikonfirmasi. Silakan kirim nomor HP Anda.")
        return INPUT_NOHP

    elif data.startswith("owner_tolak_"):
        uid = int(data.split("_")[-1])
        await context.bot.send_message(chat_id=uid, text="❌ Bukti tidak valid. Silakan kirim ulang.")
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
        await update.message.reply_text("Hanya foto yang diterima.")
        return KIRIM_BUKTI

async def handle_nohp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_store[update.message.from_user.id]["nohp"] = update.message.text
    await update.message.reply_text("Nomor HP diterima. Langkah selanjutnya akan dikirim segera.")
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
            INPUT_NOHP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nohp)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_button_handler, pattern="^(git_pull|restart_bot)$"))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(owner_konfirmasi_|owner_tolak_).*$"))

    print("Bot is running...")
    app.run_polling()
