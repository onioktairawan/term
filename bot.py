import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
from telegram.ext import MessageHandler, filters

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states for conversation
START, PILIH_BULAN, KONFIRMASI, PEMBAYARAN, KIRIM_BUKTI, VERIFIKASI = range(6)

# Command handler for /start
async def start(update: Update, context: CallbackContext) -> int:
    # Check if message text is different before editing
    message = update.callback_query.message
    text = "Selamat datang! Berikut produk yang kami jual:\n\nProduk A - Rp 100,000\nProduk B - Rp 200,000"

    # Only edit if the text is different
    if message.text != text:
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Beli Disini", callback_data='beli')],
                [InlineKeyboardButton("CS", callback_data='cs')],
                [InlineKeyboardButton("Testimoni", callback_data='testimoni')]
            ])
        )
    return PILIH_BULAN

# Handle product selection
async def pilih_bulan(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("1 Bulan", callback_data='1_bulan')],
        [InlineKeyboardButton("3 Bulan", callback_data='3_bulan')],
        [InlineKeyboardButton("6 Bulan", callback_data='6_bulan')],
        [InlineKeyboardButton("12 Bulan", callback_data='12_bulan')],
        [InlineKeyboardButton("Kembali", callback_data='kembali')],
    ]
    await update.callback_query.message.edit_text(
        "Silakan pilih durasi berlangganan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return KONFIRMASI

# Handle confirmation of purchase
async def konfirmasi(update: Update, context: CallbackContext) -> int:
    bulan = update.callback_query.data
    if bulan == 'kembali':
        # Go back to the product list
        return await start(update, context)
    
    text = f"Detail produk untuk {bulan} bulan:\nHarga: Rp {int(bulan.split('_')[0])*100000}\n\nApakah Anda yakin?"
    keyboard = [
        [InlineKeyboardButton("Konfirmasi", callback_data='konfirmasi')],
        [InlineKeyboardButton("Kembali", callback_data='kembali')]
    ]
    await update.callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PEMBAYARAN

# Payment methods
async def pembayaran(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data='qris')],
        [InlineKeyboardButton("DANA", callback_data='dana')],
        [InlineKeyboardButton("Bank BCA", callback_data='bca')],
        [InlineKeyboardButton("Kembali", callback_data='kembali')]
    ]
    await update.callback_query.message.edit_text(
        "Silakan pilih metode pembayaran:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return KIRIM_BUKTI

# Kirim bukti transfer
async def kirim_bukti(update: Update, context: CallbackContext) -> int:
    # Ask user to send transfer proof
    await update.callback_query.message.edit_text(
        "Silakan kirim bukti transfer (screenshot).",
    )
    return VERIFIKASI

# Handle verification of transfer proof
async def verifikasi(update: Update, context: CallbackContext) -> int:
    # Handle verification logic, notify owner
    media = update.message.photo[-1].file_id if update.message.photo else None
    if media:
        # Notify owner about the transfer proof
        await context.bot.send_message(chat_id=context.bot_data['owner_chat_id'], text="Bukti transfer baru diterima.")
        # Ask for next step (phone number)
        await update.message.reply_text("Terima kasih! Sekarang kirimkan nomor HP Anda.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Mohon kirimkan bukti transfer dalam bentuk screenshot.")
        return VERIFIKASI

# Handle user command /help (optional)
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Bot ini digunakan untuk membeli produk.")

# Main function to run the bot
def main():
    application = Application.builder().token('YOUR_BOT_API_TOKEN').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PILIH_BULAN: [CallbackQueryHandler(pilih_bulan)],
            KONFIRMASI: [CallbackQueryHandler(konfirmasi)],
            PEMBAYARAN: [CallbackQueryHandler(pembayaran)],
            KIRIM_BUKTI: [CallbackQueryHandler(kirim_bukti)],
            VERIFIKASI: [MessageHandler(filters.PHOTO, verifikasi)],
        },
        fallbacks=[CommandHandler('help', help_command)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
