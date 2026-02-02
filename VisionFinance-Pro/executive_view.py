
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from quant_core.analysis.portfolio_runner import PortfolioRunner

def run_executive_view():
    """
    Main entry point for the Hybrid UI.
    """
    print("... Market Analysis in Progress ...")
    
    runner = PortfolioRunner(initial_capital=10000)
    stats, allocations = runner.run_full_analysis()
    
    # --- 1. FIND THE 'STAR' PICK ---
    # We look for the Strongest BUY signal
    best_pick = None
    best_score = -1
    
    for alloc in allocations:
        if alloc['Action'] == 'BUY':
            # In a real app we'd have a numerical score in alloc, 
            # here we assume if it's a BUY it's passed thresholds.
            # Let's say we prioritize GLD or SPY if multiple buys exist, or just take the first one.
            best_pick = alloc
            break
            
    # --- 2. CLEAR SCREEN (Simulated with newlines) ---
    print("\n" * 2)
    
    # --- 3. PRINT EXECUTIVE CARD ---
    print("************************************************************")
    print("*                                                          *")
    print("*               YONETICI OZETI (EXECUTIVE CARD)            *")
    print("*                                                          *")
    print("************************************************************")
    
    if best_pick:
        print(f"\n   >>> TAVSIYE: AL ({best_pick['Ticker']}) <<<")
        print(f"   FIYAT: ${best_pick['Price']}")
        print(f"   NEDEN: {best_pick['Advice']}") 
        print(f"   DETAY: {best_pick['Story'][0] if best_pick['Story'] else 'Veri Yok'}")
    else:
        print("\n   >>> TAVSIYE: NAKITTE BEKLE (HOLD) <<<")
        print("   NEDEN: Piyasa sartlari riskli veya firsat yok.")
        
    print("\n************************************************************\n")
    
    print("... Detayli Tablolar Asagidadir ...\n")
    
    # --- 4. PRINT DETAILED TABLES ---
    runner.print_report(stats, allocations)

if __name__ == "__main__":
    run_executive_view()
