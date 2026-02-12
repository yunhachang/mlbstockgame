import pandas as pd
import numpy as np
import os
import sys
from collections import defaultdict

# [핵심 설정]
WPA_WEIGHT = 2.8
BASE_PRICE = 1000

def run_game1_simulation():
    input_path = 'data/ws_2025_with_wpa.csv'
    
    if not os.path.exists(input_path):
        print(f"❌ 에러: {input_path} 파일이 없습니다.")
        sys.exit(1)

    df = pd.read_csv(input_path)
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    
    print(f"📊 로드된 컬럼: {list(df.columns)}")

    # 1. 1차전 추출
    game_ids = df['game_id'].unique()
    game1_df = df[df['game_id'] == game_ids[0]].copy()
    
    price_history = []
    # 선수별 누적 WPA (ID를 키로 사용)
    player_wpa = defaultdict(float)
    player_names = {} # ID: Name 매핑

    # 2. 이닝별/이벤트별 데이터 순회
    # 타자와 투수 모두의 WPA를 추적해야 함
    for _, row in game1_df.iterrows():
        inn_key = f"{row['inning']}{row['half']}"
        wpa_val = row['wpa']
        
        # 타자 데이터 업데이트
        b_id, b_name = row['batter_id'], row['batter_name']
        player_wpa[b_id] += wpa_val
        player_names[b_id] = b_name
        
        # 투수 데이터 업데이트 (투수는 타자 WPA의 반대)
        p_id, p_name = row['pitcher_id'], row['pitcher_name']
        player_wpa[p_id] -= wpa_val
        player_names[p_id] = p_name
        
        # 이닝/이벤트별 가격 기록 (모든 선수의 현재가)
        # 데이터가 너무 많아질 수 있으므로 이닝 종료 시점 위주로 기록
        
    # 3. 최종 가격 리스트 생성 (기획자님 요청대로 고변동성 적용)
    # 실제 앱에서는 매 타석 변하겠지만, 시뮬레이션은 이닝 단위로 정리
    innings = sorted(game1_df['inning'].unique())
    for inn in innings:
        for half in ['top', 'bottom']:
            # 해당 이닝까지의 누적 WPA로 가격 산출
            for p_id, cum_wpa in player_wpa.items():
                price = BASE_PRICE * (1 + WPA_WEIGHT * cum_wpa)
                price_history.append({
                    'inning_key': f"{inn}{half}",
                    'player_name': player_names[p_id],
                    'price': max(100, round(price, 2))
                })

    # 4. 결과 저장
    result_df = pd.DataFrame(price_history)
    os.makedirs('data', exist_ok=True)
    out_path = 'data/game1_price_history.csv'
    result_df.to_csv(out_path, index=False)
    
    print(f"✅ 파일 생성 완료: {out_path}")
    
    # 1차전 TOP 5 출력
    final = result_df[result_df['inning_key'] == f"{innings[-1]}bottom"]
    top5 = final.sort_values('price', ascending=False).head(5)
    print("\n🔥 1차전(9이닝) 최종 주가 TOP 5:")
    print(top5[['player_name', 'price']])

if __name__ == "__main__":
    run_game1_simulation()
