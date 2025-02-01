import fitz  # PyMuPDF for text extraction
import pandas as pd
import streamlit as st
from datetime import datetime
import tempfile
import os

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    print("Extracted Text:\n", text)  # Debugging: Print the extracted text
    return text

# Function to parse the extracted text and extract required data
def parse_text_to_data(text):
    data = {}
    
    # Extract date
    date_line = [line for line in text.split("\n") if "Islamabad, the" in line]
    if date_line:
        date_str = date_line[0].split("Islamabad, the")[-1].strip()
        try:
            data["Date"] = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            data["Date"] = "Unknown Date"
    
    # Extract table data
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "E-10 Gasoline" in line:
            for j in range(i + 1, min(i + 10, len(lines))):
                if "Rs / Liter" in lines[j]:  # Header row
                    if j + 1 < len(lines):
                        values = lines[j + 1].split()
                        if len(values) >= 8:
                            try:
                                data["Ex-refinery"] = float(values[0])
                                data["IFEM"] = float(values[2])
                                data["Distributor (OMC) Margin"] = float(values[4])
                                data["Dealer Commission"] = float(values[5])
                                data["Petroleum levy"] = float(values[6])
                                data["Sales Tax"] = float(values[7])
                                data["MOGAS Retail"] = float(values[8])
                                data["E-10 Gasoline Retail"] = float(values[9])
                                data["E-10 Gasoline Direct"] = float(values[10])
                            except (IndexError, ValueError) as e:
                                print(f"Error parsing data: {e}")
                        break
    return data

# Streamlit app
def main():
    st.title("E-10 Gasoline Price Data Extractor")

    # Upload PDF files
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        data_list = []
        for uploaded_file in uploaded_files:
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                # Extract text from the PDF
                text = extract_text_from_pdf(tmp_file_path)
                
                # Parse the text to extract data
                data = parse_text_to_data(text)
                
                # Append the data to the list
                if data:
                    data_list.append(data)
            finally:
                # Clean up the temporary file
                os.unlink(tmp_file_path)
        
        # Convert the list of dictionaries to a DataFrame
        if data_list:
            df = pd.DataFrame(data_list)
            
            # Display the DataFrame
            st.write("### Extracted Data")
            st.dataframe(df)
            
            # Export data to Excel
            excel_file = "extracted_data.xlsx"
            df.to_excel(excel_file, index=False)
            
            # Provide a download link for the Excel file
            st.write("### Download Extracted Data")
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="Download Excel File",
                    data=file,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No data extracted from the uploaded PDFs.")
    else:
        st.info("Please upload PDF files to extract data.")

if __name__ == "__main__":
    main()
    with open(excel_filename, "rb") as f:
        st.download_button("📥 Download Excel File", f, file_name=excel_filename)

st.info("Upload scanned PDFs containing fuel pricing tables. The extracted data will be sorted by date and saved in an Excel file.")
