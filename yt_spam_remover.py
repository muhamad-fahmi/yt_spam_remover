import os
import pickle
import re
import time
from colorama import init, Fore, Style
init(autoreset=True)

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
KEYWORD_FILE = "spam_keywords.txt"

# ------------------ Banner --------------------------------
def print_banner():
    banner = fr"""
{Fore.CYAN}{Style.BRIGHT}
     )           (                        (                                 
  ( /(   *   )   )\ )                     )\ )                              
  )\())` )  /(  (()/(          )    )    (()/(  (    )        )     (  (    
 ((_)\  ( )(_))  /(_))`  )  ( /(   (      /(_))))\  (     (  /((   ))\ )(   
__ ((_)(_(_())  (_))  /(/(  )(_))  )\  ' (_)) /((_) )\  ' )\(_))\ /((_|()\  
\ \ / /|_   _|  / __|((_)_\((_)_ _((_))  | _ (_)) _((_)) ((_))((_|_))  ((_) 
 \ V /   | |    \__ \| '_ \) _` | '  \() |   / -_) '  \() _ \ V // -_)| '_| 
  |_|    |_|    |___/| .__/\__,_|_|_|_|  |_|_\___|_|_|_|\___/\_/ \___||_|   
                     |_|                                                    
                                                              {Fore.YELLOW}🧹 By - @MF {Style.RESET_ALL}
"""
    print(banner)

# ------------------ Check Quota -------------------------
def handle_quota_error(e):
    if isinstance(e, HttpError) and e.resp.status == 403 and 'quotaExceeded' in str(e):
        print(f"{Fore.RED}❌ Kuota API YouTube Anda telah habis!")
        print("🔗 Silakan cek kuota di: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas")
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write("Kuota habis!\n")
        return True
    return False

# ------------------ CHANNEL_ID --------------------------
CHANNEL_ID_FILE = "channel_id.txt"

def save_channel_id(channel_id):
    with open(CHANNEL_ID_FILE, "w", encoding="utf-8") as f:
        f.write(channel_id.strip())

def load_channel_id():
    if os.path.exists(CHANNEL_ID_FILE):
        with open(CHANNEL_ID_FILE, "r", encoding="utf-8") as f:
            cid = f.read().strip()
            if cid:
                return cid
    return None

# ------------------ Keyword Management ------------------
def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_keywords(keywords):
    with open(KEYWORD_FILE, "w", encoding="utf-8") as f:
        for keyword in keywords:
            f.write(keyword.strip() + "\n")

def manage_keywords():
    while True:
        print("\n📋 Menu Keyword Spam:")
        print("1. Lihat semua keyword")
        print("2. Tambah keyword")
        print("3. Hapus keyword")
        print("4. Kembali ke menu utama")
        choice = input("👉 Pilih menu (1-4): ").strip()
        keywords = load_keywords()

        if choice == "1":
            if not keywords:
                print("⚠️ Tidak ada keyword.")
            else:
                print("\n📌 Daftar Keyword:")
                for i, k in enumerate(keywords, 1):
                    print(f"{i}. {k}")
        elif choice == "2":
            clear = lambda: os.system("cls" if os.name == "nt" else "clear")
            clear()
            
            new_keyword = input("➕ Masukkan keyword baru: ").strip().lower()
            if new_keyword and new_keyword not in keywords:
                keywords.append(new_keyword)
                save_keywords(keywords)
                print("✅ Keyword ditambahkan.")
            else:
                print("⚠️ Keyword sudah ada atau kosong.")
        elif choice == "3":
            if not keywords:
                print("⚠️ Tidak ada keyword untuk dihapus.")
                continue
            for i, k in enumerate(keywords, 1):
                print(f"{i}. {k}")
            try:
                index = int(input("🗑️ Masukkan nomor keyword yang ingin dihapus: ")) - 1
                if 0 <= index < len(keywords):
                    removed = keywords.pop(index)
                    save_keywords(keywords)
                    print(f"✅ Keyword '{removed}' dihapus.")
                else:
                    print("❌ Nomor tidak valid.")
            except ValueError:
                print("❌ Masukkan angka.")
        elif choice == "4":
            clear = lambda: os.system("cls" if os.name == "nt" else "clear")
            clear()
            break
        else:
            print("❌ Pilihan tidak valid.")

# ------------------ YouTube Auth ------------------
def authenticate():
    creds = None
    if not os.path.exists("client_secret.json"):
        print("❌ File 'client_secret.json' tidak ditemukan!")
        print("➡️ Silakan letakkan file 'client_secret.json' di folder aplikasi.")
        print("➡️ File 'client_secret.json' didapatkan dari Google Cloud Console : 'https://console.cloud.google.com/apis/credentials'.")
        print("➡️ Pastikan Anda sudah mengaktifkan YouTube Data API v3.")
        input("Tekan Enter untuk keluar...")
        clear = lambda: os.system("cls" if os.name == "nt" else "clear")
        clear()
        exit(1)

    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token_file:
            creds = pickle.load(token_file)

    if not creds or not creds.valid:
        from google.auth.transport.requests import Request

        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pkl", "wb") as token_file:
            pickle.dump(creds, token_file)
        print("✅ Token baru berhasil digenerate dan disimpan sebagai 'token.pkl'.")

    return build("youtube", "v3", credentials=creds)

