import os
import requests
import matplotlib.pyplot as plt
from openai import OpenAI
from collections import Counter, defaultdict
from tqdm import tqdm
import time

# OpenAIクライアントの設定
client = OpenAI()
client.api_key = os.getenv('OPENAI_API_KEY')

if not client.api_key:
    raise ValueError("環境変数 'OPENAI_API_KEY' が設定されていません。")

def fetch_diet_records(year):
    """
    指定年の国会会議録を取得し、日ごとの発言内容をまとめる関数。
    """
    url = f'https://kokkai.ndl.go.jp/api/meeting'
    params = {
        'recordPacking': 'json',
        'maximumRecords': 10,  # 一度に10件まで取得可能
        'startRecord': 1,
        'from': f'{year}-01-01',
        'until': f'{year}-12-31'
    }
    records = defaultdict(str)
    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            break
        data = response.json().get('meetingRecord', [])
        if not data:
            break

        for record in data:
            date = record.get('date')
            speeches = record.get('speechRecord', [])
            for speech in speeches:
                records[date] += speech.get('speech', '') + "\n"
        
        params['startRecord'] += len(data)
        time.sleep(1)
    
    return records

def extract_topics(speech_text, date):
    """
    OpenAI APIを使って日ごとの発言内容から主要トピックを抽出し、マークダウン形式で保存。
    """
    prompt = f"以下は、{date}に行われた発言の内容です。主要な政策トピックを抽出してください:\n\n{speech_text}\n\nトピック:"
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
        file.write(f"### 日付: {date}\n")
        file.write(f"**抽出されたトピック**: {', '.join(topics)}\n\n")
    
    return topics

def analyze_trends(records):
    """
    日ごとの発言内容をOpenAI APIに渡してトピックを分析し、出現頻度をカウントする。
    tqdmで進捗を表示。
    """
    topic_counter = Counter()
    for date, speeches in tqdm(records.items(), desc="Processing daily records"):
        topics = extract_topics(speeches, date)
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
