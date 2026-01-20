import requests
import pandas as pd
import os

# 1. 설정
PLAYER_ID = 660271  # 오타니 쇼헤이
BASE_PRICE = 50000

def calculate_stock(war, wpa):
    return round((BASE_PRICE + (float(war) * 8000)) * (1 + (float(wpa) * 1.5)))

# 2. MLB API 호출 (2024년 전체 데이터)
url = f"https://statsapi.mlb.com/api/v1/people/{PLAYER_ID}/stats?stats=gameLog&group=hitting&season=2024"
data = requests.get(url).json()

raw_logs = []
if "stats" in data and len(data["stats"]) > 0:
    splits = data["stats"][0].get("splits", [])
    for log in splits:
        s = log.get("stat", {})
        raw_logs.append({
            "Date": log.get("date", ""),
            "Opponent": log.get("opponent", {}).get("name", "MLB"),
            "Hits": s.get("hits", 0),
            "HR": s.get("homeRuns", 0),
            "RBI": s.get("rbi", 0)
        })

# 3. 데이터 가공 (시계열 정렬)
df = pd.DataFrame(raw_logs)
if not df.empty:
    df = df.sort_values(by="Date").reset_index(drop=True)
    cum_war = 0.0
    for i, row in df.iterrows():
        daily_wpa = (row["HR"] * 0.15) + (row["RBI"] * 0.05) + (row["Hits"] * 0.02) - 0.05
        cum_war += (row["HR"] * 0.1) + (row["Hits"] * 0.01)
        df.at[i, "Price"] = calculate_stock(cum_war, daily_wpa)

    # 4. 결과 저장 (CSV 파일로 저장)
    df.to_csv("ohtani_stock_history.csv", index=False)
    print("Stock data updated successfully!")
