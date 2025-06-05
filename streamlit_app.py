import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

st.title("Barn Team Hours Tracker")

# Barn team list
barn_team_names = ["Sky", "Giselle", "Hannah", "Gabe", "Izzy", "Mia"]

# Create time slots from 8:30 AM to 10:00 PM
def generate_time_slots(start, end, interval_minutes):
    times = []
    current = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while current <= end_dt:
        times.append(current.time())
        current += timedelta(minutes=interval_minutes)
    return times

time_options = generate_time_slots(time(8, 30), time(22, 0), 30)

# Get pay period based on date
def get_pay_period(date_obj):
    return "Pay Period 1" if date_obj.day <= 15 else "Pay Period 2"

# Input fields
employee = st.selectbox("Barn Team Member", barn_team_names)
date = st.date_input("Date")
start_time = st.selectbox("Start Time", time_options, format_func=lambda t: t.strftime("%I:%M %p"))
end_time = st.selectbox("End Time", time_options, format_func=lambda t: t.strftime("%I:%M %p"))
hourly_rate = st.selectbox("Hourly Rate", [15, 17])

if datetime.combine(date, end_time) <= datetime.combine(date, start_time):
    st.warning("End time must be after start time.")
else:
    if st.button("Add Entry"):
        hours_worked = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).seconds / 3600
        total_pay = round(hours_worked * hourly_rate, 2)
        pay_period = get_pay_period(date)
        month_str = date.strftime("%B %Y")

        new_entry = {
            "Barn Team Member": employee,
            "Date": date.strftime("%m/%d/%Y"),
            "Month": month_str,
            "Pay Period": pay_period,
            "Start": start_time.strftime("%I:%M %p"),
            "End": end_time.strftime("%I:%M %p"),
            "Hours Worked": round(hours_worked, 2),
            "Hourly Rate": hourly_rate,
            "Pay": total_pay
        }

        if "log" not in st.session_state:
            st.session_state.log = []

        st.session_state.log.append(new_entry)
        st.success("Entry added!")

# Display full log
if "log" in st.session_state and st.session_state.log:
    df = pd.DataFrame(st.session_state.log)

    st.subheader("Logged Entries")
    st.dataframe(df)

    # Delete entries
    st.subheader("Delete Entries")
    to_delete = st.multiselect("Select rows to delete", df.index, format_func=lambda i: f"{df.iloc[i]['Barn Team Member']} on {df.iloc[i]['Date']}")

    if st.button("Delete Selected"):
        st.session_state.log = [row for i, row in enumerate(st.session_state.log) if i not in to_delete]
        st.success("Selected entries deleted.")
        st.experimental_rerun()

    # Download full log
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Full CSV", csv, "barn_team_hours.csv", "text/csv")

    # Pay period summary
    st.subheader("Generate Pay Period Summary")
    all_months = df["Month"].unique()
    selected_month = st.selectbox("Select Month", sorted(all_months, reverse=True))
    selected_period = st.selectbox("Select Pay Period", ["Pay Period 1", "Pay Period 2"])

    if st.button("Generate Summary"):
        summary_df = df[(df["Month"] == selected_month) & (df["Pay Period"] == selected_period)]
        if summary_df.empty:
            st.info("No entries found for this period.")
        else:
            grouped = summary_df.groupby("Barn Team Member")[["Hours Worked", "Pay"]].sum().reset_index()
            grouped["Hours Worked"] = grouped["Hours Worked"].round(2)
            grouped["Pay"] = grouped["Pay"].round(2)

            st.write(f"Summary for {selected_period} of {selected_month}")
            st.dataframe(grouped)

            summary_csv = grouped.to_csv(index=False).encode('utf-8')
            st.download_button("Download Summary CSV", summary_csv, "pay_period_summary.csv", "text/csv")
