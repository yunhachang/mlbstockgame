import pandas as pd
import numpy as np
from collections import defaultdict
import random
import os

# ==========================================
# [설정] 슬롯 게임 & BM 파라미터
# ==========================================
INITIAL_CASH = 10000      
INITIAL_SLOTS = 3         
MAX_SLOTS = 10            
SLOT_UPGRADE_FEE = 3000   # 슬롯 1개당 가격 (호스트 수익)
TRANSACTION_FEE_RATE = 0.005 # 매도 수수료 0.5%
REINVEST_THRESHOLD = 1.5  # 총 자산이 초기 자본의 1.5배가 되면 슬롯 구매

class User:
    def __init__(self, user_id, strategy):
        self.user_id = user_id
        self.strategy = strategy
        self.cash = INITIAL_CASH
        self.slots = INITIAL_SLOTS
        self.portfolio = {} # {player_id: quantity}
        self.trade_count = 0

class HostBank:
    def __init__(self):
        self.fee_revenue = 0.0
        self.slot_revenue = 0.0
    
    def add_fee(self, amount): self.fee_revenue += amount
    def add_slot_sale(self, amount): self.slot_revenue += amount
    def total(self): return self.fee_revenue + self.slot_revenue

def run_bm_simulation():
    # 데이터 로드
    if not os.path.exists('data/price_history.csv'):
        print("Error: price_history.csv not found.")
        return
    
    prices_df = pd.read_csv('data/price_history.csv')
    innings = prices_df['inning_key'].unique()
    host = HostBank()
    
    # 100명의 유저 생성
    users = [User(i, random.choice(['Momentum', 'Random', 'Value'])) for i in range(100)]
    snapshots = []

    for inning in innings:
        curr_p = prices_df[prices_df['inning_key'] == inning]
        price_map = dict(zip(curr_p['player_id'], curr_p['price']))
        
        for user in users:
            # 1. 자산 가치 계산
            portfolio_val = sum(price_map.get(pid, 0) * q for pid, q in user.portfolio.items())
            total_val = user.cash + portfolio_val
            
            # 2. [BM] 슬롯 구매 결정
            if total_val > (INITIAL_CASH * REINVEST_THRESHOLD) and user.slots < MAX_SLOTS:
                if user.cash > SLOT_UPGRADE_FEE:
                    user.cash -= SLOT_UPGRADE_FEE
                    user.slots += 1
                    host.add_slot_sale(SLOT_UPGRADE_FEE)

            # 3. 매도 로직 (0.5% 수수료 적용)
            for pid in list(user.portfolio.keys()):
                if random.random() < 0.2: # 20% 확률로 매도
                    sell_price = price_map.get(pid, 0)
                    amount = sell_price * user.portfolio[pid]
                    fee = amount * TRANSACTION_FEE_RATE
                    user.cash += (amount - fee)
                    host.add_fee(fee)
                    del user.portfolio[pid]
                    user.trade_count += 1

            # 4. 매수 로직 (빈 슬롯 한도 내)
            while len(user.portfolio) < user.slots:
                p_id = random.choice(list(price_map.keys()))
                p_price = price_map[p_id]
                if user.cash > p_price:
                    user.cash -= p_price
                    user.portfolio[p_id] = 1
                    user.trade_count += 1
                else: break

            snapshots.append({
                'inning': inning, 'user_id': user.user_id, 'total_value': total_val,
                'slots': user.slots, 'cash': user.cash
            })

    # 결과 저장
    pd.DataFrame(snapshots).to_csv('data/bm_user_snapshots.csv', index=False)
    
    # 리포트 생성
    print(f"\n🏆 [BM REPORT] Total Revenue: {host.total():,.0f} P")
    print(f"💰 Fee Revenue: {host.fee_revenue:,.0f} P | Slot Sales: {host.slot_revenue:,.0f} P")
    print(f"📈 Total Trades: {sum(u.trade_count for u in users)} times")

if __name__ == "__main__":
    run_bm_simulation()
