import streamlit as st
import pandas as pd
import base64
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False)
    writer.book.save(output)
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename="transposed_data.xlsx", text="Download transposed data"):
    b64 = base64.b64encode(to_excel(df)).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'

st.title("Data Transposer")

# Upload files
data_file = st.file_uploader("Upload Data Download", type=['xlsx'])
target_file = st.file_uploader("Upload Target Sheet", type=['xlsx'])

if data_file and target_file:
    data_df = pd.read_excel(data_file)
    target_df = pd.read_excel(target_file)



    st.write("### Map Target Columns to Data Download Columns")
    
    mapping = {}
    for col in target_df.columns:
        options = [''] + data_df.columns.tolist()
        if not col.startswith('*'):  # If column doesn't start with '*', add an 'Exclude' option
            options.append('Exclude')

        selected_data_col = st.selectbox(f"For target column '{col}', select the matching data download column:", options, key=col)
        
        if selected_data_col and selected_data_col != 'Exclude':
            mapping[col] = selected_data_col

    if st.button("Transpose Data"):
        missed_mandatory = [col for col in target_df.columns if col.startswith('*') and col not in mapping]
        if missed_mandatory:
            st.error(f"Please map all mandatory target columns before transposing. Missed: {', '.join(missed_mandatory)}")
        else:
            transposed_data = pd.DataFrame()
            for target_col, data_col in mapping.items():
                transposed_data[target_col] = data_df[data_col]
            st.write(transposed_data)
            st.markdown(get_table_download_link(transposed_data), unsafe_allow_html=True)
