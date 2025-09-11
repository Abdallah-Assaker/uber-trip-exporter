"""
Uber Trip Exporter Script

This script extracts Uber trip data and fills out the monthly transportation claim form.

IMPORTANT: Before running this script:
1. Update the 'token.txt' file with your current Uber authentication cookie
2. Get the cookie from your browser's Developer Tools (F12) -> Network tab -> Cookie header
3. Do NOT put quotes around the cookie in the token.txt file

Usage:
    python uber-script.py [month]
    
    month: Optional integer (1-12) for the month to fetch data for.
           If not provided, uses the previous month.
           For December (12), uses the previous year.

The script will:
- Fetch trip data from Uber's GraphQL API for the specified month
- Download receipt PDFs
- Fill out the Excel claim form
- Merge all receipts into one PDF

For detailed instructions, see README.md
"""

import requests
import json
import re
import os
import shutil
import sys
import pdfkit
from datetime import datetime, timedelta
from calendar import monthrange
from PyPDF2 import PdfMerger
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import NamedStyle

path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def get_month_date_range(month=None):
    """
    Calculate start and end timestamps for a given month.
    
    Args:
        month (int): Month number (1-12). If None, uses previous month.
                    For December (12), uses previous year.
    
    Returns:
        tuple: (start_timestamp_ms, end_timestamp_ms, month_year_string)
    """
    current_date = datetime.now()
    
    if month is None:
        # Default to previous month
        if current_date.month == 1:
            target_month = 12
            target_year = current_date.year - 1
        else:
            target_month = current_date.month - 1
            target_year = current_date.year
    else:
        # Use provided month
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")
        
        target_month = month
        if month == 12:
            target_year = current_date.year - 1
        else:
            target_year = current_date.year
    
    # Calculate start of month (00:00:00)
    start_date = datetime(target_year, target_month, 1)
    
    # Calculate end of month (23:59:59.999)
    _, last_day = monthrange(target_year, target_month)
    end_date = datetime(target_year, target_month, last_day, 23, 59, 59, 999000)
    
    # Convert to milliseconds (Uber API expects milliseconds)
    start_timestamp_ms = int(start_date.timestamp() * 1000)
    end_timestamp_ms = int(end_date.timestamp() * 1000)
    
    # Create month-year string for file naming
    month_year_string = start_date.strftime("%Y-%m")
    
    print(f"📅 Fetching data for: {start_date.strftime('%B %Y')}")
    print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    return start_timestamp_ms, end_timestamp_ms, month_year_string

def parse_command_line_args():
    """Parse command line arguments for month parameter."""
    if len(sys.argv) > 1:
        try:
            month = int(sys.argv[1])
            if not 1 <= month <= 12:
                print("❌ Error: Month must be between 1 and 12")
                sys.exit(1)
            return month
        except ValueError:
            print("❌ Error: Month must be a valid integer between 1 and 12")
            print("Usage: python uber-script.py [month]")
            print("Example: python uber-script.py 7  (for July)")
            sys.exit(1)
    return None

# Parse command line arguments
target_month = parse_command_line_args()

# Get date range for the target month
start_time_ms, end_time_ms, month_year = get_month_date_range(target_month)

