import requests
import yfinance as yf
import asyncio
from telegram import Bot

# --- [사용자 설정값] ---
TELEGRAM_TOKEN = '7874043423:AAEtpCMnZpG9lOzMHfwd1LxumLiAB-_oNAw'
CHANNEL_ID = '-1003685297139' 

def get_cnn_fgi():
    """CNN Fear & Greed 지수 가져오기"""
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.cnn.com/markets/fear-and-greed"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"CNN 접근 실패: {res.status_code}")
    data = res.json()
    score = data['fear_and_greed']['score']
    rating = data['fear_and_greed']['rating']
    return score, rating

def get_price(ticker):
    """주식 가격 가져오기 (미국/한국 공용)"""
    stock = yf.Ticker(ticker)
    return stock.fast_info['last_price']

async def send_message(text):
    """텔레그램 채널로 메시지 전송"""
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=text)

async def main():
    print("🚀 데이터 분석 및 조건 검사 시작...")
    try:
        # 1. 데이터 수집
        score, rating = get_cnn_fgi()
        spy_price = get_price("SPY")
        tiger_price = get_price("360750.KS")
        
        # 2. 메시지 구성 (기본 지표 정보)
        status = f"📊 [실시간 Fear & Greed 보고서]\n\n" \
                 f"🔥 탐욕 지수: {score:.2f} ({rating.upper()})\n\n" \
                 f"🇺🇸 SPY (미국): ${spy_price:.2f}\n" \
                 f"🇰🇷 TIGER 미국S&P500: {int(tiger_price):,}원\n\n" \
                 f"※ 이 알림은 특정 구간에만 자동 발송됩니다."

        # 3. 전송 조건 검사 (40 이하 또는 60 이상)
        should_send = False
        headline = ""

        if score <= 40:
            headline = "🚨🐣 매수 포인트 포착! 😎💵"
            should_send = True
        elif score >= 60:
            headline = "💰🐥 매도 포인트 포착! 😘💸"
            should_send = True
        else:
            # 40 < score < 60 구간
            print(f"😴 현재 지수 {score:.2f}: 관망 구간이므로 메시지를 보내지 않습니다.")

        # 4. 최종 전송
        if should_send:
            final_msg = f"{headline}\n\n{status}"
            await send_message(final_msg)
            print(f"📱 전송 완료! (지수: {score:.2f})")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
