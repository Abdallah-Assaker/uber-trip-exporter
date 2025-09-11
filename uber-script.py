"""
Uber Trip Exporter Script

This script extracts Uber trip data and fills out the monthly transportation claim form.

IMPORTANT: Before running this script:
1. Update the 'token.txt' file with your current Uber authentication cookie
2. Get the cookie from your browser's Developer Tools (F12) -> Network tab -> Cookie header
3. Do NOT put quotes around the cookie in the token.txt file

The script will:
- Fetch trip data from Uber's GraphQL API
- Download receipt PDFs
- Fill out the Excel claim form
- Merge all receipts into one PDF

For detailed instructions, see README.md
"""

import requests
import json
import re
import os
import pdfkit
from datetime import datetime
from PyPDF2 import PdfMerger
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import NamedStyle

path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

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
  $endTimeMs: Float = 1756673999999
  $includePast: Boolean = true
  $includeUpcoming: Boolean = true
  $limit: Int = 60
  $nextPageToken: String
  $orderTypes: [RVWebCommonActivityOrderType!] = [RIDES, TRAVEL]
  $profileType: RVWebCommonActivityProfileType = PERSONAL
  $startTimeMs: Float = 1753995600000
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
    "endTimeMs": 1756673999999,
    "startTimeMs": 1753995600000,
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

        output = {
        "overall_amount": round(overall_amount, 2),
        "trips": trips
          }

        with open("trips.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved {len(trips)} trips to trips.json (total: {output['overall_amount']})")
else:
  print("Error:", response.status_code, response.text)

merge_receipts(trips)

# Define the addresses for determining the trip reason
home_address = "223 متفرع من شارع 90 – خلف فندق الدوسيت – التجمع الخامس – القاهرة الجديدة، N Teseen, New Cairo 1, Cairo Governorate 11835, Egypt"
work_address = "1 Al Tabeer, El-Zaytoun Sharkeya, Zeitoun, Cairo Governorate 4520120, Egypt"

# Load the Excel template
excel_file = "Private Taxi Claim Form (Ver 2; 31Jul25).xlsx"

# Read the Excel file
try:
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
    
    # Same Excel file in your script directory
    excel_file = "Private Taxi Claim Form (Ver 2; 31Jul25).xlsx"

    # Open the workbook
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

    # Save changes back to the same file
    wb.save(excel_file)
    print(f"✅ Data written directly into {excel_file}")
    
except Exception as e:
    print(f"❌ Error filling Excel form: {e}")