import streamlit as st
import pdfplumber
import pandas as pd
import os

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
        "Ex-refinery": None,
        "IFEM": None,
        "Distributor (OMC) Margin": None,
        "Dealer Commission": None,
        "Petroleum Levy": None,
        "Sales Tax": None,
        "MOGAS Retail": None,
        "E-10 Gasoline Retail": None,
        "E-10 Gasoline Direct": None,
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
            data["Ex-refinery"] = lines[i+1].strip()
        elif "IFEM" in line:
            data["IFEM"] = lines[i+1].strip()
        elif "Distributor (OMC) Margin" in line:
            data["Distributor (OMC) Margin"] = lines[i+1].strip()
        elif "Dealer Commission" in line:
            data["Dealer Commission"] = lines[i+1].strip()
        elif "Petroleum Levy" in line:
            data["Petroleum Levy"] = lines[i+1].strip()
        elif "Sales Tax" in line:
            data["Sales Tax"] = lines[i+1].strip()
        elif "MOGAS Retail" in line:
            data["MOGAS Retail"] = lines[i+1].strip()
        elif "E-10 Gasoline Retail" in line:
            data["E-10 Gasoline Retail"] = lines[i+1].strip()
        elif "E-10 Gasoline Direct" in line:
            data["E-10 Gasoline Direct"] = lines[i+1].strip()

    return data

# Streamlit App
def main():
    st.title("PDF Data Extractor")
    st.write("Upload scanned PDFs to extract data related to gasoline prices.")

    # Upload multiple PDFs
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} files.")

        # Extract data from each PDF
        data_list = []
        for uploaded_file in uploaded_files:
            # Save the uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract data
            data = extract_data_from_pdf(uploaded_file.name)
            data_list.append(data)

            # Remove the temporary file
            os.remove(uploaded_file.name)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(data_list)

        # Display the extracted data
        st.write("Extracted Data:")
        st.dataframe(df)

        # Download the data as a CSV file
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Extracted Data as CSV",
            data=csv,
            file_name="extracted_data.csv",
            mime="text/csv",
        )

# Run the Streamlit app
if __name__ == "__main__":
    main()
