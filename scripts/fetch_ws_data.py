import requests
import pandas as pd
import os

def fetch_ws_2025_data(game_pk):
    # 2025년 실제 경기 데이터를 가져오는 엔드포인트
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    try:
        response = requests.get(url).json()
        plays = response.get('liveData', {}).get('plays', {}).get('allPlays', [])
        
        results = []
        for play in plays:
            about = play.get('about', {})
            result = play.get('result', {})
            matchup = play.get('matchup', {})
            
            results.append({
                "game_pk": game_pk,
                "inning": about.get('inning'),
                "half": about.get('halfInning'),
                "event": result.get('event'),
                "batter": matchup.get('batter', {}).get('fullName'),
                "pitcher": matchup.get('pitcher', {}).get('fullName'),
                "description": result.get('description'),
                "score_home": result.get('homeScore'),
                "score_away": result.get('awayScore'),
                # 베팅 배당률 계산을 위한 핵심 상황 데이터
                "outs": play.get('count', {}).get('outs'),
                "is_scoring": result.get('isScoringPlay'),
            })
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

# 2025 월드시리즈 주요 경기 PK
ws_2025_pks = ["775330", "775332", "775336"] 

all_plays = []
for pk in ws_2025_pks:
    print(f"2025 WS Game {pk} 데이터 추출 중...")
    all_plays.extend(fetch_ws_2025_data(pk))

if all_plays:
    os.makedirs('data', exist_ok=True)
    pd.DataFrame(all_plays).to_csv('data/ws_2025_backtest.csv', index=False)
    print("✅ 2025 월드시리즈 백테스트 파일 생성 완료!")
