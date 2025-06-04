import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Barn Team Hours Tracker")

# Input fields
employee = st.text_input("Employee Name")
date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")
hourly_rate = st.selectbox("Hourly Rate", [15, 17])

# Calculate and add entry
if st.button("Add Entry"):
    hours_worked = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).seconds / 3600
    total_pay = hours_worked * hourly_rate
    
    new_entry = {
        "Employee": employee,
        "Date": date.strftime("%m/%d/%y"),
        "Start": start_time.strftime("%I:%M %p"),
        "End": end_time.strftime("%I:%M %p"),
        "Hours Worked": round(hours_worked, 2),
        "Hourly Rate": hourly_rate,
        "Pay": round(total_pay, 2)
    }

    if "log" not in st.session_state:
        st.session_state.log = []

    st.session_state.log.append(new_entry)
    st.success("Entry added!")

# Show table
if "log" in st.session_state and st.session_state.log:
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "barn_team_hours.csv", "text/csv")
