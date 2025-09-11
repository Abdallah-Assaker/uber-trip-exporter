# Uber Trip Exporter

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python automation script that extracts Uber trip data and generates monthly transportation expense reports for company reimbursement.

## 🚀 Features

- **Automated Data Extraction**: Fetches trip data from Uber's GraphQL API
- **Smart Address Matching**: Uses keywords to classify trips as "To Work" or "From Work"
- **Receipt Management**: Downloads and merges all trip receipts into a single PDF
- **Excel Integration**: Automatically fills out company expense claim forms
- **Month-Specific Organization**: Creates organized folders for each month's data
- **Secure Token Management**: Uses external token file for easy monthly updates
- **Easy Sharing**: Share with colleagues without exposing your credentials

## 📋 Prerequisites

- Python 3.7 or higher
- Active Uber account with trip history
- Company expense claim form (Excel template)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abdallah-Assaker/uber-trip-exporter.git
   cd uber-trip-exporter
   ```

2. **Install dependencies**
   ```bash
   pip install requests pandas openpyxl PyPDF2 pdfkit
   ```

3. **Install wkhtmltopdf**
   - Download from: https://wkhtmltopdf.org/downloads.html
   - Install to default location: `C:\Program Files\wkhtmltopdf\`

## 🔧 Setup

### 1. Get Your Authentication Token

1. Go to [Uber Riders](https://riders.uber.com) and log in
2. Open Developer Tools (F12)
3. Navigate to the **Network** tab
4. Refresh the page or navigate to your trips
5. Find a request to `graphql`
6. Copy the entire `Cookie` header value

### 2. Configure Token File

1. Create a `token.txt` file in the project directory
2. Paste your cookie string (no quotes needed)
3. Save the file

**Example `token.txt`:**
```
marketing_vistor_id=abc123; udi-id=def456; isWebLogin=true; sid=xyz789; ...
```

### 3. Configure Address Keywords

The script uses keyword-based matching to classify trips as "To Work" or "From Work" since Uber addresses may vary slightly due to location accuracy.

**On first run**, the script will automatically create a `config.json` file with default template. Alternatively, you can copy from the example:

```bash
copy config.json.example config.json
```

The config file format:

```json
{
  "home_address_keywords": [
    "YOUR_HOME_STREET_NAME",
    "YOUR_HOME_LANDMARK", 
    "YOUR_HOME_AREA"
  ],
  "work_address_keywords": [
    "YOUR_WORK_STREET_NAME",
    "YOUR_WORK_LANDMARK",
    "YOUR_WORK_AREA"
  ]
}
```

**Update this file** with actual keywords from your addresses:

```json
{
  "home_address_keywords": [
    "223 متفرع من شارع 90",
    "خلف فندق الدوسيت", 
    "N Teseen, New Cairo 1",
    "التسعين الشمالي"
  ],
  "work_address_keywords": [
    "1 Al Tabeer",
    "El-Zaytoun Sharkeya",
    "Zeitoun, Cairo",
    "الطابير"
  ]
}
```

**Tips for choosing keywords:**
- ✅ Use consistent parts of addresses (street names, landmarks)
- ✅ Include both Arabic and English variations
- ✅ Add area/district names that don't change
- ✅ Include nearby landmarks mentioned in addresses
- ❌ Avoid full addresses that may vary
- ❌ Don't use building numbers that might change (e.g., 223 vs 224)
- 🔍 Test by checking actual addresses in the generated `trips.json` file

## 🚀 Usage

### Basic Usage (Previous Month)
```bash
python uber-script.py
```

### Specific Month Usage
```bash
python uber-script.py [month]
```

**Examples:**
```bash
python uber-script.py 7     # Fetch July data
python uber-script.py 12    # Fetch December data (previous year)
python uber-script.py 1     # Fetch January data (current year)
```

**Month Logic:**
- **No parameter**: Fetches previous month's data
- **Month 1-11**: Uses current year
- **Month 12 (December)**: Uses previous year (for year-end reporting)

### What the script does:
1. ✅ Calculates date range for the specified month/year
2. ✅ Creates a month-specific output folder (YYYY-MM format)
3. ✅ Fetches your Uber trips for that period
4. ✅ Downloads receipt PDFs to temporary folder
5. ✅ Creates monthly Excel claim form in the output folder
6. ✅ Merges all receipts into `all_receipts.pdf` in the output folder
7. ✅ Saves trip data to `trips.json` in the output folder
8. ✅ Cleans up temporary receipt files
9. ✅ Preserves original Excel template

## 📁 Output Structure

After running the script, you'll have a folder structure like this:
```
project-folder/
├── uber-script.py
├── Private_Taxi_Claim_Form.xlsx (original template)
├── token.txt
└── 2025-09/                    # Month-specific folder
    ├── trips.json              # Trip data in JSON format
    ├── all_receipts.pdf         # Merged PDF receipts
    └── 2025-09_Private_Taxi_Claim_Form.xlsx  # Filled claim form
