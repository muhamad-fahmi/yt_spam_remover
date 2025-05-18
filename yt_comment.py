import os
import pickle
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# OAuth2
def authenticate():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

# YouTube API
youtube = authenticate()

# ID channel
CHANNEL_ID = "UCGXdKEbrgqaG-1D3Q3O2SoQ"


def get_uploads_playlist_id(channel_id):
    res = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    return res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# video_id
def get_all_video_ids(playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in res['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])

        next_page_token = res.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

# komentar
def get_comments(video_id):
    comments = []
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=100
    ).execute()

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comment_id = item["snippet"]["topLevelComment"]["id"]
        comments.append((comment_id, comment))

    return comments

# deteksi spam
def is_spam(comment):
    comment_lower = comment.lower()

    spam_keywords = [
        "subscribe back", "bit.ly", "free", "check my channel", "whatsapp", "telegram", "xxx", "maxwin", "gacor", "judi",
        "main slot", "slot online", "situs judi", "agen slot", "link alternatif", "jepe", "slot gacor", "gampang jackpot",
        "dola77", "doma77", "slot bonus", "slot terbaru", "slot demo", "winrate", "maxwin", "sensasional", "jackpot",
        "jackpot besar", "slot online terpercaya", "slot online indonesia", "slot online gacor", "slot online bonus",
        "slot online jackpot", "slot online terbaru", "slot online demo", "slot online winrate", "slot online maxwin", "agemaxwin", "bonus", "pengguna", "link", "agen", "situs", "daftar", "bonus new member", "bonus deposit", "bonus referral", "bonus cashback", "harian"
    ]

    # Keyword cocok langsung
    if any(keyword in comment_lower for keyword in spam_keywords):
        return True

    # Deteksi nama domain / situs tidak umum (nama brand "77", "88", dll)
    if re.search(r'\b[a-zA-Z]{3,10}(77|88|99|69)\b', comment):
        return True

    # Banyak link
    if len(re.findall(r"https?://", comment)) > 1:
        return True

    # Emoji berlebihan
    if comment.count("🔥") > 5 or comment.count("💰") > 5 or comment.count("💸") > 5 or comment.count("💵") > 5:
        return True

    return False

# hapus komentar
def delete_comment(comment_id):
    youtube.comments().setModerationStatus(
        id=comment_id,
        moderationStatus="rejected"
    ).execute()


if __name__ == "__main__":
    uploads_playlist_id = get_uploads_playlist_id(CHANNEL_ID)
    video_ids = get_all_video_ids(uploads_playlist_id)

    for video_id in video_ids:
        print(f"Memeriksa komentar pada Video ID: {video_id}")
        comments = get_comments(video_id)
        for comment_id, text in comments:
            print(f"Komentar: {text}")

            if is_spam(text):
                print(f"🚫 Hapus komentar spam: {text}")
                delete_comment(comment_id)
