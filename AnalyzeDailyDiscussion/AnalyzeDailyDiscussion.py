import os
import requests
from openai import OpenAI
from collections import Counter, defaultdict
from tqdm import tqdm
import time

# OpenAIクライアントの設定
client = OpenAI()
client.api_key = os.getenv('OPENAI_API_KEY')

if not client.api_key:
    raise ValueError("環境変数 'OPENAI_API_KEY' が設定されていません。")

def fetch_diet_records(year, month):
    """
    指定年と月の国会会議録を取得し、日ごとの発言内容をまとめる関数。
    """
    url = f'https://kokkai.ndl.go.jp/api/meeting'
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-31"  # 月末日付（安全のため31日まで指定）
    params = {
        'recordPacking': 'json',
        'maximumRecords': 10,  # 一度に10件まで取得可能
        'startRecord': 1,
        'from': start_date,
        'until': end_date
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

def split_text(text, max_length=2000):
    """
    テキストを指定した文字数（max_length）以内の部分に分割する関数。
    """
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def extract_topics(speech_text, date):
    """
    OpenAI APIを使って分割された発言内容から主要トピックとその概要を抽出。
    """
    all_topics = []
    speech_parts = split_text(speech_text, max_length=2000)

    for part in speech_parts:
        prompt = f"以下は、{date}に行われた国会答弁の一部です。主要な政策トピックとその概要を抽出してください:\n\n{part}\n\nトピック:"
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
        all_topics.extend(topics)

    return list(set(all_topics))

def analyze_trends(records, year, month):
    """
    日ごとの発言内容を分析し、トピックを日ごとにマークダウンファイルとして保存。
    """
    for date, speeches in tqdm(records.items(), desc="Processing daily records"):
        topics = extract_topics(speeches, date)

        # 日付ごとのトピックを要約としてマークダウンファイルに保存
        output_filename = f"{date}.md"
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(f"# {date}の国会議事録 トピック要約\n\n")
            file.write(f"**抽出されたトピック**: {', '.join(topics)}\n\n")

    print(f"日ごとのトピック要約を .md ファイルに出力しました。")

def main(year, month):
    """
    指定年と月の国会会議録データを取得し、日ごとのトピック要約を出力するメイン関数。
    """
    records = fetch_diet_records(year, month)
    if not records:
        print(f"{year}年{month}月のデータが見つかりませんでした。")
        return

    analyze_trends(records, year, month)

# 実行例: 2024年3月の日ごとのトピック要約作成
main(2024, 3)