```

**Benefits of Folder Organization:**
- ✅ Separate outputs by month for easy archiving
- ✅ Original template stays clean and reusable
- ✅ No more cluttered main directory
- ✅ Easy to find specific month's data

## 🔄 Monthly Workflow

1. **Update Token**: Get fresh cookie from browser → Update `token.txt`
2. **Run Script**: `python uber-script.py [month]` (e.g., `python uber-script.py 7` for July)
3. **Find Output**: Navigate to the `YYYY-MM/` folder created by the script
4. **Submit Forms**: Use the Excel file and merged PDF from the month folder for reimbursement

## 🤝 Sharing with Colleagues

To share this script:

1. **Fork/Clone** this repository
2. **Remove your `token.txt`** (it's already in `.gitignore`)
3. **Share the folder** with colleagues
4. **Each person creates their own `token.txt`**
5. **Each person updates their home/work addresses**

## 🛡️ Security Notes

- The `token.txt` file is automatically ignored by Git
- Never commit authentication tokens to version control
- Update your token monthly or when authentication fails
- Each user should have their own `token.txt` file

## 🐛 Troubleshooting

### Authentication Errors
- Get a fresh cookie from your browser
- Update `token.txt` with the new cookie
- Ensure no extra quotes or spaces in the token file

### Invalid Month Parameter
- Month must be an integer between 1 and 12
- Use `python uber-script.py 7` not `python uber-script.py July`
- Check command syntax: `python uber-script.py [month]`

### Trip Classification Issues (To Work / From Work)
- Trips showing as blank reason or incorrect classification
- **Solution**: Update address keywords in the script
- Check `trips.json` for actual address strings used by Uber
- Add more keyword variations to `home_address_keywords` and `work_address_keywords`
- Use partial addresses that are consistent (street names, landmarks, areas)

**Example address keyword debugging:**
1. Run the script and check `YYYY-MM/trips.json`
2. Look at `pickup_location` values for your actual trips
3. Find consistent parts and add them to keyword lists
4. Re-run the script to test classification

### Missing Output Files
- Check the month-specific folder (e.g., `2025-09/`)
- Files are organized in folders, not in the main directory
- Look for the pattern `YYYY-MM/` where YYYY-MM matches your target month

### No Data Found
- Verify you had Uber trips in the specified month/year
- Check if the month logic is correct (December uses previous year)
- Ensure your date range covers the intended period

### Missing Receipts
- Check internet connection
- Verify trips exist in your Uber account
- Some older trips may not have downloadable receipts
- Temporary receipts folder is automatically cleaned up after processing

### Excel Errors
- Ensure the Excel template is in the same directory
- Don't modify the structure of the Excel template
- Original template should remain as `Private_Taxi_Claim_Form.xlsx`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤖 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add some improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## ⚠️ Disclaimer

This script is for personal use and automation of legitimate expense reporting. Users are responsible for complying with their company's expense policies and Uber's terms of service.

## 📞 Support

If you encounter issues or have questions:
1. Check the [Issues](https://github.com/Abdallah-Assaker/uber-trip-exporter/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

---

**Made with ❤️ for automating boring expense reports**
