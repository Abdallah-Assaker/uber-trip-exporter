# Uber Trip Exporter

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python automation script that extracts Uber trip data and generates monthly transportation expense reports for company reimbursement with automatic email delivery.

## 🚀 Features

- **✨ External Configuration**: Uses JSON config files for easy customization without code editing
- **🔍 Automated Data Extraction**: Fetches trip data from Uber's GraphQL API
- **🏠 Smart Address Matching**: Uses configurable keywords to classify trips as "To Work" or "From Work"
- **📄 Receipt Management**: Downloads and merges all trip receipts into a single PDF
- **📊 Excel Integration**: Automatically fills out company expense claim forms
- **📁 Month-Specific Organization**: Creates organized folders for each month's data
- **📧 Email Automation**: Automatically compresses and emails monthly reports (NEW!)
- **🔐 Secure Token Management**: Uses external token file for easy monthly updates
- **🎛️ Command Line Parameters**: Accepts month parameter for flexible data extraction
- **📝 Enhanced Logging**: Colored console output with progress indicators and timestamps
- **🤝 Easy Sharing**: Share with colleagues without exposing your credentials

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
   pip install requests pandas openpyxl PyPDF2 redmail
   ```

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

### 3. Configure Address Keywords & Email Settings

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
  ],
  "email_config": {
    "enabled": false,
    "recipient_email": "your-work-email@company.com",
    "sender_email": "your-sender-email@gmail.com",
    "sender_password": "your-app-password",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "subject_template": "Uber Trip Report - {month_year}",
    "body_template": "Please find attached the Uber trip report for {month_year}.\n\nTotal amount: ${total_amount}\nNumber of trips: {trip_count}\n\nBest regards,\nUber Trip Exporter"
  }
}
```

#### Address Keywords Configuration

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

#### Email Configuration (Optional)

The script can automatically compress monthly reports into ZIP files and email them to you. This feature uses **Red Mail**, a modern Python email library.

**To enable email functionality:**

1. **Set `enabled` to `true`** in the email_config section
2. **Configure your email settings:**

**For Gmail (Recommended):**
```json
{
  "email_config": {
    "enabled": true,
    "recipient_email": "your-work@company.com",
    "sender_email": "your-gmail@gmail.com",
    "sender_password": "your-app-password",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
  }
}
```

