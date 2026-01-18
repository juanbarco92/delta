import pandas as pd
from typing import List, Dict, Any
from .client import MeliClient

class MeliAuditor:
    def __init__(self, client: MeliClient, sku_truth_path: str):
        self.client = client
        self.sku_truth = pd.read_csv(sku_truth_path)
        # Ensure SKUs are strings for matching
        self.sku_truth['sku'] = self.sku_truth['sku'].astype(str)

    def audit_orders(self, limit: int = 50) -> pd.DataFrame:
        # 1. Get Seller ID
        me = self.client.get_me()
        seller_id = me["id"]
        print(f"Auditing orders for Seller ID: {seller_id}")

        # 2. Fetch Orders
        orders_data = self.client.get_orders(seller_id, limit=limit)
        orders = orders_data.get("results", [])
        
        audit_results = []

        for order in orders:
            try:
                # Skipping orders without shipping
                if "shipping" not in order or not order["shipping"].get("id"):
                    continue

                shipment_id = order["shipping"]["id"]
                shipment = self.client.get_shipment(shipment_id)
                
                # Extract relevant shipment data
                # Logic: We assume one main item or handling multiple items needs aggregation
                # For PoC, we look at order items to find SKU
                
                order_items = order.get("order_items", [])
                for item in order_items:
                    item_sku = item.get("item", {}).get("seller_sku")
                    if not item_sku:
                        continue
                        
                    # Find in Truth Table
                    truth_row = self.sku_truth[self.sku_truth['sku'] == str(item_sku)]
                    
                    if truth_row.empty:
                        # SKU not in truth table, skip
                        continue
                    
                    truth_data = truth_row.iloc[0]
                    
                    # Billed details (from shipment)
                    # Note: shipment object structure depends on API version. 
                    # Usually 'shipping_option' has cost. 'dimensions' might be strictly what was sent?
                    # We often look at 'shipping_items' dimensions if available or the package dimensions.
                    
                    # Approximating logic for PoC:
                    billed_cost = shipment.get("base_cost", 0)
                    # Real dimensions from Truth
                    
                    result = {
                        "order_id": order["id"],
                        "shipment_id": shipment_id,
                        "sku": item_sku,
                        "quantity": item["quantity"],
                        "billed_cost": billed_cost,
                        "truth_weight": truth_data.get("weight_kg"),
                        "truth_vol": f"{truth_data.get('width')}x{truth_data.get('height')}x{truth_data.get('depth')}",
                        # Money Lost calculation would ideally require re-quoting. 
                        # For now we assume a placeholder or difference in weight implies potential loss.
                        "status": shipment.get("status"),
                        "logic_note": "Compared against truth table"
                    }
                    audit_results.append(result)
                    
            except Exception as e:
                print(f"Error processing order {order.get('id')}: {e}")

        df = pd.DataFrame(audit_results)
        return df

    def calculate_money_lost(self, df: pd.DataFrame) -> pd.DataFrame:
        # Placeholder for complex cost calculation
        # In a real app, this would re-query the shipping calculator with 'truth' dimensions
        # and subtract that from 'billed_cost'.
        
        # For PoC, let's just flag rows where we successfully audited
        df["money_lost_estimate"] = "Not Calculated (Requires Rate Card)"
        return df
