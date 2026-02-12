import pandas as pd
import numpy as np
import os
import random
from collections import defaultdict

# [핵심 설정] 9이닝 단판 승부 고변동성 모드
WPA_WEIGHT = 2.8           # 9이닝 안에 약 170% 수익률을 뽑아내기 위한 가중치
TRANSACTION_FEE = 0.005    # 0.5% 수수료
SLOT_PRICE = 3000          # 슬롯 확장 비용
INITIAL_CASH = 10000

def run_game1_simulation():
    # 1. 데이터 로드
    input_path = 'data/ws_2025_with_wpa.csv'
    if not os.path.exists(input_path):
        print(f"에러: {input_path} 파일이 없습니다.")
        return

    full_df = pd.read_csv(input_path)
    
    # 2. 1차전(Game 1) 데이터만 필터링
    game_ids = full_df['game_id'].unique()
    game1_df = full_df[full_df['game_id'] == game_ids[0]].copy()
    
    # 3. 가격 히스토리 생성
    price_history = []
    player_stats = defaultdict(float) 
    
    innings = sorted(game1_df['inning'].unique())
    half_innings = ['top', 'bottom']
    
    print("📊 1차전(9이닝) 가격 시뮬레이션 시작...")
    
    for inn in innings:
        for half in half_innings:
            step_data = game1_df[(game1_df['inning'] == inn) & (game1_df['half'] == half)]
            if step_data.empty: continue
            
            # WPA 누적
            for _, row in step_data.iterrows():
                player_stats[row['player_id']] += row['wpa']
            
            # 이닝 종료 후 가격 기록
            for p_id in player_stats:
                p_info = game1_df[game1_df['player_id'] == p_id].iloc[0]
                p_name = p_info['player_name']
                # 기획자님표 고변동성 공식
                price = 1000 * (1 + WPA_WEIGHT * player_stats[p_id])
                
                price_history.append({
                    'inning': inn,
                    'half': half,
                    'inning_key': f"{inn}{half}",
                    'player_id': p_id,
                    'player_name': p_name,
                    'price': max(100, round(price, 2))
                })

    price_df = pd.DataFrame(price_history)
    os.makedirs('data', exist_ok=True)
    price_df.to_csv('data/game1_price_history.csv', index=False)
    
    # MVP 확인용 출력
    final_prices = price_df.groupby('player_name').last().sort_values('price', ascending=False)
    print("\n🔥 1차전 종료 시점 예상 주가 TOP 5:")
    print(final_prices[['price']].head(5))
    print(f"\n✅ 결과가 data/game1_price_history.csv에 저장되었습니다.")

if __name__ == "__main__":
    run_game1_simulation()
