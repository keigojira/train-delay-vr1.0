import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os
import asyncio

TOKEN = os.getenv("TOKEN")  # .env から取得
CHANNEL_ID = 1339804956374335488
CHECK_INTERVAL = 10  # 分

TARGET_LINES = ['横須賀線', '東海道線', '湘南新宿ライン']

藤沢起点_駅リスト = {
    '東海道線': ['東京', '新橋', '品川', '川崎', '横浜', '戸塚', '大船', '藤沢', '辻堂', '茅ヶ崎', '平塚', '大磯', '二宮', '国府津', '鴨宮'],
    '横須賀線': ['東京', '新橋', '品川', '西大井', '新川崎', '横浜', '保土ヶ谷', '東戸塚', '戸塚', '大船', '北鎌倉', '鎌倉', '逗子', '東逗子', '田浦'],
    '湘南新宿ライン': ['大宮', '浦和', '赤羽', '池袋', '新宿', '渋谷', '恵比寿', '大崎', '西大井', '新川崎', '武蔵小杉', '横浜', '戸塚', '大船', '藤沢']
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

previous_delays = set()

def fetch_delay_info():
    url = 'https://transit.yahoo.co.jp/traininfo/area/4/'
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
            return '藤沢' in stations
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

@bot.event
async def on_ready():
    print(f"✅ Botが起動しました！ユーザー: {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🚅 テストメッセージ：Botは正常に動作しています！")
    check_delay_loop.start()

@tasks.loop(minutes=CHECK_INTERVAL)
async def check_delay_loop():
    channel = bot.get_channel(CHANNEL_ID)
    current_delays = fetch_delay_info()
    new_delays, recovered = compare_delay_changes(current_delays)

    for line, info in new_delays:
        await channel.send(f'🚨【遅延情報】{line}：{info}')
    for line in recovered:
        await channel.send(f'✅【運転再開】{line}：現在は平常通り運行中です')

# ✅ テストコマンド
@bot.command()
async def test(ctx):
    await ctx.send("✅ テスト成功！Botは動作しています。")

bot.run(TOKEN)
