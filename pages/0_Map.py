import streamlit as st
import pandas as pd
import base64
from io import BytesIO




# Helper Functions

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False)
    writer.book.save(output)
    return output.getvalue()

def get_table_download_link(df, filename="transposed_data.xlsx", text="Download transposed data"):
    b64 = base64.b64encode(to_excel(df)).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'

# Main App

st.title("Data Transposer")

# State management
if 'page' not in st.session_state:
    st.session_state.page = 'start'

# Welcome page
if st.session_state.page == 'start':
    st.write("Welcome to the Data Transposer!")
    if st.button("Let's get started!"):
        st.session_state.page = 'upload_data'

# Data Download Upload & Preview
elif st.session_state.page == 'upload_data':
    data_file = st.file_uploader("Upload Data Download", type=['xlsx'])
    
    if data_file:
        st.session_state.data_df = pd.read_excel(data_file)
        st.write("### Data Download Preview:")
        st.dataframe(st.session_state.data_df.head())

        if st.button("Continue"):
            st.session_state.page = 'upload_target'

# Target Sheet Upload & Preview
elif st.session_state.page == 'upload_target':
    target_file = st.file_uploader("Upload Target Sheet", type=['xlsx'])
    
    if target_file:
        st.session_state.target_df = pd.read_excel(target_file)
        st.write("### Target Sheet Preview:")
        st.dataframe(st.session_state.target_df.head())

        if st.button("Continue"):
            st.session_state.page = 'map_headers'

# Map Headers & Preview Transposed Data
elif st.session_state.page == 'map_headers':
    st.write("### Map Target Columns to Data Download Columns")

    mapping = {}
    for col in st.session_state.target_df.columns:
        options = [''] + st.session_state.data_df.columns.tolist()
        if not col.startswith('*'):  # If column doesn't start with '*', add an 'Exclude' option
            options.append('Exclude')

        selected_data_col = st.selectbox(f"For target column '{col}', select the matching data download column:", 
                                         options, key=col)
        
        if selected_data_col and selected_data_col != 'Exclude':
            mapping[col] = selected_data_col

    if st.button("Finish"):
        missed_mandatory = [col for col in st.session_state.target_df.columns if col.startswith('*') and col not in mapping]
        if missed_mandatory:
            st.error(f"Please map all mandatory target columns before transposing. Missed: {', '.join(missed_mandatory)}")
        else:
            transposed_data = pd.DataFrame()
            for target_col, data_col in mapping.items():
                transposed_data[target_col] = st.session_state.data_df[data_col]
            st.session_state.transposed_data = transposed_data
            st.session_state.page = 'download'

# Display Transposed Data and Download Link
elif st.session_state.page == 'download':
    st.write("### Transposed Data:")
    st.dataframe(st.session_state.transposed_data)
    st.markdown(get_table_download_link(st.session_state.transposed_data), unsafe_allow_html=True)


