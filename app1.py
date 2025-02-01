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
        try:
            if "Ex-refinery" in line:
                value = lines[i+1].strip().split()[0]
                data["Value"][0] = float(value) if value.replace('.', '', 1).isdigit() else None
            elif "IFEM" in line:
                value = lines[i+1].strip().split()[0]
                data["Value"][1] = float(value) if value.replace('.', '', 1).isdigit() else None
            elif "Distributor (OMC) Margin" in line:
                value = lines[i+1].strip().split()[0]
                data["Value"][2] = float(value) if value.replace('.', '', 1).isdigit() else None
            elif "Dealer Commission" in line:
                value = lines[i+1].strip().split()[0]
                data["Value"][3] = float(value) if value.replace('.', '', 1).isdigit() else None
            elif "Petroleum Levy" in line:
                value = lines[i+1].strip().split()[0]
                data["Value"][4] = float(value) if value.replace('.', '', 1).isdigit() else None
            elif "Sales Tax" in line:
                value = lines[i+1].strip().split()[0]
                data["Value"][5] = float(value) if value.replace('.', '', 1).isdigit() else None
        except (IndexError, ValueError) as e:
            st.warning(f"Error extracting value for line: {line}. Error: {e}")

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

        # Handle duplicates by keeping the first occurrence
        all_data = all_data.drop_duplicates(subset=["Component", "Date"], keep="first")

        # Replace NaN values with None (which becomes null in JSON)
        all_data = all_data.where(pd.notnull(all_data), None)

        # Pivot the DataFrame to match the structure of Book1.xlsx
        try:
            pivot_df = all_data.pivot(index="Component", columns="Date", values="Value")
        except ValueError as e:
            st.error(f"Error while pivoting data: {e}")
            st.write("Duplicate entries detected. Please check the data.")
            st.write(all_data)
            return

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
