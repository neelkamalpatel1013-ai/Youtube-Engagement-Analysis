"""
YouTube Social Media Engagement Data Collector — FINAL VERSION
===============================================================
✅ Quota-safe  (uses playlistItems, not search)
✅ Engagement Rate calculated
✅ Best posting time analysis
✅ Saves to CSV + SQLite (for Power BI)
"""

import sqlite3
from datetime import datetime

import pandas as pd
from googleapiclient.discovery import build

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

API_KEY    = "AIzaSyAhH1EkSuoIjKwyb-_1jROjMdEXkUKzLlE"
CHANNEL_ID = "UCSHZKyawb77ixDdsGog4iWA"
MAX_RESULTS = 50

# ─────────────────────────────────────────────
# STEP 1: Connect to YouTube API
# ─────────────────────────────────────────────

youtube = build("youtube", "v3", developerKey=API_KEY)
print("✅ Connected to YouTube API")


# ─────────────────────────────────────────────
# STEP 2: Get Video IDs via Playlist (1 quota unit — NOT search)
# ─────────────────────────────────────────────

def get_video_ids(channel_id, max_results=50):
    print("📋 Fetching video IDs from uploads playlist...")

    # Get uploads playlist ID from channel
    channel_response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    uploads_playlist_id = (
        channel_response["items"][0]["contentDetails"]
        ["relatedPlaylists"]["uploads"]
    )

    video_ids = []
    next_page_token = None

    while len(video_ids) < max_results:
        playlist_response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=min(50, max_results - len(video_ids)),
            pageToken=next_page_token
        ).execute()

        for item in playlist_response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"✅ Found {len(video_ids)} video IDs")
    return video_ids


# ─────────────────────────────────────────────
# STEP 3: Get Stats for Each Video
# ─────────────────────────────────────────────

def get_video_stats(video_ids):
    print("📊 Fetching video statistics...")

    all_videos = []

    # Process in batches of 50 (API limit)
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]

        response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch)
        ).execute()

        for item in response["items"]:
            snippet = item.get("snippet", {})
            stats   = item.get("statistics", {})

            published_at = snippet.get("publishedAt", "")
            published_dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ") if published_at else None

            views    = int(stats.get("viewCount",   0))
            likes    = int(stats.get("likeCount",   0))
            comments = int(stats.get("commentCount", 0))

            # Engagement Rate formula (from Gemini's approach)
            engagement_rate = round(((likes + comments) / views) * 100, 2) if views > 0 else 0.0

            all_videos.append({
                "Title":               snippet.get("title", "N/A"),
                "Published_At":        published_dt,
                "Publish_Day":         published_dt.strftime("%A") if published_dt else None,
                "Publish_Hour (UTC)":  published_dt.hour if published_dt else None,
                "Views":               views,
                "Likes":               likes,
                "Comments":            comments,
                "Engagement_Rate (%)": engagement_rate,
                "Fetched_At":          datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            })

    print(f"✅ Stats fetched for {len(all_videos)} videos")
    return pd.DataFrame(all_videos)


# ─────────────────────────────────────────────
# STEP 4: Best Posting Time Analysis
# ─────────────────────────────────────────────

def analyze_best_posting_times(df):
    print("🕐 Analyzing best posting times...")

    # Engagement score weights comments and likes more than raw views
    df["Engagement_Score"] = df["Views"] + (df["Likes"] * 10) + (df["Comments"] * 20)

    # Best day to post
    best_days = (
        df.groupby("Publish_Day")["Engagement_Score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Publish_Day": "Day", "Engagement_Score": "Avg_Engagement_Score"})
    )
    best_days["Avg_Engagement_Score"] = best_days["Avg_Engagement_Score"].round(0)

    # Best hour to post
    best_hours = (
        df.groupby("Publish_Hour (UTC)")["Engagement_Score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Publish_Hour (UTC)": "Hour_UTC", "Engagement_Score": "Avg_Engagement_Score"})
    )
    best_hours["Avg_Engagement_Score"] = best_hours["Avg_Engagement_Score"].round(0)

    return best_days, best_hours


# ─────────────────────────────────────────────
# STEP 5: Save to CSV + SQLite
# ─────────────────────────────────────────────

def save_data(df, best_days, best_hours):

    # Main data CSV (for Power BI)
    df.to_csv("youtube_engagement.csv", index=False)
    print("✅ Saved → youtube_engagement.csv")

    # Analysis CSVs (for Power BI recommendation cards)
    best_days.to_csv("best_days_to_post.csv", index=False)
    best_hours.to_csv("best_hours_to_post.csv", index=False)
    print("✅ Saved → best_days_to_post.csv")
    print("✅ Saved → best_hours_to_post.csv")

    # SQLite DB (direct Power BI connection possible)
    conn = sqlite3.connect("youtube_engagement.db")
    df.to_sql("video_stats",   conn, if_exists="replace", index=False)
    best_days.to_sql("best_days",   conn, if_exists="replace", index=False)
    best_hours.to_sql("best_hours", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Saved → youtube_engagement.db (3 tables)")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 YouTube Engagement Data Collection Starting...\n")

    ids                  = get_video_ids(CHANNEL_ID, MAX_RESULTS)
    df                   = get_video_stats(ids)
    best_days, best_hours = analyze_best_posting_times(df)
    best_hours = best_hours.sort_values("Avg_Engagement_Score", ascending=False).reset_index(drop=True)
    best_days = best_days.sort_values("Avg_Engagement_Score", ascending=False).reset_index(drop=True)

# Add rank column instead of relying on Hour_UTC
    best_hours.insert(0, "Rank", range(1, len(best_hours) + 1))
    best_hours["Label"] = "Hour " + best_hours["Hour_UTC"].astype(str)
    best_days.insert(0, "Rank", range(1, len(best_days) + 1))
    save_data(df, best_days, best_hours)

    # Print summary
    print("\n" + "="*50)
    print("📌 TOP 5 MOST ENGAGING VIDEOS")
    print("="*50)
    print(df[["Title", "Views", "Likes", "Comments", "Engagement_Rate (%)"]].head())

    print("\n" + "="*50)
    print("📅 BEST DAYS TO POST")
    print("="*50)
    print(best_days.to_string(index=False))

    print("\n" + "="*50)
    print("⏰ TOP 5 BEST HOURS TO POST (UTC)")
    print("="*50)
    print(best_hours.head(5).to_string(index=False))

    print("\n🎉 Done! Import the CSV files or .db file into Power BI.\n")