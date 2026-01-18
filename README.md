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


## External Access (Ngrok)

To use the OAuth flow with a public URL (recommended):

1. **Start the Tunnel**:
   ```bash
   poetry run python tunnel.py
   ```
   This will output a Public URL (e.g., `https://1234.ngrok-free.app`).

2. **Update Mercado Libre App**:
   - Go to your App settings in Mercado Libre.
   - Set the Redirect URI to the generated URL (plus any path if needed, usually just the base matching your local server, but for this script we assume you just redirect code manually).
   - *Note*: If you are just copying the code manually, `localhost` is fine. If you want to receive webhooks or use the proper flow later, use the ngrok URL.

## Output
The script generates `report.xlsx` containing the audit results.
