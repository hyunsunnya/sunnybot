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

def get_spy_price():
    """현재 SPY 가격 가져오기"""
    spy = yf.Ticker("SPY")
    return spy.fast_info['last_price']

async def send_message(text):
    """텔레그램 채널로 메시지 전송"""
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=text)

async def main():
    print("🚀 데이터 분석 및 채널 방송 준비 중...")
    try:
        score, rating = get_cnn_fgi()
        price = get_spy_price()
        
        status = f"📊 [실시간 FGI 투자 지표]\n\n" \
                 f"📌 탐욕 지수: {score:.2f} ({rating.upper()})\n" \
                 f"💵 SPY 가격: ${price:.2f}\n\n" \
                 f"※ 이 알림은 봇에 의해 자동 발송됩니다."
        
        print("-" * 30)
        print(status)
        print("-" * 30)

        # [알림 조건 설정]
        # 현재 지수가 45(공포) 이하일 때만 채널에 전송
        # 전송 테스트를 해보고 싶다면 45를 100으로 잠시 바꿔보세요!
        if score <= 100: 
            msg = f"🚨 매수 타이밍 포착!\n{status}\n\n시장이 공포에 빠졌습니다. 분할 매수를 검토하세요!"
            await send_message(msg)
            print("📱 채널로 알림 전송 완료!")
        else:
            print("현재는 공포 구간이 아니므로 채널 메시지를 보내지 않습니다.")
            # (선택 사항) 매일 상황을 보고받고 싶다면 아래 줄의 주석(#)을 제거하세요.
            # await send_message(f"✅ 오늘 시장 상황 보고\n{status}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