# ------------------ Core Program ------------------
def is_spam(comment):
    comment_lower = comment.lower()
    keywords = load_keywords()

    if any(k in comment_lower for k in keywords):
        return True
    if re.search(r'\b[a-zA-Z]{3,10}(77|88|99|69)\b', comment):
        return True
    if comment.count("https://") > 1:
        return True
    if comment.count("🔥") > 5 or comment.count("💰") > 5 or comment.count("💸") > 5:
        return True
    return False

def verify_comment(youtube, comment_id):
    try:
        res = youtube.commentThreads().list(part="snippet", id=comment_id).execute()
        return bool(res.get("items"))
    except:
        return False

def get_uploads_playlist_id(youtube, channel_id):
    res = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_all_video_ids(youtube, playlist_id):
    video_ids, next_page_token = [], None
    while True:
        res = youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=50, pageToken=next_page_token
        ).execute()
        video_ids += [item["snippet"]["resourceId"]["videoId"] for item in res["items"]]
        next_page_token = res.get("nextPageToken")
        if not next_page_token:
            break
    return video_ids

def get_comments(youtube, video_id, channel_id):
    try:
        video = youtube.videos().list(part="snippet", id=video_id).execute()
        if not video["items"] or video["items"][0]["snippet"]["channelId"] != channel_id:
            print(f"⚠️ Video {video_id} bukan dari channel ini. Lewati.")
            return []
    except:
        return []

    comments, next_page_token = [], None
    while True:
        res = youtube.commentThreads().list(
            part="snippet", videoId=video_id, textFormat="plainText", maxResults=100, pageToken=next_page_token
        ).execute()
        for item in res["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append((item["snippet"]["topLevelComment"]["id"], snippet["textDisplay"]))
        next_page_token = res.get("nextPageToken")
        if not next_page_token:
            break
    return comments

def delete_comment(youtube, comment_id, max_retries=3):
    if not verify_comment(youtube, comment_id):
        print(f"⚠️ Komentar {comment_id} tidak ditemukan. Lewati.")
        return False
    for attempt in range(max_retries):
        try:
            youtube.comments().setModerationStatus(id=comment_id, moderationStatus="rejected").execute()
            print(f"🛑 Komentar {comment_id} disembunyikan.")
            return True
        except Exception as e:
            time.sleep(2 ** attempt)
    return False

# ------------------ Main Menu ------------------
def main():
    clear = lambda: os.system("cls" if os.name == "nt" else "clear")
    clear()
    print_banner()
    while True:
        print("\n📌 Menu Utama:")
        print("1. Mulai scan komentar")
        print("2. Kelola keyword spam")
        print("3. Keluar")
        print("0. Clear log dan kembali ke menu utama")
        pilihan = input("👉 Pilih menu (1-3): ").strip()

        if pilihan == "1":

            youtube = authenticate()

            channel_id = load_channel_id()

            if channel_id:
                print(f"📥 Channel ID yang digunakan: {channel_id}")
                ganti = input("🔄 Ganti Channel ID? (y/n): ").strip().lower()
                if ganti == "y":
                    channel_id = input("📥 Masukkan Channel ID baru: ").strip()
                    if not channel_id:
                        print("❌ Channel ID tidak boleh kosong.")
                        continue
                    save_channel_id(channel_id)
            else:
                channel_id = input("📥 Masukkan Channel ID: ").strip()
                if not channel_id:
                    print("❌ Channel ID tidak boleh kosong.")
                    continue
                save_channel_id(channel_id)

            try:
                uploads_playlist_id = get_uploads_playlist_id(youtube, channel_id)
                video_ids = get_all_video_ids(youtube, uploads_playlist_id)
            except Exception as e:
                if handle_quota_error(e):
                    break
                print(f"❌ Gagal mengambil video: {e}")
                continue

            for video_id in video_ids:
                print(f"\n🔍 Mengecek komentar Video ID: {video_id}")
                try:
                    comments = get_comments(youtube, video_id, channel_id)
                except Exception as e:
                    if handle_quota_error(e):
                        break
                    print(f"❌ Gagal mengambil komentar: {e}")
                    continue

                if not comments:
                    print("⚠️ Tidak ada komentar.")
                    continue

                for comment_id, text in comments:
                    print(f"💬 {text}")
                    if is_spam(text):
                        print("🚫 Deteksi spam!")
                        try:
                            delete_comment(youtube, comment_id)
                        except Exception as e:
                            if handle_quota_error(e):
                                break
                            print(f"❌ Gagal menghapus komentar: {e}")

        elif pilihan == "2":
            manage_keywords()
        elif pilihan == "3":
            print("👋 Keluar dari program.")
            clear = lambda: os.system("cls" if os.name == "nt" else "clear")
            clear()
            break
        elif pilihan == "0":
            clear = lambda: os.system("cls" if os.name == "nt" else "clear")
            clear()
        else:
            print("❌ Pilihan tidak valid.")

if __name__ == "__main__":
    main()
