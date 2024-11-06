import os
import requests
import matplotlib.pyplot as plt
from openai import OpenAI
from collections import Counter
import time

# OpenAIクライアントの設定
client = OpenAI()
client.api_key = os.getenv('OPENAI_API_KEY')

if not client.api_key:
    raise ValueError("環境変数 'OPENAI_API_KEY' が設定されていません。")

def fetch_diet_records(year):
    """
    指定年の国会会議録を取得する関数。
    会議録の議事内容（発言内容）を含むデータを取得します。
    """
    url = f'https://kokkai.ndl.go.jp/api/meeting'
    params = {
        'recordPacking': 'json',
        'maximumRecords': 10,  # 一度に10件まで取得可能
        'startRecord': 1,
        'from': f'{year}-01-01',
        'until': f'{year}-12-31'
    }
    records = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            break
        data = response.json().get('meetingRecord', [])
        if not data:
            break
        records.extend(data)
        
        # 次の開始位置を設定
        params['startRecord'] += len(data)
        
        # APIアクセスの間に少し待機
        time.sleep(1)
        
    return records

def extract_topics(speech_text):
    """
    OpenAI APIを使って発言内容から主要トピックを抽出し、マークダウン形式で保存。
    """
    prompt = f"以下の発言内容から主要な政策トピックを抽出してください:\n\n{speech_text}\n\nトピック:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは政策分析に精通した専門家です。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.5
    )
    topics = response.choices[0].message.content.strip().split(', ')
    
    # トピックをマークダウン形式で保存
    with open("diet_topics_summary.md", "a", encoding="utf-8") as file:
        file.write(f"### 発言内容\n{speech_text}\n\n")
        file.write(f"**抽出されたトピック**: {', '.join(topics)}\n\n")
    
    return topics

def analyze_trends(records):
    """
    取得した会議録データを使って発言内容からトピックを分析し、出現頻度をカウントする。
    """
    topic_counter = Counter()
    for record in records:
        for speech in record.get('speechRecord', []):
            speech_text = speech.get('speech', '')
            if speech_text:
                topics = extract_topics(speech_text)
                topic_counter.update(topics)
    return topic_counter

def plot_trend_map(topic_counter, year):
    """
    トピックの頻度を可視化するためのグラフを生成する。
    """
    topics, counts = zip(*topic_counter.most_common(10))
    
    plt.figure(figsize=(10, 6))
    plt.barh(topics, counts, color='skyblue')
    plt.xlabel("発言回数")
    plt.ylabel("トピック")
    plt.title(f"{year}年の国会議論トレンドマップ")
    plt.gca().invert_yaxis()  # 項目を上位順で表示
    plt.show()

def main(year):
    """
    指定年の国会会議録データを取得し、トレンドマップを作成するメイン関数。
    """
    # マークダウンファイルの初期化
    with open("diet_topics_summary.md", "w", encoding="utf-8") as file:
        file.write(f"# {year}年の国会議事録 トピック要約\n\n")

    records = fetch_diet_records(year)
    if not records:
        print(f"{year}年のデータが見つかりませんでした。")
        return

    topic_counter = analyze_trends(records)
    plot_trend_map(topic_counter, year)

# 実行例: 2024年のトレンドマップ作成
main(2024)
