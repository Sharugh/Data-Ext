import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import re
import os
from datetime import datetime

# Set Tesseract Path if needed (Update path accordingly)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to extract date from the image
def extract_date(text):
    date_pattern = r"(\d{1,2}/\d{1,2}/\d{4})"  # Adjust pattern based on actual format
    match = re.search(date_pattern, text)
    return match.group(1) if match else "Unknown Date"

# Function to extract required data from OCR text
def extract_table_data(text):
    rows = text.split("\n")
    required_keywords = [
        "Ex-refinery", "IFEM", "Distributor (OMC) Margin", 
        "Dealer Commisson", "Petroleum levy", "Sales Tax"
    ]
    
    fuel_types = ["MOGAS", "E-10 Gasoline"]
    
    extracted_data = []
    for row in rows:
        if any(keyword in row for keyword in required_keywords) or any(ft in row for ft in fuel_types):
            extracted_data.append(row)
    
    return extracted_data

# Streamlit UI
st.title("📄 Extract Fuel Pricing Data from Scanned PDFs")
uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    extracted_data_list = []
    
    for file in uploaded_files:
        images = convert_from_bytes(file.read())  # Convert PDF to images
        full_text = ""

        for image in images:
            text = pytesseract.image_to_string(image)  # OCR extraction
            full_text += text + "\n"

        extracted_date = extract_date(full_text)
        extracted_data = extract_table_data(full_text)

        for row in extracted_data:
            extracted_data_list.append({"Date": extracted_date, "Data": row})

    # Convert to DataFrame and sort by Date
    df = pd.DataFrame(extracted_data_list)
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna().sort_values(by="Date")

    # Display the extracted data
    st.write("### Extracted Data")
    st.dataframe(df)

    # Save to Excel
    excel_filename = "fuel_pricing_data.xlsx"
    df.to_excel(excel_filename, index=False)

    # Provide download link
    with open(excel_filename, "rb") as f:
        st.download_button("📥 Download Excel File", f, file_name=excel_filename)

st.info("Upload scanned PDFs containing fuel pricing tables. The extracted data will be sorted by date and saved in an Excel file.")
