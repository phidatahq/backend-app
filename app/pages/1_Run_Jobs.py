from typing import Optional

import streamlit as st

# -*- List of test jobs
Jobs = {
    "Test 1": "path_to_test_1",
    "Test 2": "path_to_test_3",
    "Test 3": "path_to_test_3",
}


# -*- Run a job
def run_job(job_name: Optional[str] = None) -> None:
    if job_name is None:
        st.write("No job selected")
        return
    st.write(f"Running job: {job_name}")


#
# -*- Create Sidebar
#
def create_sidebar():
    st.sidebar.markdown("## Settings")

    selected_job = st.sidebar.selectbox("Select a job", Jobs.keys())
    if selected_job is not None and selected_job in Jobs:
        st.session_state["selected_job"] = selected_job
        st.session_state["selected_job_path"] = Jobs[selected_job]

    if st.sidebar.button("Run"):
        run_job(selected_job)

    st.sidebar.markdown("---")

    if st.sidebar.button("Reload Session"):
        st.session_state.clear()
        st.experimental_rerun()


#
# -*- Run the app
#
create_sidebar()
