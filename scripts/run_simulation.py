"""
Master Simulation Runner
전체 시뮬레이션을 순서대로 실행
"""

import sys

def run_all_simulations():
    """
    전체 시뮬레이션 파이프라인 실행
    
    1. 가격 시뮬레이션 (이닝별 선수 가격 변동)
    2. 유저 시뮬레이션 (100명의 가상 유저 거래)
    """
    
    print("="*60)
    print("MLB STOCK GAME - FULL SIMULATION PIPELINE")
    print("="*60)
    print("\nPipeline:")
    print("  Step 1: Player Price Simulation")
    print("  Step 2: User Portfolio Simulation")
    print("\nStarting...\n")
    
    try:
        # Step 1: 가격 시뮬레이션
        print("\n" + "🔥"*30)
        print("STEP 1: PLAYER PRICE SIMULATION")
        print("🔥"*30)
        
        from price_simulator import run_price_simulation
        price_history, final_prices = run_price_simulation()
        
        # Step 2: 유저 시뮬레이션
        print("\n" + "👥"*30)
        print("STEP 2: USER PORTFOLIO SIMULATION")
        print("👥"*30)
        
        from user_simulator import run_user_simulation
        snapshots, user_results = run_user_simulation()
        
        # 최종 요약
        print("\n" + "="*60)
        print("🎉 ALL SIMULATIONS COMPLETE!")
        print("="*60)
        
        print("\nGenerated Files:")
        print("  📊 Price Data:")
        print("     - data/price_history.csv")
        print("     - data/final_prices.csv")
        print("\n  👥 User Data:")
        print("     - data/user_portfolio_snapshots.csv")
        print("     - data/user_final_results.csv")
        
        print("\n" + "="*60)
        print("QUICK STATS")
        print("="*60)
        
        print(f"\n💰 Price Simulation:")
        print(f"   Total Players: {len(final_prices)}")
        print(f"   Best ROI: {final_prices['roi_pct'].max():.1f}%")
        print(f"   Worst ROI: {final_prices['roi_pct'].min():.1f}%")
        
        print(f"\n👥 User Simulation:")
        print(f"   Total Users: {len(user_results)}")
        print(f"   Avg ROI: {user_results['roi_pct'].mean():.1f}%")
        print(f"   Winners: {len(user_results[user_results['roi_pct'] > 0])}")
        print(f"   Losers: {len(user_results[user_results['roi_pct'] < 0])}")
        
        # 전략별 승률
        print(f"\n📈 Strategy Win Rates:")
        for strategy in user_results['strategy'].unique():
            strategy_data = user_results[user_results['strategy'] == strategy]
            winners = len(strategy_data[strategy_data['roi_pct'] > 0])
            total = len(strategy_data)
            win_rate = (winners / total) * 100
            avg_roi = strategy_data['roi_pct'].mean()
            print(f"   {strategy:25s}: {win_rate:5.1f}% win rate | Avg ROI: {avg_roi:+6.1f}%")
        
        print("\n✅ Success! Check the data/ folder for detailed results.")
        
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_simulations()
