import streamlit as st

st.set_page_config(
    page_title="Apps",
    page_icon="🚝",
)

st.markdown("## Select an App from the sidebar")
st.markdown("1. Run Jobs: Run a job and check its status")
st.markdown("2. Plotting Demo: Plot random numbers")
st.markdown("\n")

st.sidebar.success("Select an App from above")
