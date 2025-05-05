import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import os

# Memuat variabel dari .env
load_dotenv()

# Ambil token dan variabel lainnya
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
CHANNEL_TESTI = os.getenv('CHANNEL_TESTI')
NAMA_PENERIMA = os.getenv('NAMA_PENERIMA')
NOREK_BCA = os.getenv('NOREK_BCA')
NOMOR_DANA = os.getenv('NOMOR_DANA')
NOMOR_GOPAY = os.getenv('NOMOR_GOPAY')
LINK_QRIS = os.getenv('LINK_QRIS')

# Logging untuk debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Step ConversationHandler
PILIH_METODE, KONFIRMASI_BAYAR, NO_HP, OTP, DONE = range(5)

# Fungsi untuk mulai bot
def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    keyboard = [
        [InlineKeyboardButton("Beli Prem Sekarang", callback_data='beli')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Kirim pesan selamat datang dengan tombol
    update.message.reply_text(
        "Selamat datang! Tekan tombol di bawah untuk mulai proses pembelian.",
        reply_markup=reply_markup
    )

    return PILIH_METODE

# Fungsi untuk pilihan metode pembayaran
def pilih_metode(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("BCA", callback_data='bca')],
        [InlineKeyboardButton("DANA", callback_data='dana')],
        [InlineKeyboardButton("Gopay", callback_data='gopay')],
        [InlineKeyboardButton("QRIS", callback_data='qris')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Pilih metode pembayaran:",
        reply_markup=reply_markup
    )
    
    return KONFIRMASI_BAYAR

# Fungsi untuk konfirmasi pembayaran
def konfirmasi_bayar(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    metode = query.data

    # Mengirimkan informasi rekening sesuai metode
    if metode == 'bca':
        info_bayar = f"Silahkan transfer ke:\nNo Rekening: {NOREK_BCA}\nAtas Nama: {NAMA_PENERIMA}"
    elif metode == 'dana':
        info_bayar = f"Silahkan transfer ke:\nNo DANA: {NOMOR_DANA}\nAtas Nama: {NAMA_PENERIMA}"
    elif metode == 'gopay':
        info_bayar = f"Silahkan transfer ke:\nNo Gopay: {NOMOR_GOPAY}\nAtas Nama: {NAMA_PENERIMA}"
    else:
        info_bayar = f"Silahkan transfer ke:\nLink QRIS: {LINK_QRIS}"

    keyboard = [
        [InlineKeyboardButton("Kirim Bukti Transfer", callback_data='bukti_transfer')],
        [InlineKeyboardButton("Ulangi", callback_data='ulang')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=info_bayar,
        reply_markup=reply_markup
    )

    return NO_HP

# Fungsi untuk menerima bukti transfer
def kirim_bukti_transfer(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        text="Silakan kirim bukti transfer berupa gambar atau file.",
    )

    return OTP

# Fungsi untuk input nomor HP
def input_no_hp(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Kirimkan nomor HP Anda untuk proses verifikasi.",
    )
    
    return OTP

# Fungsi untuk verifikasi OTP
def verifikasi_otp(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Masukkan kode OTP yang dikirim ke nomor HP Anda.",
    )
    
    return DONE

# Fungsi selesai
def selesai(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Terima kasih! Proses telah selesai. Silakan cek status pembayaran Anda.",
    )
    
    return ConversationHandler.END

# Fungsi utama untuk menjalankan bot
def main() -> None:
    updater = Updater(BOT_TOKEN)

    # Menambahkan handler untuk command dan callback query
    dp = updater.dispatcher

    # ConversationHandler untuk setiap step
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PILIH_METODE: [CallbackQueryHandler(pilih_metode)],
            KONFIRMASI_BAYAR: [CallbackQueryHandler(konfirmasi_bayar)],
            NO_HP: [MessageHandler(Filters.text & ~Filters.command, input_no_hp)],
            OTP: [MessageHandler(Filters.text & ~Filters.command, verifikasi_otp)],
            DONE: [MessageHandler(Filters.text & ~Filters.command, selesai)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dp.add_handler(conv_handler)

    # Memulai bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
