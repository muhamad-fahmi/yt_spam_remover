**YT Spam Remover** adalah tool untuk mendeteksi dan menghapus komentar spam dari channel YouTube. Alat ini menggunakan YouTube Data API V3 dan mendeteksi spam berdasarkan keyword dan pola umum dari komentar promosi, judi, atau bot.

---

## Fitur

- 🔍 Scan semua komentar di semua video channel
- 🛑 Deteksi komentar spam secara otomatis
- 🧹 Hapus komentar spam (mode moderasi YouTube)
- 🗂️ Manajemen keyword spam (tambah, hapus, lihat)
- ✅ Autentikasi via OAuth 2.0

---

## Instalasi

1. Clone repository:

    ```bash
    git clone https://github.com/muhamad-fahmi/yt_spam_remover.git
    cd yt_spam_remover
    ```
2.  Install requirements:
    ```bash
    pip -i requirements.txt
    ```
3. Build Exe
    ```bash
    python -m PyInstaller --onefile yt_spam_remover.py
    ```
4. Tambahkan file kredensial YouTube:

    - Buat project di [Google Cloud Console](https://console.cloud.google.com/projectcreate)
    - Aktifkan [YouTube Data API v3](https://console.cloud.google.com/apis/api/youtube.googleapis.com?inv=1&invt=Abx3fg)
    - Buat OAuth Client ID dan download `client_secret.json` pada "Credentials"
    - Letakkan file tersebut di folder utama proyek

