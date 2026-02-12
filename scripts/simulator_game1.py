import pandas as pd
import numpy as np
import os
from collections import defaultdict

# [핵심 설정]
WPA_WEIGHT = 2.8
BASE_PRICE = 1000

def run_game1_simulation():
    input_path = 'data/ws_2025_with_wpa.csv'
    if not os.path.exists(input_path):
        print(f"❌ 에러: {input_path} 파일이 없습니다.")
        return

    df = pd.read_csv(input_path)
    
    # [수정 포인트] 컬럼명 대소문자 표준화 (KeyError 방지)
    # 모든 컬럼명을 소문자로 변경하여 'player_id'를 확실히 찾게 합니다.
    df.columns = [c.lower() for c in df.columns]
    
    # 필요한 컬럼이 있는지 확인
    required_cols = ['game_id', 'inning', 'half', 'player_id', 'player_name', 'wpa']
    for col in required_cols:
        if col not in df.columns:
            print(f"❌ 에러: 데이터에 '{col}' 컬럼이 없습니다. 현재 컬럼: {list(df.columns)}")
            return

    # 1. 1차전(첫 번째 경기) 추출
    game_ids = df['game_id'].unique()
    game1_df = df[df['game_id'] == game_ids[0]].copy()
    
    price_history = []
    player_stats = defaultdict(float) 
    
    innings = sorted(game1_df['inning'].unique())
    half_innings = ['top', 'bottom']
    
    print(f"📊 1차전(Game ID: {game_ids[0]}) 가격 시뮬레이션 시작...")
    
    for inn in innings:
        for half in half_innings:
            step_data = game1_df[(game1_df['inning'] == inn) & (game1_df['half'] == half)]
            if step_data.empty: continue
            
            # WPA 누적
            for _, row in step_data.iterrows():
                player_stats[row['player_id']] += row['wpa']
            
            # 이닝 종료 후 가격 기록
            for p_id in player_stats:
                # 해당 선수의 이름을 찾기 위한 로직
                p_name_lookup = game1_df[game1_df['player_id'] == p_id]['player_name'].iloc[0]
                
                # 기획자님표 고변동성 공식
                price = BASE_PRICE * (1 + WPA_WEIGHT * player_stats[p_id])
                
                price_history.append({
                    'inning': inn,
                    'half': half,
                    'inning_key': f"{inn}{half}",
                    'player_id': p_id,
                    'player_name': p_name_lookup,
                    'price': max(100, round(price, 2))
                })

    result_df = pd.DataFrame(price_history)
    os.makedirs('data', exist_ok=True)
    result_df.to_csv('data/game1_price_history.csv', index=False)
    
    # 결과 요약 출력
    final_prices = result_df.groupby('player_name').last().sort_values('price', ascending=False)
    print("\n🔥 1차전 종료 시점 주가 TOP 5:")
    print(final_prices[['price']].head(5))
    print(f"\n✅ 완료! data/game1_price_history.csv 확인 요망.")

if __name__ == "__main__":
    run_game1_simulation()
