# Mercado Libre Shipping Cost Auditor

A Proof of Concept (PoC) SaaS application to audit Mercado Libre shipping costs by comparing billed dimensions/costs against a "source of truth" CSV.

## Features
- **OAuth 2.0 Auth**: Auto-refreshes tokens.
- **Robust API Client**: Handles retries and rate limits.
- **Audit Logic**: Matches sold SKUs to your dimensions table.

## Setup

1. **Install Dependencies**
   Ensure you have Poetry installed.
   ```bash
   poetry install
   ```

2. **Configuration**
   The project uses a `.env` file for credentials. This has been pre-configured with your provided `APP_ID`.
   
   Ensure your Mercado Libre App has the Redirect URI set to: `http://localhost:3000`

3. **Prepare Input Data**
   Create a file named `sku_truth.csv` in the root directory with the following columns:
   ```csv
   sku,weight_kg,width,height,depth
   TEST-SKU-001,0.5,10,10,10
   ```

## Running the Auditor

Run the main script using poetry:

```bash
poetry run python main.py
```

On the first run, it will ask you to authenticate by visiting a URL and pasting the code.

## Output
The script generates `report.xlsx` containing the audit results.