**Gmail Setup Steps:**
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: [Google App Passwords Guide](https://support.google.com/accounts/answer/185833)
3. Use the App Password (not your regular password) in the config
4. Update sender_email with your Gmail address
5. Update recipient_email with where you want to receive reports

**For Other Email Providers:**
- **Outlook/Hotmail**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Update smtp_server and smtp_port accordingly

**Email Features:**
- 📦 **Automatic ZIP compression** of monthly folders
- 📧 **HTML and plain text** email formats
- 🎨 **Professional email templates** with trip summary
- 🔒 **Secure STARTTLS encryption**
- 🧹 **Automatic cleanup** of temporary files
- ⚠️ **Detailed error handling** with helpful messages

## 🚀 Usage

### Command Line Interface

The script now features **enhanced console logging** with colored output, progress indicators, and timestamps for better user experience.

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

### Console Output Features
- 🎨 **Colored logging**: Different colors for INFO, SUCCESS, WARNING, ERROR messages
- ⏱️ **Timestamps**: Each log entry shows the current time
- 📊 **Progress indicators**: Shows progress when processing multiple trips
- 🔄 **Real-time feedback**: Live updates on API calls, file operations, and Excel processing

### What the script does:
1. ✅ **Date Calculation**: Calculates date range for the specified month/year
2. 📁 **Folder Creation**: Creates a month-specific output folder (YYYY-MM format)
3. 🔍 **Data Fetching**: Fetches your Uber trips for that period with progress tracking
4. 📄 **Receipt Download**: Downloads receipt PDFs with individual status updates
5. 📊 **Excel Processing**: Creates monthly Excel claim form with progress indicators
6. 📑 **PDF Merging**: Merges all receipts into `all_receipts.pdf` with detailed logging
7. 💾 **Data Saving**: Saves trip data to `trips.json` with confirmation
8. 📦 **ZIP Compression**: Compresses monthly folder for easy sharing (if email enabled)
9. 📧 **Email Delivery**: Sends professional email with ZIP attachment (if configured)
10. 🧹 **Cleanup**: Cleans up temporary files with status reports
11. ✅ Preserves original Excel template

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

### Option 1: Local Files Only (Email Disabled)
1. **Update Token**: Get fresh cookie from browser → Update `token.txt`
2. **Run Script**: `python uber-script.py [month]` (e.g., `python uber-script.py 7` for July)
3. **Find Output**: Navigate to the `YYYY-MM/` folder created by the script
4. **Submit Forms**: Use the Excel file and merged PDF from the month folder for reimbursement

### Option 2: Automatic Email Delivery (Email Enabled)
1. **Update Token**: Get fresh cookie from browser → Update `token.txt`
2. **Run Script**: `python uber-script.py [month]` (e.g., `python uber-script.py 7` for July)
3. **Check Email**: Receive professional email with ZIP attachment containing all files
4. **Submit Forms**: Download ZIP attachment and submit for reimbursement

**Email Sample:**
```
Subject: Uber Trip Report - 2025-08

Please find attached the Uber trip report for 2025-08.

Total amount: $5,421.70
Number of trips: 24

The attached ZIP file contains:
- trips.json (trip data)  
- all_receipts.pdf (merged receipts)
- Excel claim form

Best regards,
Uber Trip Exporter
```

## 🛡️ Security Notes

- The `token.txt` file is automatically ignored by Git
- Never commit authentication tokens to version control
- Update your token monthly or when authentication fails
- Each user should have their own `token.txt` file

### Script Architecture

```
uber-script.py
├── 🔧 Configuration Management
│   ├── read_token_from_file()
│   └── read_config_from_file()
├── 📅 Date & Time Utilities  
│   ├── get_month_date_range()
│   └── parse_command_line_args()
├── 🌐 API Functions
│   └── get_uber_trips()
├── 📄 PDF & Receipt Management
│   ├── download_receipt_pdf()
│   ├── get_receipt_timestamp()
│   └── merge_receipts()
├── 📊 Excel Processing
│   ├── create_monthly_excel_copy()
│   └── process_excel_file()
└── 🎯 Main Execution
    └── main()
```

### Dependencies Simplified

**Current Dependencies:**
- ✅ `requests` - API calls
- ✅ `pandas` - Excel data manipulation
- ✅ `openpyxl` - Excel file handling
- ✅ `PyPDF2` - PDF merging
- ✅ `redmail` - Modern email sending (NEW!)

## 🐛 Troubleshooting

### Authentication Errors
- Get a fresh cookie from your browser
- Update `token.txt` with the new cookie
- Ensure no extra quotes or spaces in the token file

### Email Issues
- **Authentication Failed**: 
  - For Gmail: Ensure 2FA is enabled and you're using an App Password
  - Check that sender_email and sender_password are correct
  - Verify the App Password doesn't contain spaces
- **Connection Failed**:
  - Check internet connection
  - Verify SMTP server settings (smtp.gmail.com:587 for Gmail)
  - Try again in a few moments
- **Permission Denied**:
  - Check email provider's security settings
  - Ensure "Less secure app access" is not blocking the connection (use App Passwords instead)

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

### Enhanced Debugging with New Logging

The script now provides **detailed colored console output** to help with troubleshooting:

- 🔍 **API Progress**: See real-time API call status and response details
- 📊 **Trip Processing**: Progress indicators show which trips are being processed
- 📁 **File Operations**: Clear feedback on file creation, Excel writing, and PDF merging
- ⚠️ **Warning Messages**: Detailed warnings for missing data or classification issues
- ❌ **Error Details**: Specific error messages with context for easier debugging

**Tips for using the enhanced logging:**
- 🎨 **Colors**: Green = Success, Blue = Info, Yellow = Warning, Red = Error
- ⏱️ **Timestamps**: Each message shows exactly when it occurred
- 📈 **Progress**: Watch the `[X/Y]` indicators to see processing status

### Missing Output Files
- Check the month-specific folder (e.g., `2025-09/`)
- Files are organized in folders, not in the main directory
- Look for the pattern `YYYY-MM/` where YYYY-MM matches your target month
- Console output will show exactly which folder was created

### No Data Found
- Verify you had Uber trips in the specified month/year
- Check if the month logic is correct (December uses previous year)
- Ensure your date range covers the intended period
- Console shows exact date range being queried

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
