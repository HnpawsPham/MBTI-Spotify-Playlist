import streamlit as st
import spotipy
import requests, time, validators, json, base64
from spotipy.oauth2 import SpotifyOAuth

# SECRETS
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
b64_auth = base64.b64encode(auth_str.encode()).decode()


auth_url = "https://accounts.spotify.com/api/token"
auth_headers = {
    "Authorization": f"Basic {b64_auth}",
    "Content-Type": "application/x-www-form-urlencoded"
}
auth_data = {
    "grant_type": "client_credentials"
}

auth_res = requests.post(auth_url, headers=auth_headers, data=auth_data)
access_token = auth_res.json().get("access_token")

if access_token:
    st.success("✅ Đã lấy được Access Token!")

    ids = "7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"
    audio_url = f"https://api.spotify.com/v1/audio-features?ids={ids}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(audio_url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        st.subheader("🎧 Audio Features")
        for track in data["audio_features"]:
            st.write({
                "Track ID": track["id"],
                "Energy": track["energy"],
                "Danceability": track["danceability"],
                "Tempo": track["tempo"],
                "Valence": track["valence"]
            })
    else:
        st.error("Lỗi khi gọi audio-features")
else:
    st.error("❌ Lỗi khi lấy Access Token")

# # CONFIG
# if "auth_manager" not in st.session_state:
#     st.session_state.auth_manager = SpotifyOAuth(
#         SPOTIFY_CLIENT_ID=SPOTIFY_CLIENT_ID,
#         SPOTIFY_CLIENT_SECRET=SPOTIFY_CLIENT_SECRET,
#         redirect_uri="https://mbti-spotify-playlist1.streamlit.app/callback",
#         scope="user-library-read playlist-read-private"
#     )

# auth_manager = st.session_state.auth_manager
# params = st.query_params

# # LOGIN
# if "spotify" not in st.session_state:
#     if "code" not in params:
#         login_url = auth_manager.get_authorize_url()
#         st.markdown(f"[Login with Spotify]({login_url})", unsafe_allow_html=True)
#         st.stop()
#     else:
#         code = params["code"][0]
#         try:
#             token_info = auth_manager.get_access_token(code)
#             access_token = token_info["access_token"]
#             st.session_state.spotify = spotipy.Spotify(auth=access_token)
#             st.success("Đăng nhập thành công!")
#         except Exception as e:
#             st.error("Đăng nhập thất bại:")
#             st.exception(e)
#             st.stop()

# sp = st.session_state.spotify

# # ULITIES
# def extract_playlist_id(url):
#     match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
#     return match.group(1) if match else None

# def get_audio_features(track_ids):
#     all_features = []
#     chunks = [track_ids[i:i + 50] for i in range(0, len(track_ids), 50)]  # Spotify limit: 100, dùng 50 cho an toàn
#     for chunk in chunks:
#         try:
#             features = sp.audio_features(chunk)
#             if features:
#                 all_features.extend([f for f in features if f is not None])
#         except Exception as e:
#             st.warning(f"Lỗi khi lấy features với chunk: {chunk[:2]}...: {e}")
#             continue
#         time.sleep(0.1)  
#     return all_features

# def playlist_info(playlist):
#     raw_items = playlist["tracks"]["items"]
#     track_ids = [item["track"]["id"] for item in raw_items if item["track"] and item["track"].get("id")]
#     if not track_ids:
#         st.error("Playlist không có track hợp lệ")
#         return None
#     features = get_audio_features(track_ids)
#     if not features:
#         st.error("Không thể lấy audio features")
#         return None
#     n = len(features)
#     return {
#         "danceability": sum(f["danceability"] for f in features) / n,
#         "energy": sum(f["energy"] for f in features) / n,
#         "tempo": sum(f["tempo"] for f in features) / n,
#         "valence": sum(f["valence"] for f in features) / n,
#         "acousticness": sum(f["acousticness"] for f in features) / n,
#         "instrumentalness": sum(f["instrumentalness"] for f in features) / n,
#     }


# playlist_urls = st.text_area(
#     "Dán nhiều link playlist Spotify (mỗi dòng 1 link):",
#     placeholder="https://open.spotify.com/playlist/...\nhttps://open.spotify.com/playlist/..."
# )

# if playlist_urls:
#     urls = [url.strip() for url in playlist_urls.splitlines() if url.strip()]
#     for playlist_url in urls:
#         if validators.url(playlist_url):
#             playlist_id = extract_playlist_id(playlist_url)
#             try:
#                 playlist = sp.playlist(playlist_id)
#                 st.write(f"**{playlist['name']}**")
#                 if playlist["images"]:
#                     st.image(playlist["images"][0]["url"], caption="Playlist")
#                 audio_stats = playlist_info(playlist)
#                 if audio_stats:
#                     st.write("**Thống kê audio:**", audio_stats)
#             except spotipy.SpotifyException as e:
#                 st.error(f"Không thể truy cập playlist: {playlist_url}")
#                 st.exception(e)
#         else:
#             st.warning(f"URL không hợp lệ: {playlist_url}")
# else:
#     st.info("Nhập URL để bắt đầu")

# CALLBACK
# query_params = st.query_params

# if "code" in query_params:
#     code = query_params["code"]

#     st.markdown(f"""
#         <meta http-equiv="refresh" content="0; url=Analysis?code={code}" />
#     """, unsafe_allow_html=True)
    
#     st.write("Đang chuyển hướng...")
# else:
#     st.error("Không tìm thấy mã truy cập.")