def read_token_from_file(file_path="token.txt"):
    """
    Read the authentication token/cookie from a text file.
    The file should contain the cookie string without quotes.
    """
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        token_file_path = os.path.join(script_dir, file_path)
        
        with open(token_file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
            if not token:
                raise ValueError("Token file is empty")
            return token
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found in the script directory.")
        print(f"Please create a '{file_path}' file with your authentication cookie.")
        print("You can copy the cookie from your browser's developer tools.")
        exit(1)
    except Exception as e:
        print(f"❌ Error reading token file: {e}")
        exit(1)

# Read the cookie from external file
cookie = read_token_from_file()

url = "https://riders.uber.com/graphql"

headers = {
    "cookie": cookie,
    "content-type": "application/json",
    "Cache-Control": "no-cache",
    "User-Agent": "PostmanRuntime/7.45.0",
    "origin": "https://riders.uber.com",
    "x-csrf-token": "x",
}

# 1. Query to list trips
activities_query = """
query Activities(
  $cityID: Int
  $endTimeMs: Float
  $includePast: Boolean = true
  $includeUpcoming: Boolean = true
  $limit: Int = 60
  $nextPageToken: String
  $orderTypes: [RVWebCommonActivityOrderType!] = [RIDES, TRAVEL]
  $profileType: RVWebCommonActivityProfileType = PERSONAL
  $startTimeMs: Float
) {
  activities(cityID: $cityID) {
    past(
      endTimeMs: $endTimeMs
      limit: $limit
      nextPageToken: $nextPageToken
      orderTypes: $orderTypes
      profileType: $profileType
      startTimeMs: $startTimeMs
    ) @include(if: $includePast) {
      activities {
        uuid
        cardURL
        description
        subtitle   # 👈 added here
        __typename
      }
      nextPageToken
      __typename
    }
    upcoming @include(if: $includeUpcoming) {
      activities {
        uuid
        cardURL
        description
        subtitle
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

# 2. Query to get details of a single trip (pickup & dropoff)
trip_details_query = """
query GetTrip($tripUUID: String!) {
  getTrip(tripUUID: $tripUUID) {
    trip {
      uuid
      waypoints
    }
  }
}
"""

# 3. Receipt query
receipt_query = """
query GetReceipt($tripUUID: String!, $timestamp: String) {
  getReceipt(tripUUID: $tripUUID, timestamp: $timestamp) {
    receiptsForJob {
      timestamp
      type
    }
    receiptData
  }
}
"""

def download_receipt_pdf(uuid, timestamp, folder="receipts"):
    os.makedirs(folder, exist_ok=True)
    pdf_path = os.path.join(folder, f"{uuid}.pdf")

    url = f"https://riders.uber.com/trips/{uuid}/receipt?contentType=PDF&timestamp={timestamp}"

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/pdf"):
        with open(pdf_path, "wb") as f:
            f.write(resp.content)
        print(f"✅ Saved {pdf_path}")
        return pdf_path
    else:
        print(f"❌ Failed: {resp.status_code}, {resp.text[:200]}")
        return None

def cleanup_temp_receipts_folder(folder="receipts"):
    """Remove the temporary receipts folder after processing."""
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"🗑️ Cleaned up temporary folder: {folder}")

def create_monthly_excel_copy(template_file, month_year=None, output_folder=None):
    """
    Create a copy of the Excel template with month-year prefix in the specified output folder.
    If month_year is None, it will use the current month-year.
    If output_folder is None, it will create the file in the current directory.
    """
    if month_year is None:
        month_year = datetime.now().strftime("%Y-%m")
    
    # Extract file name and extension
    file_name, file_ext = os.path.splitext(template_file)
    
    # Create new filename with month prefix
    new_filename = f"{month_year}_{file_name}{file_ext}"
    
    # If output folder is specified, create the path within that folder
    if output_folder:
        new_filepath = os.path.join(output_folder, new_filename)
    else:
        new_filepath = new_filename
    
    # Copy the template to new file
    shutil.copy2(template_file, new_filepath)
    print(f"✅ Created monthly copy: {new_filepath}")
    
    return new_filepath

def process_excel_file(excel_file, trips, template_excel_file, home_address, work_address):
    """Process the Excel file with trip data."""
    # Read the Claim Form sheet
    df_claim = pd.read_excel(excel_file, sheet_name="Claim Form", header=None)
    
    # Read the Legend sheet
    df_legend = pd.read_excel(excel_file, sheet_name="Legend")
    
    # Fill in the trip data starting from row 8 (index 7 in 0-based)
    start_row = 7
    
    for i, trip in enumerate(trips):
        # Determine the reason for the trip based on pickup location
        if trip["pickup_location"] == home_address:
            trip_reason = "العودة من العمل"  # Return from work
        elif trip["pickup_location"] == work_address:
            trip_reason = "الذهاب إلى العمل"  # Going to work
        else:
            trip_reason = ""  # Unknown reason
        
        # Convert the date string to a proper date format
        try:
            trip_dt = datetime.strptime(trip["time"].replace("•", "").strip(), "%b %d %I:%M %p")
            trip_dt = trip_dt.replace(year=datetime.now().year)  # اضف السنة
            trip_date = trip_dt.date()
        except:
            trip_date = trip["time"]  # Fallback to string if parsing fails
        
        # Fill in the row data
        df_claim.iloc[start_row + i, 1] = trip_date  # Date (Column B)
        df_claim.iloc[start_row + i, 2] = trip["pickup_location"]  # Pickup location (Column C)
        df_claim.iloc[start_row + i, 3] = trip["dropoff_location"]  # Dropoff location (Column D)
        df_claim.iloc[start_row + i, 4] = trip["price"]  # Price (Column E)
        df_claim.iloc[start_row + i, 5] = trip_reason  # Reason (Column F)
        df_claim.iloc[start_row + i, 6] = "محفظة التطبيق"  # Payment method (Column G)
        df_claim.iloc[start_row + i, 7] = ""  # Notes (Column H)
    
    # Open the workbook (use the monthly copy we created)
    wb = load_workbook(excel_file)
    ws = wb["Claim Form"]

    start_row = 8  # Row 8 in Excel (since Excel rows are 1-based)

    for i, trip in enumerate(trips, start=0):
        # Try to parse the trip date
        try:
            trip_dt = datetime.strptime(
                trip["time"].replace("•", "").strip(), "%b %d %I:%M %p"
            )
            trip_dt = trip_dt.replace(year=datetime.now().year)  # add year if missing
            trip_date = trip_dt
        except:
            trip_date = trip["time"]  # fallback if parsing fails

        row = start_row + i
        ws.cell(row=row, column=2, value=trip_date)  # Column B = Date
        ws.cell(row=row, column=3, value=trip["pickup_location"])
        ws.cell(row=row, column=4, value=trip["dropoff_location"])
        ws.cell(row=row, column=5, value=trip["price"])
        ws.cell(row=row, column=6, value="To Work" if trip["pickup_location"] == home_address else
                                      "From Work" if trip["pickup_location"] == work_address else "")
        ws.cell(row=row, column=7, value="App Wallet")
        ws.cell(row=row, column=8, value="")

        # Format the date column as dd/mm/yyyy
        ws.cell(row=row, column=2).number_format = "dd/mm/yyyy"

    # Save changes to the monthly copy
    wb.save(excel_file)
    print(f"✅ Data written to monthly copy: {excel_file}")
    print(f"📄 Original template preserved: {template_excel_file}")
  
def get_receipt_timestamp(uuid):
    receipt_payload = {
        "operationName": "GetReceipt",
        "query": receipt_query,
        "variables": {"tripUUID": uuid, "timestamp": ""},
    }
    receipt_resp = requests.post(url, headers=headers, data=json.dumps(receipt_payload))
    if receipt_resp.status_code == 200:
        receipt_data = receipt_resp.json()

        # Defensive checks
        if not receipt_data or "data" not in receipt_data or not receipt_data["data"]:
            print(f"❌ No data returned for receipt {uuid}")
            return None

        receipt_info = receipt_data["data"].get("getReceipt")
        if receipt_info:
            jobs = receipt_info.get("receiptsForJob", [])
            if jobs:
                return jobs[0]["timestamp"]
    else:
        print(f"❌ Request failed for {uuid}: {receipt_resp.status_code} {receipt_resp.text[:200]}")
    return None

def merge_receipts(trips, folder="receipts", output_file="all_receipts.pdf"):
    merger = PdfMerger()

    # Sort trips by time desc
    sorted_trips = sorted(
        trips,
        key=lambda t: parse_trip_date(t.get("time", "")),
        reverse=True
    )

    for trip in sorted_trips:
        pdf_file = os.path.join(folder, f"{trip['uuid']}.pdf")
        if os.path.exists(pdf_file):
            merger.append(pdf_file)
            print(f"📄 Added {trip['time']} → {pdf_file}")
        else:
            print(f"⚠️ Missing PDF for {trip['uuid']} ({trip['time']})")

    if sorted_trips:
        with open(output_file, "wb") as f:
            merger.write(f)
        merger.close()
        print(f"✅ Merged {len(sorted_trips)} receipts into {output_file}")
    else:
        print("⚠️ No trips available to merge.")


def parse_trip_date(date_str: str):
    """Convert Uber's subtitle string into datetime (adjust format if needed)."""
    try:
        # Example: "Aug 31, 2025, 10:15 AM"
        return datetime.strptime(date_str, "%b %d, %Y, %I:%M %p")
    except Exception as e:
        print(f"⚠️ Failed to parse date '{date_str}': {e}")
        return datetime.min    

variables = {
    "includePast": True,
    "includeUpcoming": True,
    "limit": 60,
    "orderTypes": ["RIDES", "TRAVEL"],
    "profileType": "PERSONAL",
    "endTimeMs": end_time_ms,
    "startTimeMs": start_time_ms,
}

payload = {
    "operationName": "Activities",
    "query": activities_query,
    "variables": variables,
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    data = response.json()
    trips = []
    overall_amount = 0.0

    for trip in data["data"]["activities"]["past"]["activities"]:
        uuid = trip["uuid"]
        trip_url = trip["cardURL"]
        desc = trip.get("description", "")   
        subtitle = trip.get("subtitle", "")  

        # parse price
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", desc)
        price = float(match.group(1)) if match else 0.0
        overall_amount += price

        status = "Canceled" if "canceled" in desc.lower() else "Completed"
        if status == "Canceled" or "unfulfilled" in desc.lower():
            continue  # Skip canceled and unfulfilled trips

        pickup_address = ""
        dropoff_address = ""
        receipt_file = None

        # 2nd request: fetch trip details
        trip_payload = {
            "operationName": "GetTrip",
            "query": trip_details_query,
            "variables": {"tripUUID": uuid},
        }

        detail_resp = requests.post(url, headers=headers, data=json.dumps(trip_payload))
        
        if detail_resp.status_code != 200:
            print(f"[ERROR] Failed to fetch details for trip {uuid}. Status: {detail_resp.status_code}")
            print(f"Payload: {json.dumps(trip_payload, indent=2)}")
            print(f"Response: {detail_resp.text}")
        else:
            print(f"Fetched details for trip {uuid}, status: {detail_resp.status_code}")

        if detail_resp.status_code == 200:
            trip_data = detail_resp.json()
            waypoints = trip_data["data"]["getTrip"]["trip"]["waypoints"]
            if waypoints and len(waypoints) >= 2:
              pickup_address = waypoints[0]
              dropoff_address = waypoints[-1]
        else:
            print(f"[ERROR] {uuid}: {detail_resp.status_code} {detail_resp.text}")

            for wp in waypoints:
              addr = wp.get("address", {})
              full_address = f"{addr.get('title','')} {addr.get('subtitle','')}".strip()
              if wp["type"] == "PICKUP":
                  pickup_address = full_address
              elif wp["type"] == "DROPOFF":
                  dropoff_address = full_address

        # Get receipt timestamp
        timestamp = get_receipt_timestamp(uuid)

        if timestamp:
            # Download receipt PDF
            download_receipt_pdf(uuid, timestamp)
        else:
            print(f"❌ No timestamp found for trip {uuid}")

        trips.append({
            "uuid": uuid,
            "url": trip_url,
            "status": status,
            "price": price,
            "time": subtitle,
            "pickup_location": pickup_address,
            "dropoff_location": dropoff_address,
        })

    # Create month-specific output folder
    output_folder = month_year
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Created output folder: {output_folder}")

    # Create month-specific output file paths
    monthly_receipts_file = os.path.join(output_folder, "all_receipts.pdf")
    monthly_trips_file = os.path.join(output_folder, "trips.json")

    # Save trips data with month prefix
    with open(monthly_trips_file, "w", encoding="utf-8") as f:
        json.dump({
            "overall_amount": round(overall_amount, 2),
            "trips": trips,
            "month_year": month_year,
            "date_range": {
                "start": start_time_ms,
                "end": end_time_ms
            }
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(trips)} trips to {monthly_trips_file} (total: {round(overall_amount, 2)})")
    
    # Merge receipts with month-specific filename
    merge_receipts(trips, output_file=monthly_receipts_file)
    
    # Clean up temporary receipts folder
    cleanup_temp_receipts_folder()

    # Now process the Excel file within the same output folder
    # Define the addresses for determining the trip reason
    home_address = "223 متفرع من شارع 90 – خلف فندق الدوسيت – التجمع الخامس – القاهرة الجديدة، N Teseen, New Cairo 1, Cairo Governorate 11835, Egypt"
    work_address = "1 Al Tabeer, El-Zaytoun Sharkeya, Zeitoun, Cairo Governorate 4520120, Egypt"

    # Load the Excel template (original file name)
    template_excel_file = "Private_Taxi_Claim_Form.xlsx"

    # Create a monthly copy of the Excel file using the calculated month_year
    excel_file = create_monthly_excel_copy(template_excel_file, month_year, output_folder)

    # Process Excel file
    try:
        process_excel_file(excel_file, trips, template_excel_file, home_address, work_address)
        
        print(f"\n🎉 Monthly report completed!")
        print(f"📁 All files saved in folder: {output_folder}")
        print(f"   - trips.json (trip data)")
        print(f"   - all_receipts.pdf (merged receipts)")
        print(f"   - {month_year}_Private_Taxi_Claim_Form.xlsx (claim form)")
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {e}")

else:
    print("Error:", response.status_code, response.text)
    sys.exit(1)