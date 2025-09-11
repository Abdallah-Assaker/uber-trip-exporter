# Uber Trip Exporter

This script automates the monthly process of extracting Uber trip data and filling out the company transportation allowance form.

## Setup Instructions

### 1. Install Required Dependencies
Make sure you have Python installed, then install the required packages:
```bash
pip install requests pandas openpyxl PyPDF2 pdfkit
```

### 2. Install wkhtmltopdf
Download and install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html
Install it to the default location: `C:\Program Files\wkhtmltopdf\`

### 3. Get Your Authentication Token

1. Open your browser and go to https://riders.uber.com
2. Log in to your Uber account
3. Open Developer Tools (F12)
4. Go to the "Network" tab
5. Refresh the page or navigate to your trips
6. Look for requests to `graphql` or `riders.uber.com`
7. Click on one of these requests
8. In the "Headers" section, find the "Cookie" header
9. Copy the entire cookie value (it will be a long string)

### 4. Update the Token File

1. Open the `token.txt` file in the same directory as the script
2. Replace the entire content with your cookie string
3. Save the file

**Important Notes:**
- Do NOT put quotes around the cookie string in the token.txt file
- The cookie string should be on a single line
- Update this token whenever you get authentication errors

### 5. Configure Your Addresses

Edit the script and update these variables with your actual addresses:
- `home_address`: Your home address
- `work_address`: Your work address

### 6. Run the Script

Simply run:
```bash
python uber-script.py
```

## What the Script Does

1. Fetches your Uber trip data from the past month
2. Downloads receipt PDFs for each trip
3. Merges all receipts into a single PDF file
4. Fills out the Excel claim form with trip details
5. Saves all data to `trips.json` for backup

## Files Generated

- `trips.json`: Raw trip data in JSON format
- `all_receipts.pdf`: Merged PDF of all trip receipts
- `receipts/`: Folder containing individual receipt PDFs
- Updated Excel claim form with your trip data

## Troubleshooting

### Authentication Errors
If you get authentication errors:
1. Get a fresh cookie from your browser (steps 3-4 above)
2. Update the `token.txt` file
3. Run the script again

### Missing Receipts
If some receipts fail to download:
- Check your internet connection
- Verify the trip exists in your Uber account

### Excel Errors
Make sure the Excel template file is in the same directory and hasn't been modified in structure.

## Monthly Usage

1. Update the `token.txt` file with a fresh cookie
2. Optionally update the date range in the script variables
3. Run the script
4. Submit the generated claim form and receipt PDF to your company