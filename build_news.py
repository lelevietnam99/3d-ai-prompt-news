import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
import re
from deep_translator import GoogleTranslator

# 1. Nguồn tin tập trung vào AI (OpenAI, Google, TechCrunch AI, 80 Level)
FEEDS = {
    "OpenAI (ChatGPT Updates)": "https://openai.com/news/rss.xml",
    "Google Blog (Gemini AI)": "https://blog.google/technology/ai/rss/",
    "TechCrunch (AI News)": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "80 Level (AI & 3D Tech)": "https://80.lv/articles.rss"
}

# 2. Hệ thống Thẻ Chủ đề theo yêu cầu mới
TOPICS = {
    "Tính Năng Mới": ['claude 3.5', 'gpt-4o', 'gemini 1.5', 'update', 'new feature', 'release', 'announcing'],
    "Kỹ Thuật Prompt": ['prompt engineering', 'prompting', 'best practices', 'how to write', 'guide'],
    "AI Làm Phim & 3D": ['3d', 'video generation', 'kling', 'sora', 'runway', 'render', 'animation']
}

def get_clean_summary(html_content, max_length=300):
    if not html_content: return "Không có mô tả."
    soup = BeautifulSoup(html_content, "html.parser")
    # Loại bỏ các thẻ rác nếu có
    for s in soup(['script', 'style']): s.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return text[:max_length] + "..." if len(text) > max_length else text

def extract_topics(text):
    found_topics = set()
    text_lower = text.lower()
    for topic, keywords in TOPICS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                found_topics.add(topic)
                break
    return list(found_topics)

def translate_to_vi(text):
    try:
        if not text or text.isspace(): return ""
        # Chia nhỏ đoạn văn nếu quá dài để tránh lỗi API
        return GoogleTranslator(source='auto', target='vi').translate(text)
    except:
        return text

# 3. Giao diện HTML tập trung vào sự tối giản và thẻ tag
html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI & 3D Filmmaking News - Chuyên sâu Prompt</title>
    <style>
        body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; background-color: #f8f9fa; color: #212529; line-height: 1.6; padding: 20px; }}
        .container {{ max-width: 850px; margin: auto; }}
        header {{ text-align: center; padding: 40px 0; background: linear-gradient(135deg, #2c3e50, #4ca1af); color: white; border-radius: 15px; margin-bottom: 30px; }}
        .feed-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 25px; }}
        .source-name {{ color: #4ca1af; font-size: 0.9em; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
        .news-item {{ border-bottom: 1px solid #edf2f7; padding: 20px 0; }}
        .news-item:last-child {{ border-bottom: none; }}
        .news-title {{ font-size: 1.3em; color: #2d3748; text-decoration: none; font-weight: 700; display: block; margin-bottom: 10px; }}
        .news-title:hover {{ color: #4ca1af; }}
        .summary-vi {{ color: #4a5568; margin-bottom: 12px; }}
        .tag-container {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }}
        .tag {{ padding: 4px 12px; border-radius: 6px; font-size: 0.75em; font-weight: 600; }}
        .tag-new {{ background: #ebf8ff; color: #2b6cb0; }}
        .tag-prompt {{ background: #fefcbf; color: #744210; }}
        .tag-3d {{ background: #faf5ff; color: #553c9a; }}
        .meta {{ font-size: 0.8em; color: #a0aec0; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Cập Nhật AI & Prompt Làm Phim</h1>
            <p>Dành riêng cho dự án Phim 3D Đức Phật | {datetime.now().strftime("%d/%m/%Y")}</p>
        </header>
"""

for site_name, url in FEEDS.items():
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            html_content += f'<div class="feed-card"><div class="source-name">{site_name}</div>'
            for entry in feed.entries[:4]:
                t_eng = entry.title
                link = entry.link
                raw_summary = entry.get('summary', entry.get('description', ''))
                s_eng = get_clean_summary(raw_summary)
                
                # Phân loại và Dịch
                topics = extract_topics(t_eng + " " + s_eng)
                t_vi = translate_to_vi(t_eng)
                s_vi = translate_to_vi(s_eng)
                
                tags_html = '<div class="tag-container">'
                for tp in topics:
                    cls = "tag-new" if tp == "Tính Năng Mới" else ("tag-prompt" if tp == "Kỹ Thuật Prompt" else "tag-3d")
                    tags_html += f'<span class="tag {cls}">#{tp.replace(" ", "_")}</span>'
                tags_html += '</div>'

                html_content += f"""
                <div class="news-item">
                    {tags_html}
                    <a class="news-title" href="{link}" target="_blank">{t_vi}</a>
                    <div class="summary-vi">{s_vi}</div>
                    <div class="meta">Nguồn gốc: {t_eng}</div>
                </div>
                """
            html_content += '</div>'
    except Exception as e:
        print(f"Lỗi tại {site_name}: {e}")

html_content += """
        <footer style="text-align: center; color: #a0aec0; padding: 20px;">
            Dữ liệu được cập nhật tự động phục vụ nghiên cứu phim 3D.
        </footer>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
