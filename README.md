# 🎙️ YouTube Engagement Analytics: Lex Fridman Podcast

An end-to-end data pipeline and interactive Power BI dashboard analyzing the performance, engagement rates, and optimal posting schedules for the Lex Fridman YouTube channel.

## 📌 Project Overview
This project extracts real-world social media data using the official YouTube Data API (v3), processes the metrics using Python and Pandas, and visualizes the insights through a custom-designed, highly interactive Power BI dashboard. It analyzes the latest 50 episodes, encompassing over 52 Million total views, to uncover what drives audience engagement.

## 🛠️ Tools & Technologies Used
* **Data Extraction:** Python 3, Google YouTube Data API (v3)
* **Data Transformation:** Pandas
* **Database/Storage:** SQLite3, CSV
* **Data Visualization:** Power BI Desktop, DAX, Custom Visuals (Chiclet Slicer)
* **UI/UX Design:** Custom dark-theme aesthetics, F-Pattern layout, custom canvas backgrounds

## ⚙️ The Data Pipeline
The data extraction is handled by `yt_api.py`, a quota-safe script that:
1. Connects to the YouTube API and retrieves the channel's upload playlist.
2. Extracts statistics (Views, Likes, Comments, Publish Dates) for the latest 50 videos.
3. Calculates a custom **Engagement Rate (%)** metric: `((Likes + Comments) / Views) * 100`.
4. Analyzes the dataset to determine the best historical days and hours to post based on an average engagement score.
5. Exports the cleaned, transformed data into both `.csv` and a local SQLite database (`.db`) for seamless Power BI integration.

## 📈 Dashboard Features & Insights
The Power BI dashboard (`yt engagement dashboard.pbix`) was built with a focus on premium UI/UX design and actionable analytics.
* **App-Style Interface:** Features a dedicated left-hand navigation pane using a Chiclet Slicer for instant, dashboard-wide cross-filtering by video title.
* **Dynamic KPIs:** Tracks Total Views (52M+), Total Videos, Average Views (1.05M), and overall Engagement Rate (2.29%).
* **Temporal Analysis:** Identifies peak audience activity, revealing the specific days (e.g., Sunday) and times (e.g., 11:00 AM UTC) that yield the highest engagement.
* **Conversion Funnels & Trends:** Visualizes month-over-month view fluctuations and compares individual episode performance through customized, decluttered bar charts.

## 📂 Repository File Structure
* `yt_api.py` - The main Python script for API data extraction and transformation.
* `youtube_engagement.csv` - The primary dataset containing episode-level statistics.
* `best_days_to_post.csv` - Aggregated data ranking the best days for engagement.
* `best_hours_to_post.csv` - Aggregated data ranking the best hours (UTC) for engagement.
* `youtube_engagement.db` - The SQLite database containing all generated tables.
* `yt engagement dashboard.pbix` - The final interactive Power BI dashboard file.

## 🚀 How to Run the Project
1. **Data Collection:** Clone the repository and run `python yt_api.py`. *(Note: You will need to supply your own YouTube Data API key in the script).*
2. **Dashboard Viewing:** Open the `yt engagement dashboard.pbix` file using Power BI Desktop.
3. **Data Refresh:** In Power BI, change the data source settings to point to the newly generated local `.csv` or `.db` files, and click "Refresh" to load the latest data.
