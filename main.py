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


# ----- 6レース終了時分析（最終評価軸に完全対応） -----
@bot.command()
async def check(ctx, mid_score: int, mid_rank: int = 0, room_type: str = "normal"):
    title_text = f"📊 6レース終了時分析: {mid_score}点"
    if mid_rank > 0:
        title_text += f" / {mid_rank}位"

    embed = discord.Embed(title=title_text)

    if mid_score >= 60:
        embed.color = discord.Color.purple()
        embed.add_field(
            name="状態: ⚡ 神レベルペース（60点以上）",
            value=(
                "・120点超え（圧倒的無双）が十分狙える神ペース！\n"
                "・無理な突っ込みだけ避け、今の前張り／打開のテンポを維持。\n"
                "・**目標**: 後半も60点近く積み上げて無双狙い！"
            ),
            inline=False,
        )
    elif mid_score >= 50:
        embed.color = discord.Color.green()
        embed.add_field(
            name="状態: 🔥 圧勝級ペース（50〜59点）",
            value=(
                "・100点超え（圧勝級）を狙える大チャンス！\n"
                "・無駄な事故を避け、確実に上位〜中位上位でまとめよう。\n"
                "・**目標**: 後半50点以上稼いで100点オーバー達成！"
            ),
            inline=False,
        )
    elif mid_score >= 43:
        embed.color = discord.Color.blue()
        embed.add_field(
            name="状態: 💪 好成績ペース（43〜49点）",
            value=(
                "・85点以上の『かなりすごい（好成績）』ラインが目の前！\n"
                "・中位混戦に巻き込まれたら即アイテム確保＋コイン10枚へ切り替え。\n"
                "・**目標**: 後半42点以上稼いで85〜95点オーバーを確保！"
            ),
            inline=False,
        )
    elif mid_score >= 36:
        embed.color = discord.Color.gold()
        embed.add_field(
            name="状態: ⚖️ 平均・ボーダーペース（36〜42点）",
            value=(
                "・後半でしっかり巻き返せば72点（勝ち越しライン）を十分確保可能！\n"
                "・1位を狙いすぎて事故るより、泥臭く6〜8点（12位以上）を確実に拾う。\n"
                "・**目標**: 後半36点以上キープで72点以上を守り切る！"
            ),
            inline=False,
        )
    else:
        embed.color = discord.Color.red()
        embed.add_field(
            name="状態: ⚠️ 平均以下警告（35点以下）",
            value=(
                "・前追いはリスク大！全レース『完全打開（コイン10枚＋強無敵）』徹底！\n"
                "・目的を大勝ちから『マイナス（大ドカン）を最小限に抑える作業』に変更。\n"
                "・**目標**: 後半最低37点以上を死守して72点ボーダーまで押し戻す！"
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


# ----- 12レース最終結果 & 予想MMR -----
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
        msg = "✨ 大勝ちです！上位キープと安定感が素晴らしすぎます。"
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
