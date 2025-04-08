import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import os

# ================== 設定 =====================
TOKEN = os.getenv('TOKEN')  # .envから読み取るように変更
CHANNEL_ID = 1339804956374335488   # ← 通知先チャンネルのIDに置き換えて！
CHECK_INTERVAL = 10  # 分ごとに確認

TARGET_LINES = ['横須賀線', '東海道線', '湘南新宿ライン']

藤沢起点_駅リスト = {
    '東海道線': ['東京', '新橋', '品川', '川崎', '横浜', '戸塚', '大船', '藤沢', '辻堂', '茅ヶ崎', '平塚', '大磯', '二宮', '国府津', '鴨宮'],
    '横須賀線': ['東京', '新橋', '品川', '西大井', '新川崎', '横浜', '保土ヶ谷', '東戸塚', '戸塚', '大船', '北鎌倉', '鎌倉', '逗子', '東逗子', '田浦'],
    '湘南新宿ライン': ['大宮', '浦和', '赤羽', '池袋', '新宿', '渋谷', '恵比寿', '大崎', '西大井', '新川崎', '武蔵小杉', '横浜', '戸塚', '大船', '藤沢']
}

# ================ Bot 起動 =====================
intents = discord.Intents.default()
client = discord.Client(intents=intents)

previous_delays = set()

def fetch_delay_info():
    url = 'https://transit.yahoo.co.jp/traininfo/area/4/'  # JR東日本（関東）エリア
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    delays = []

    for trouble in soup.select('.trouble > dl'):
        line_name = trouble.select_one('dt').text.strip()
        if any(target in line_name for target in TARGET_LINES):
            if is_near_fujisawa(line_name):
                info = trouble.select_one('dd').text.strip()
                delays.append((line_name, info))

    return delays

def is_near_fujisawa(line_name):
    for route_name, stations in 藤沢起点_駅リスト.items():
        if route_name in line_name:
            try:
                idx = stations.index('藤沢')
                return True  # 藤沢が含まれていればOK（簡易実装）
            except ValueError:
                continue
    return False

def compare_delay_changes(current_delays):
    global previous_delays
    new_delays = []
    recovered_lines = []

    current_lines = set(line for line, _ in current_delays)

    for line, info in current_delays:
        if line not in previous_delays:
            new_delays.append((line, info))

    for line in previous_delays:
        if line not in current_lines:
            recovered_lines.append(line)

    previous_delays = current_lines
    return new_delays, recovered_lines

async def notify_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        current_delays = fetch_delay_info()
        new_delays, recovered = compare_delay_changes(current_delays)

        for line, info in new_delays:
            await channel.send(f'🚨【遅延情報】{line}：{info}')

        for line in recovered:
            await channel.send(f'✅【運転再開】{line}：現在は平常通り運行中です')

        await asyncio.sleep(CHECK_INTERVAL * 60)

@client.event
async def on_ready():
    print(f'✅ Bot起動成功: {client.user.name}')
    client.loop.create_task(notify_loop())

client.run(TOKEN)

@client.event
async def on_ready():
    print(f"✅ Botが起動しました！ユーザー: {client.user}")  # ログに起動を表示
    channel = client.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send("🚅 テストメッセージ：Botは正常に動作しています！")
    else:
        print("❌ チャンネルが見つかりませんでした。CHANNEL_IDを確認してください。")

import discord
import requests
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容にアクセスするためのインテントを有効にする

client = discord.Client(intents=intents)

# 遅延情報を取得する関数
def get_delay_info():
    # 実際の遅延情報のページにアクセスする（仮にURLを設定しています）
    url = "https://example.com/delay-info"  # 実際の遅延情報のURLに変更してください
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 適切なHTML要素を検索し、遅延情報を取得（仮の要素として「.delay-status」を指定）
    delay_info = soup.find(class_="delay-status")  # 適切なクラス名を使用してください

    if delay_info:
        return delay_info.text.strip()
    else:
        return "遅延情報が見つかりませんでした。"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # ボット自身のメッセージには反応しない

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')  # メッセージに反応して送信

    elif message.content.startswith('!delay'):
        delay_info = get_delay_info()  # 遅延情報を取得
        await message.channel.send(f"現在の遅延情報: {delay_info}")  # 遅延情報を送信

client.run('YOUR_BOT_TOKEN')  # ボットのトークンをここに設定


