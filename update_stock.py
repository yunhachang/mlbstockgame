import requests
import pandas as pd

# 1. 상장 선수 리스트 (오타니, 김하성, 스프링어 추가)
players = {
    "660271": "Ohtani",
    "673490": "Kim",
    "543807": "Springer" # 24시즌 부진했던 샘플 선수
}

all_data = []

for p_id, p_name in players.items():
    url = f"https://statsapi.mlb.com/api/v1/people/{p_id}/stats?stats=gameLog&group=hitting&season=2024"
    try:
        response = requests.get(url).json()
        if 'stats' in response and response['stats']:
            splits = response['stats'][0]['splits']
            
            # 날짜순 정렬 (과거 -> 최신)
            splits.sort(key=lambda x: x['date']) 
            
            t_h, t_hr, t_rbi, t_ab = 0, 0, 0, 0
            
            for game in splits:
                date = game['date']
                s = game['stat']
                
                # 누적 데이터 계산
                t_h += s.get('hits', 0)
                t_hr += s.get('homeRuns', 0)
                t_rbi += s.get('rbi', 0)
                t_ab += s.get('atBats', 0)
                
                # 실시간 누적 타율
                c_avg = t_h / t_ab if t_ab > 0 else 0
                
                # --- [기획 밸런싱: '냉혹한 시장' 로직] ---
                
                # 1. 덩치 (성적의 합)
                market_cap = (t_h * 100) + (t_hr * 800) + (t_rbi * 200)
                
                # 2. 현재 폼 (타율 기반 멀티플라이어)
                # 기준점 0.270으로 설정. 이보다 낮으면 가차없이 깎임
                form_multiplier = c_avg / 0.270 
                
                # 3. 최종 주가: (누적 가치 * 타율 비중) + 기본 상장가
                price = int((market_cap * form_multiplier) + 1000)
                
                all_data.append({
                    "Date": date,
                    "Player": p_name,
                    "Price": max(price, 500), # 하한선은 500으로 방어
                    "AVG": round(c_avg, 3)
                })
                
    except Exception as e:
        print(f"Error processing {p_name}: {e}")

if all_data:
    df = pd.DataFrame(all_data)
    df = df.sort_values(by=['Player', 'Date'])
    df.to_csv('mlb_stock_history.csv', index=False)
    print("3인 선수(상승/조정/하락) 데이터 업데이트 완료!")
