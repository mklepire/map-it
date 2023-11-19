# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

# Styling
st.markdown("""
<style>
    .reportview-container {
        background-color: #f0f0f5;
    }
    .stApp {
        background-color: black;
    }
    .reportview-container .main {
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
    }
    .reportview-container .main * {
        color: #5c5c5c;  /* Change this to your desired color */
    }
</style>
""", unsafe_allow_html=True)

# Main App

st.title("Data Transposer 🔄")

# State management
if 'page' not in st.session_state:
    st.session_state.page = 'start'
if 'next_page' not in st.session_state:
    st.session_state.next_page = False

# Welcome page
if st.session_state.page == 'start':
    st.markdown("""
    Welcome to the **Data Transposer**!
    
    This app assists in transposing data from your *Data Download* file to match the format of a *Target Sheet*. 
    Follow the steps to effortlessly transform your data.
    """)
    with st.container():
        if st.button("Let's get started!"):
            st.session_state.page = 'upload_data'
            st.session_state.next_page = True

# Data Download Upload & Preview
elif st.session_state.page == 'upload_data':
    st.subheader("Step 1: Upload your Data Download file")
    st.write("Ensure the file is in .xlsx format.")
    data_file = st.file_uploader("", type=['xlsx'])
    
    if data_file:
        st.session_state.data_df = pd.read_excel(data_file)
        st.write("### Data Download Preview:")
        st.dataframe(st.session_state.data_df.head())

        with st.container():
            if st.button("Continue to Target Sheet"):
                st.session_state.page = 'upload_target'
                st.session_state.next_page = True

# Target Sheet Upload & Preview
elif st.session_state.page == 'upload_target':
    st.subheader("Step 2: Upload your Target Sheet")
    st.write("Ensure the file is in .xlsx format.")
    target_file = st.file_uploader("", type=['xlsx'])
    
    if target_file:
        st.session_state.target_df = pd.read_excel(target_file)
        st.write("### Target Sheet Preview:")
        st.dataframe(st.session_state.target_df.head())

        with st.container():
            if st.button("Continue to Header Mapping"):
                st.session_state.page = 'map_headers'
                st.session_state.next_page = True

# Map Headers & Preview Transposed Data
elif st.session_state.page == 'map_headers':
    st.subheader("Step 3: Map Target Columns to Data Download Columns")

    mapping = {}
    for col in st.session_state.target_df.columns:
        options = [''] + st.session_state.data_df.columns.tolist()
        if not col.startswith('*'):
            options.append('Exclude')

        selected_data_col = st.selectbox(f"For target column '{col}', select the matching data download column:", 
                                         options, key=col)
        
        if selected_data_col and selected_data_col != 'Exclude':
            mapping[col] = selected_data_col

    with st.container():
        if st.button("Finish and Transpose Data"):
            missed_mandatory = [col for col in st.session_state.target_df.columns if col.startswith('*') and col not in mapping]
            if missed_mandatory:
                st.error(f"Please map all mandatory target columns before transposing. Missed: {', '.join(missed_mandatory)}")
            else:
                transposed_data = pd.DataFrame()
                for target_col, data_col in mapping.items():
                    transposed_data[target_col] = st.session_state.data_df[data_col]
                st.session_state.transposed_data = transposed_data
                st.session_state.page = 'download'
                st.session_state.next_page = True

# Display Transposed Data and Download Link
elif st.session_state.page == 'download':
    st.subheader("Your Transposed Data is Ready!")
    st.write("### Transposed Data:")
    st.dataframe(st.session_state.transposed_data)
    st.markdown(get_table_download_link(st.session_state.transposed_data), unsafe_allow_html=True)

# Check for state change and perform the necessary action
if st.session_state.next_page:
    st.session_state.next_page = False  # Reset the flag
    st.experimental_rerun()  # Force a rerun of the script

    



