import time
import datetime
import pyupbit
import numpy as np

access = "QeU7SY6rJMmbtxLsVYxaM9OEJxsnD9eG2PDofC5x"          # 본인 값으로 변경
secret = "CyhBeua9s99NA7DN5vuX7Hsx1F3d6IUCybFUEAvi"          # 본인 값으로 변경

def get_ror(k):
    df = pyupbit.get_ohlcv("KRW-BTC", count=21)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0005
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)
    ror = df['ror'].cumprod()[-2]
    return ror

def get_best_K():
    max_ror = 0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        # print("%.1f %f" % (k, ror))
        if ror > max_ror:
            max_ror = ror
            best_K = k
    #print("Best K: ", best_K)
    return best_K

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_previous_price(ticker):
    """변동성 돌파 전략으로 종가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    previous_price = df.iloc[0]['close']
    return previous_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)

# 현재 원화 잔고
krw_balance = get_balance("KRW")

# K-factor 초기화
k_factor = 0.5
best_K = 0.0

# Best K 구하기 및 초기화
have_best_K = 0
best_K = get_best_K()    
have_best_K = 1

#손절 factor 초기화
loss_factor = 0.1
loss_applied = 1-loss_factor

# 초기 종목 매수 진행 여부 
BTC_buy = 0

# 종목 매입 수량 및 평가금액
BTC_buy_volume = 0
BTC_buy_value = 0

# 누적 수수료 정보
trade_fee = 0.0

# 시간 정보
now = datetime.datetime.now()
start_time = get_start_time("KRW-BTC")
end_time = start_time + datetime.timedelta(days=1)
real_end_time = end_time - datetime.timedelta(seconds=10)
test_end_time = now + datetime.timedelta(seconds=10)

print()
print ("현재시각: ", now)
print("시작시간: ", start_time)
print("종료시간: ", real_end_time)

print()
print("현재 원화 잔고:", krw_balance)
print()

print("현재 Best K 값: ", best_K)
print()

print()
print("**** 자동매매 Start! ****")
print()

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        real_end_time = end_time - datetime.timedelta(seconds=10)

        if start_time < now < real_end_time:
            # 하루 지난 경우
            if have_best_K == 0:
                print()
                print()
                print("하루가 지났습니다")
                print ("현재시각: ", now)
                print("시작시간: ", start_time)
                print("종료시간: ", real_end_time)

                print()
                print("현재 원화 잔고:", get_balance("KRW"))
                print()

                best_K = get_best_K()
                have_best_K = 1
                print("현재 Best K 값: ", best_K)
                print()

            # BTC 매매
            print ("BTC 매매 시도합니다")
            print()

            BTC_target_price = get_target_price("KRW-BTC", best_K)
            BTC_current_price = get_current_price("KRW-BTC")
            print("BTC_current_price", BTC_current_price)
            print("BTC_target_price", BTC_target_price)
            if BTC_target_price < BTC_current_price:
                krw_balance = get_balance("KRW")
                if BTC_buy == 0 and krw_balance >= 10000:
                    print("BTC 매수 진행 - 목표가 도달")                   
                    print("현재 BTC 가격 * 매수금액 = 매수 BTC 수량")

                    krw_balance = krw_balance*0.9995
                    trade_fee = trade_fee + krw_balance*0.0005

                    print(get_current_price("KRW-BTC"), krw_balance, krw_balance/get_current_price("KRW-BTC"))
                    print("매수 완료 -K:", best_K)
                    print()

                    # upbit.buy_market_order("KRW-BTC", krw_balance)
                    # print(get_current_price("KRW-BTC"), krw_balance, get_balance("BTC"))

                    # BTC_buy_volume = get_balance("BTC")
                    # BTC_buy_value = get_balance("BTC")*get_current_price("KRW-BTC")
                    BTC_buy = 1
                    # print("BTC_buy:", BTC_buy)
                    # print("적용된 Best K: ", best_K)
                    # print("원화 잔고", get_balance("KRW"))
                    # print("BTC 매입 수량", BTC_buy_volume)
                    # print("BTC 평가 금액", BTC_buy_value)
                    # print("매매 수수료(매수):", trade_fee)
                    # print("BTC 매수 완료")
                    # print("-------------")
                    # print()
                else:
                    print("이미 매수한 상태, 더 이상 매수하지 않습니다")
                    print()    
            else:
                print("BTC 목표가 도달하지 않아 매수 하지 않습니다")
                print()
        else:
            print()
            print("종료 시점, BTC를 매수했을 경우, 매도 시도합니다")
            print()

            # Best K 리셋
            have_best_K = 0

            if BTC_buy == 0:
                print("BTC 목표가 도달하지 않아 매수 하지 않았습니다", BTC_buy)
                print("따라서 BTC 매수않아 매도하지 않습니다", BTC_buy)
                print()
            else:
                print("매수 진행했음/매도함")
                BTC_buy = 0

                # print("BTC 매수 진행 했음: 매수수량:", BTC_buy_volume)

                # BTC_current_value = get_balance("BTC")*get_current_price("KRW-BTC")

                # print("매수 BTC 평가금액:", BTC_buy_value)
                # print("현재 BTC 평가금액:", BTC_current_value)
                
                # if BTC_current_value > 10000:
                #     print("BTC 매도 진행합니다: 매도수량:", BTC_buy_volume)
                #     upbit.sell_market_order("KRW-BTC", get_balance("BTC"))
                #     trade_fee = trade_fee + krw_balance*0.0005

                #     print("BTC 매매정보 초기화합니다")
                #     BTC_buy = 0
                #     BTC_buy_volume = 0
                #     BTC_buy_value = 0
                #     print("BTC 매매정보: ", BTC_buy)
                #     print("BTC 매수수량: ", BTC_buy_volume)
                #     print("BTC 매도금액: ", BTC_current_value)
                #     print("매매 수수료(매도):", trade_fee)
                #     print("------------")
                #     print()
                # else:
                #     print("BTC 평가금액이 5천원 이하로 매도가 불가능합니다")
                #     print()

        print()
        print()

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)