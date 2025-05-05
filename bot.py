# bot.py

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler, ContextTypes
)
from daftarproduk import produk_list
from text import *

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNEL_TESTI = os.getenv("CHANNEL_TESTI")
LINK_QRIS = os.getenv("LINK_QRIS")
NOREK_BCA = os.getenv("NOREK_BCA")
NAMA_PENERIMA = os.getenv("NAMA_PENERIMA")
NOMOR_DANA = os.getenv("NOMOR_DANA")
NOMOR_GOPAY = os.getenv("NOMOR_GOPAY")

(
    MENU, PILIH_DURASI, KONFIRMASI_PRODUK, METODE_PEMBAYARAN,
    KIRIM_BUKTI, MINTA_NOHP, MINTA_OTP, VERIF_2LANGKAH, FINAL
) = range(9)

user_data_dict = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 Beli Sekarang", callback_data="beli")],
        [
            InlineKeyboardButton("💬 CS", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("📢 Testi", url=f"https://t.me/{CHANNEL_TESTI.lstrip('@')}")
        ]
    ]
    text_produk = WELCOME
    for produk in produk_list:
        text_produk += f"\n- {produk['nama']} : Rp {produk['harga']:,}"

    if update.message:
        await update.message.reply_text(
            text_produk,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            text_produk,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    return MENU

# Tambahan handler dan flow lainnya akan disambung di sini dalam bagian berikutnya sesuai urutan: 
# - Pilih Durasi
# - Konfirmasi Produk
# - Pilih Metode Pembayaran
# - Kirim Bukti Transfer
# - Verifikasi Nomor HP
# - Kirim OTP
# - Verifikasi 2 Langkah
# - Finalisasi

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                CallbackQueryHandler(start, pattern="^beli$")
            ]
            # State lainnya akan dilanjutkan nanti
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.run_polling()
