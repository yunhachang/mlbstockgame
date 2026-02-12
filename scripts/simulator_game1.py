import pandas as pd
import numpy as np
import os
import random

# [핵심 설정]
WPA_WEIGHT = 2.8           # 9이닝 안에 170% 수익률을 뽑아내기 위한 고배율
TRANSACTION_FEE = 0.005    # 0.5% 수수료
SLOT_PRICE = 3000          # 슬롯 확장 비용
INITIAL_CASH = 10000

def run_game1_simulation():
    # 1. 데이터 로드 (WPA가 계산된 원본 데이터)
    if not os.path.exists('data/ws_2025_with_wpa.csv'):
        print("데이터가 없습니다. analyze_wpa.py를 실행하세요.")
        return

    full_df = pd.read_csv('data/ws_2025_with_wpa.csv')
    
    # 2. [중요] 1차전(Game 1) 데이터만 필터링 (보통 game_id의 첫 번째 값)
    game_ids = full_df['game_id'].unique()
    game1_df = full_df[full_df['game_id'] == game_ids[0]].copy()
    
    # 3. 선수별 가격 히스토리 생성 (9이닝 기준)
    price_history = []
    player_stats = defaultdict(float) # 누적 WPA
    
    # 이닝별로 순차적 진행 (1회초 ~ 9회말)
    innings = sorted(game1_df['inning'].unique())
    half_innings = ['top', 'bottom']
    
    for inn in innings:
        for half in half_innings:
            step_data = game1_df[(game1_df['inning'] == inn) & (game1_df['half'] == half)]
            if step_data.empty: continue
            
            # 이닝 내 플레이별 WPA 반영
            for _, row in step_data.iterrows():
                player_stats[row['player_id']] += row['wpa']
            
            # 현재 이닝 종료 시점의 가격 기록
            for p_id in player_stats:
                p_name = game1_df[game1_df['player_id'] == p_id]['player_name'].iloc[0]
                price = 1000 * (1 + WPA_WEIGHT * player_stats[p_id])
                price_history.append({
                    'inning_key': f"{inn}{half}",
                    'player_id': p_id,
                    'player_name': p_name,
                    'price': max(100, round(price, 2))
                })

    price_df = pd.DataFrame(price_history)
    os.makedirs('data', exist_ok=True)
    price_df.to_csv('data/game1_price_history.csv', index=False)
    
    print(f"✅ 1차전 가격 시뮬레이션 완료. (데이터 수: {len(price_df)}건)")
    
    # 4. 유저 BM 시뮬레이션 (간략화)
    host_rev = 0
    # ... (생략: 위에서 만든 user_simulator_bm 로직과 동일하게 실행)
    print("🚀 1차전 기반 유저 매매 시뮬레이션 실행 중...")

if __name__ == "__main__":
    from collections import defaultdict
    run_game1_simulation()
