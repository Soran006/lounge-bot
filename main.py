import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# ----- Render常時稼働用 -----
app = Flask("")


@app.route("/")
def home():
    return "Bot is alive!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ----- Discord Bot本体 -----
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 得意コース記憶用
good_courses = []


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


# ----- 6レース終了時分析 -----
@bot.command()
async def check(ctx, mid_score: int, mid_rank: int, room_type: str = "normal"):
    embed = discord.Embed(
        title=f"📊 6レース終了時分析: {mid_score}点 / {mid_rank}位",
        color=discord.Color.blue(),
    )

    if mid_score >= 65:
        embed.color = discord.Color.green()
        embed.add_field(
            name="状態: EXCELLENT（爆盛れペース）",
            value=(
                "・後半も今の前張り／打開のバランスを維持。\n"
                "・中位数位での強引な突っ込みだけ注意！\n"
                "・**目標**: 後半も50〜60点以上積み上げて120点超え！"
            ),
            inline=False,
        )
    elif mid_score >= 45:
        embed.color = discord.Color.blue()
        embed.add_field(
            name="状態: GOOD（勝ち越しペース）",
            value=(
                "・無駄なリスクは不要。事故ったらコンマ1秒で24位まで下がる。\n"
                "・中位に巻き込まれたら即アイテム溜め（コイン10枚＋無敵）にシフト。\n"
                "・**目標**: 後半で40〜50点稼ぎ、全体8位以内（85〜95点以上）を確保！"
            ),
            inline=False,
        )
    elif mid_score >= 30:
        embed.color = discord.Color.gold()
        embed.add_field(
            name="状態: WARNING（警戒・事故防止優先）",
            value=(
                "・前追いはリスク大。事故時の即降下を徹底。\n"
                "・1位狙いではなく『12位以上（6点以上）』を泥臭く拾う立ち回りへ。\n"
                "・**目標**: 後半40点稼ぎ、平均ライン（75点付近）まで押し戻す！"
            ),
            inline=False,
        )
    else:
        embed.color = discord.Color.red()
        embed.add_field(
            name="状態: DANGER（大炎上アラート・被害最小限へ）",
            value=(
                "・前張り一切禁止。全レース『完全打開（コイン10枚＋強無敵）』徹底！\n"
                "・目的を130点から『-200オーバーのドカンを回避する作業』に変更。\n"
                "・**目標**: 後半最低35〜40点を死守し、合計65〜70点（傷口最小限）で耐える！"
            ),
            inline=False,
        )

    if room_type.lower() in ["lower", "下格"]:
        embed.add_field(
            name="⚠️ 下格部屋警告",
            value="中位のデスゾーンは絶対に避けてください。事故ったら即座に24位まで下がり切ること！",
            inline=False,
        )

    await ctx.send(embed=embed)


# ----- 12レース最終結果 & 予想MMR（画像基準に完全最適化） -----
@bot.command()
async def result(ctx, final_score: int, final_rank: int = 0):
    if final_score >= 120:
        eval_title = "⚡ 神レベル（圧倒的無双）"
        est_mmr = "+180 〜 +250"
        msg = "👑 完璧なレース運び！部屋を完全に支配しましたね。この調子で盛りまくりましょう！"
        color_val = discord.Color.purple()
    elif final_score >= 100:
        eval_title = "🔥 めちゃくちゃすごい（圧勝級）"
        est_mmr = "+120 〜 +180"
        msg = "✨ 大勝収です！上位キープと安定感が素晴らしすぎます。"
        color_val = discord.Color.green()
    elif final_score >= 85:
        eval_title = "💪 かなりすごい（好成績）"
        est_mmr = "+60 〜 +120"
        msg = "👍 しっかりプラスを確保！勝ち越し成功です！"
        color_val = discord.Color.blue()
    elif final_score >= 72:
        eval_title = "⚖️ 平均〜勝ち越し"
        est_mmr = "-20 〜 +50"
        msg = "👌 ボーダーライン越え！しっかり耐えてプラス領域を守り切りました。"
        color_val = discord.Color.gold()
    else:
        eval_title = "📉 平均以下"
        est_mmr = "-150 〜 -30"
        msg = "⚠️ 苦しいマッチでした...。次は打開重視で着実に点数を拾っていきましょう！"
        color_val = discord.Color.red()

    title_text = f"🏁 12レース最終結果: {final_score}点"
    if final_rank > 0:
        title_text += f" / {final_rank}位"

    embed = discord.Embed(title=title_text, color=color_val)
    embed.add_field(name="🏆 評価", value=f"**{eval_title}**", inline=False)
    embed.add_field(name="📈 予想MMR変動", value=f"**{est_mmr} MMR**", inline=False)
    embed.add_field(name="💬 コメント", value=msg, inline=False)

    await ctx.send(embed=embed)


# ----- 得意コース登録 -----
@bot.command()
async def good(ctx, *, course_name: str):
    if course_name not in good_courses:
        good_courses.append(course_name)
        await ctx.send(f"✅ 得意コースに **【{course_name}】** を追加しました！")
    else:
        await ctx.send(f"💡 **【{course_name}】** はすでに登録されています。")


# ----- 得意コース一覧表示 -----
@bot.command()
async def goodlist(ctx):
    if not good_courses:
        await ctx.send(
            "登録されている得意コースはまだありません。\n`!good コース名` で追加してね！"
        )
    else:
        courses_str = "\n・".join(good_courses)
        embed = discord.Embed(
            title="🏆 勝率の良い得意コース一覧",
            description=f"・{courses_str}",
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)


keep_alive()

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
