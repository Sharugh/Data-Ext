import streamlit as st
import pdfplumber
import pandas as pd
import os
from openpyxl import Workbook

# Function to extract data from a single PDF
def extract_data_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Split the text into lines
    lines = text.split('\n')

    # Initialize variables to store the data
    data = {
        "Component": ["Ex-refinery", "IFEM", "Distributor (OMC) Margin", "Dealer Commission", "Petroleum Levy", "Sales Tax"],
        "Value": [None] * 6,
        "Date": None
    }

    # Extract the date (assuming it's at the top of the document)
    for line in lines:
        if "Islamabad, the" in line:
            data["Date"] = line.split("Islamabad, the")[1].strip()
            break

    # Extract the required rows
    for i, line in enumerate(lines):
        if "Ex-refinery" in line:
            data["Value"][0] = float(lines[i+1].strip().split()[0])
        elif "IFEM" in line:
            data["Value"][1] = float(lines[i+1].strip().split()[0])
        elif "Distributor (OMC) Margin" in line:
            data["Value"][2] = float(lines[i+1].strip().split()[0])
        elif "Dealer Commission" in line:
            data["Value"][3] = float(lines[i+1].strip().split()[0])
        elif "Petroleum Levy" in line:
            data["Value"][4] = float(lines[i+1].strip().split()[0])
        elif "Sales Tax" in line:
            data["Value"][5] = float(lines[i+1].strip().split()[0])

    return data

# Streamlit App
def main():
    st.title("PDF Data Extractor")
    st.write("Upload scanned PDFs to extract data related to gasoline prices.")

    # Upload multiple PDFs
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} files.")

        # Initialize a DataFrame to store all data
        all_data = pd.DataFrame(columns=["Component", "Value", "Date"])

        # Extract data from each PDF
        for uploaded_file in uploaded_files:
            # Save the uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract data
            data = extract_data_from_pdf(uploaded_file.name)
            temp_df = pd.DataFrame(data)
            all_data = pd.concat([all_data, temp_df], ignore_index=True)

            # Remove the temporary file
            os.remove(uploaded_file.name)

        # Pivot the DataFrame to match the structure of Book1.xlsx
        pivot_df = all_data.pivot(index="Component", columns="Date", values="Value")

        # Display the extracted data
        st.write("Extracted Data:")
        st.dataframe(pivot_df)

        # Download the data as an Excel file
        output_path = "extracted_data.xlsx"
        pivot_df.to_excel(output_path)

        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Extracted Data as Excel",
                data=f,
                file_name="extracted_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# Run the Streamlit app
if __name__ == "__main__":
    main()
