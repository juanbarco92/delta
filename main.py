import sys
import pandas as pd
from src.meli_auditor.config import settings
from src.meli_auditor.auth import MeliAuth
from src.meli_auditor.client import MeliClient
from src.meli_auditor.auditor import MeliAuditor

def main():
    print("Initializing MeLi Shipping Auditor...")
    
    # 1. Authentication
    auth = MeliAuth()
    try:
        auth.get_token()
        print("Authenticated successfully (using stored tokens).")
    except Exception:
        print("Authentication required.")
        print(f"Please visit: {auth.get_auth_url()}")
        code = input("Paste the code from the redirect URL here: ").strip()
        auth.exchange_code(code)
        print("Authentication successful!")

    # 2. Setup Client
    client = MeliClient(auth)

    # 3. Load CSV Proof
    csv_path = "sku_truth.csv"
    try:
        # Check if file exists roughly by trying to instantiate auditor which reads it
        auditor = MeliAuditor(client, csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found. Please create it first.")
        sys.exit(1)

    # 4. Run Audit
    print("Starting audit for last 50 orders...")
    df = auditor.audit_orders(limit=50)

    if df.empty:
        print("No audit results found (no orders or no matching SKUs).")
        return

    # 5. Calculate/Estimate Loss
    df = auditor.calculate_money_lost(df)

    # 6. Save Report
    output_file = "report.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Audit complete. Report saved to {output_file}")

if __name__ == "__main__":
    main()
