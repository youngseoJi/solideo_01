import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")

st.title("Excel-based Q&A")

def process_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write("### Preview")
        st.dataframe(df.head())
        
        return df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

col1, col2 = st.columns(2)

with col1:
    st.header("Upload File")
    uploaded_file = st.file_uploader("Drag and drop or click to upload", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        df = process_file(uploaded_file)
        st.session_state['df'] = df

with col2:
    st.header("Ask a question")
    if 'df' in st.session_state and st.session_state['df'] is not None:
        question = st.text_input("Enter your question:")
        
        output_format = st.selectbox(
            "Choose an output format:",
            ('Natural Language', 'Table', 'JSON'),
            key='output_format'
        )

        if st.button("Get Answer"):
            if question:
                try:
                    df = st.session_state['df']
                    # The names are in the first column, starting from the second row (index 1)
                    # as the first row is the header.
                    names = df.iloc[1:, 0].dropna().unique()
                    
                    found_name = None
                    for name in names:
                        if name in question:
                            found_name = name
                            break
                    
                    if found_name:
                        # The data for the found name is in the row where the first column matches the name.
                        result_df = df[df.iloc[:, 0] == found_name]
                        st.write("### Answer")

                        if st.session_state.output_format == 'Natural Language':
                            name = result_df.iloc[0, 0]
                            # Assuming the second column is the vacation date
                            vacation_date = result_df.iloc[0, 1]
                            # Get the column header for the vacation date
                            column_name = df.columns[1]
                            st.success(f"{name}님의 {column_name}는 {vacation_date} 입니다.")
                        elif st.session_state.output_format == 'Table':
                            st.dataframe(result_df)
                        elif st.session_state.output_format == 'JSON':
                            st.json(result_df.to_dict(orient='records')[0])
                    else:
                        st.write("No results found for your question.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a question.")
    else:
        st.info("Please upload a file first.")
