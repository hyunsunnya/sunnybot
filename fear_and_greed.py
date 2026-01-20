import requests
import yfinance as yf
import asyncio
import time
from telegram import Bot

# --- [사용자 설정값] ---
# ⚠️ 본인의 토큰과 ID를 다시 한번 확인하세요.
TELEGRAM_TOKEN = '7874043423:AAEtpCMnZpG9lOzMHfwd1LxumLiAB-_oNAw'
CHANNEL_ID = '-1003685297139' 

def get_cnn_fgi():
    """
    CNN Fear & Greed 지수 가져오기
    URL 뒤에 타임스탬프를 붙여 서버 캐시를 우회합니다.
    """
    timestamp = int(time.time())
    url = f"https://production.dataviz.cnn.io/index/fear_and_greed/graphdata?_={timestamp}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.cnn.com/markets/fear-and-greed"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # 현재 지수와 등급 추출
        score = data['fear_and_greed']['score']
        rating = data['fear_and_greed']['rating']
        return score, rating
    except Exception as e:
        print(f"❌ CNN 데이터 가져오기 실패: {e}")
        return None, None

def get_price(ticker):
    """
    주식 가격 가져오기
    fast_info 대신 history를 사용하여 실시간성에 가까운 종가를 가져옵니다.
    """
    try:
        stock = yf.Ticker(ticker)
        # 최신 1일치 데이터를 가져옴
        df = stock.history(period="1d")
        if not df.empty:
            return df['Close'].iloc[-1]
        else:
            # history 실패 시 fast_info로 백업
            return stock.fast_info['last_price']
    except Exception as e:
        print(f"❌ {ticker} 가격 가져오기 실패: {e}")
        return 0

async def send_message(text):
    """텔레그램 채널로 메시지 전송"""
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=text)

async def main():
    print(f"🚀 분석 시작: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 데이터 수집
        score, rating = get_cnn_fgi()
        if score is None:
            return

        spy_price = get_price("SPY")
        tiger_price = get_price("360750.KS")
        
        # 2. 메시지 구성
        status = (
            f"📊 [실시간 시장 지표 보고서]\n\n"
            f"🔥 탐욕 지수: {score:.2f} ({rating.upper()})\n"
            f"🇺🇸 SPY (미국): ${spy_price:.2f}\n"
            f"🇰🇷 TIGER S&P500: {int(tiger_price):,}원\n\n"
            f"🕒 업데이트: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"※ 이 알림은 특정 구간(40이하/60이상)에서만 발송됩니다."
        )

        # 3. 전송 조건 검사
        should_send = False
        headline = ""

        if score <= 40:
            headline = "🚨🐣 [매수 기회] 시장이 공포에 빠졌습니다! 😎💵"
            should_send = True
        elif score >= 60:
            headline = "💰🐥 [매도 주의] 시장이 과열되었습니다! 😘💸"
            should_send = True
        else:
            print(f"😴 현재 지수 {score:.2f}: 중립 구간 (41~59)이므로 전송을 건너뜁니다.")

        # 4. 최종 전송
        if should_send:
            final_msg = f"{headline}\n\n{status}"
            await send_message(final_msg)
            print(f"📱 메시지 전송 완료! (지수: {score:.2f})")

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
