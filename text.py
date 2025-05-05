# text.py

WELCOME = """
👋 Selamat datang di *Bot Premium*!

Berikut daftar produk yang tersedia:
"""

PILIH_DURASI = "Silakan pilih durasi langganan:"

DETAIL_PRODUK = lambda nama, harga: f"""
🛍 *{nama}*
💳 Harga: Rp {harga:,}
"""

METODE_PEMBAYARAN = """
💳 *Pilih Metode Pembayaran:*
- QRIS: [Klik QRIS](https://link.qriscontoh.com)
- DANA: 081234567890
- GoPay: 081234567890
- Bank BCA: 1234567890 a.n Nama Penerima
"""

KIRIM_BUKTI = "📤 Silakan kirim *bukti transfer* (dalam bentuk *screenshot*) untuk diproses."

MENUNGGU_KONFIRMASI = "⏳ Menunggu konfirmasi dari admin..."

MINTA_NOHP = "📱 Kirim *nomor HP* yang akan digunakan."

MINTA_OTP = "🔐 Kirim *kode OTP* yang kamu terima."

MINTA_VERIF2LANGKAH = "🔒 Jika akun kamu memiliki *verifikasi 2 langkah*, kirimkan di sini. Jika tidak ada, klik tombol 'Skip'."

SELESAI = """
✅ *Terima kasih atas pembelianmu!*

Tunggu beberapa saat, pesanan kamu sedang diproses.
"""

TERIMAKASIH = "🙏 Terima kasih! Jangan lupa berlangganan terus."
