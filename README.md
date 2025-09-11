# Uber Trip Exporter

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python automation script that extracts Uber trip data and generates monthly transportation expense reports for company reimbursement.

## 🚀 Features

- **Automated Data Extraction**: Fetches trip data from Uber's GraphQL API
- **Receipt Management**: Downloads and merges all trip receipts into a single PDF
- **Excel Integration**: Automatically fills out company expense claim forms
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

### 3. Update Addresses

Edit `uber-script.py` and update these variables:
```python
home_address = "Your home address"
work_address = "Your work address"
```

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
2. ✅ Fetches your Uber trips for that period
3. ✅ Downloads receipt PDFs for each trip
4. ✅ Creates a monthly copy of your Excel template (preserves original)
5. ✅ Fills out the monthly Excel claim form automatically
6. ✅ Merges all receipts into a month-specific PDF
7. ✅ Saves trip data to month-specific JSON for backup
5. ✅ Merges all receipts into `all_receipts.pdf`
6. ✅ Saves trip data to `trips.json` for backup

## 📁 Output Files

- `YYYY-MM_Private_Taxi_Claim_Form.xlsx` - Monthly claim form with your trip data
- `YYYY-MM_trips.json` - Raw trip data in JSON format with date range info
- `YYYY-MM_all_receipts.pdf` - Merged PDF of all trip receipts
- `receipts/` - Individual receipt PDFs
- **Original Excel template remains untouched**

## 🔄 Monthly Workflow

1. **Update Token**: Get fresh cookie from browser → Update `token.txt`
2. **Run Script**: `python uber-script.py [month]` (e.g., `python uber-script.py 7` for July)
3. **Submit Forms**: Use generated Excel file and merged PDF for reimbursement

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

### No Data Found
- Verify you had Uber trips in the specified month/year
- Check if the month logic is correct (December uses previous year)
- Ensure your date range covers the intended period

### Missing Receipts
- Check internet connection
- Verify trips exist in your Uber account
- Some older trips may not have downloadable receipts

### Excel Errors
- Ensure the Excel template is in the same directory
- Don't modify the structure of the Excel template

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
