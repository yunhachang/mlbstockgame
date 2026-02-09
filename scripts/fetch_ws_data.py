import statsapi
import pandas as pd
import os

def update_ws_2025():
    # 기획자님의 팩트 시트: 10/24 ~ 11/03 (UTC 기준)
    target_start = '2025-10-24'
    target_end = '2025-11-03'
    
    print(f"Searching for 2025 World Series games between {target_start} and {target_end}...")
    
    # 1. 스케줄 조회
    sched = statsapi.schedule(start_date=target_start, end_date=target_end, sportId=1)
    ws_games = [g for g in sched if g.get('game_type') == 'W']
    
    if not ws_games:
        print("No World Series games found for the given range.")
        return

    all_plays = []
    for game in ws_games:
        game_id = game['game_id']
        print(f"Fetching play-by-play for Game {game_id}: {game['summary']}")
        
        pbp = statsapi.get('game_playByPlay', {'gamePk': game_id})
        for play in pbp.get('allPlays', []):
            about = play.get('about', {})
            result = play.get('result', {})
            matchup = play.get('matchup', {})
            
            all_plays.append({
                "game_id": game_id,
                "game_date": game['game_date'],
                "inning": about.get('inning'),
                "half": about.get('halfInning'),
                "event": result.get('event'),
                "batter": matchup.get('batter', {}).get('fullName'),
                "score_home": result.get('homeScore'),
                "score_away": result.get('awayScore'),
                "outs": play.get('count', {}).get('outs'),
                "description": result.get('description')
            })

    # 2. 데이터 저장
    df = pd.DataFrame(all_plays)
    os.makedirs('data', exist_ok=True)
    df.to_csv("data/ws_2025_real_results.csv", index=False)
    print(f"Successfully saved {len(df)} plays to data/ws_2025_real_results.csv")

if __name__ == "__main__":
    update_ws_2025()
