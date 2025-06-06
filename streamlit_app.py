import streamlit as st
import pandas as pd
import gspread
from datetime import datetime, time, timedelta
from google.oauth2 import service_account

# Authenticate with Google Sheets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["GOOGLE_SHEETS_KEY"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)
sheet = gc.open("Barn Team Hours").sheet1

# Load existing data
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Barn team names
barn_team_names = ["Sky", "Giselle", "Hannah", "Gabe", "Izzy", "Mia"]

# Time options (30-min slots from 8:30 AM to 10:00 PM)
def generate_time_slots(start, end, interval_minutes):
    times = []
    current = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while current <= end_dt:
        times.append(current.time())
        current += timedelta(minutes=interval_minutes)
    return times

time_options = generate_time_slots(time(8, 30), time(22, 0), 30)

# Determine pay period
def get_pay_period(date_obj):
    return "Pay Period 1" if date_obj.day <= 15 else "Pay Period 2"

# Input form
st.title("Barn Team Hours Tracker")
employee = st.selectbox("Barn Team Member", barn_team_names)
date = st.date_input("Date")
start_time = st.selectbox("Start Time", time_options, format_func=lambda t: t.strftime("%I:%M %p"))
end_time = st.selectbox("End Time", time_options, format_func=lambda t: t.strftime("%I:%M %p"))
hourly_rate = st.selectbox("Hourly Rate", [15, 17])

# Submit entry
if datetime.combine(date, end_time) <= datetime.combine(date, start_time):
    st.warning("End time must be after start time.")
elif st.button("Add Entry"):
    hours_worked = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).seconds / 3600
    total_pay = round(hours_worked * hourly_rate, 2)
    pay_period = get_pay_period(date)
    month_str = date.strftime("%B %Y")

    row = [
        employee,
        date.strftime("%m/%d/%Y"),
        month_str,
        pay_period,
        start_time.strftime("%I:%M %p"),
        end_time.strftime("%I:%M %p"),
        round(hours_worked, 2),
        hourly_rate,
        total_pay
    ]

    sheet.append_row(row)
    st.success("Entry added to Google Sheet.")
    st.experimental_rerun()

# Pay period summary
if not df.empty:
    st.subheader("Generate Pay Period Summary")
    selected_month = st.selectbox("Select Month", sorted(df["Month"].unique(), reverse=True))
    selected_period = st.selectbox("Select Pay Period", ["Pay Period 1", "Pay Period 2"])

    filtered = df[(df["Month"] == selected_month) & (df["Pay Period"] == selected_period)]

    if not filtered.empty:
        grouped = filtered.groupby("Barn Team Member")[["Hours Worked", "Pay"]].sum().reset_index()
        grouped["Hours Worked"] = grouped["Hours Worked"].round(2)
        grouped["Pay"] = grouped["Pay"].round(2)

        st.write(f"Summary for {selected_period} of {selected_month}")
        st.dataframe(grouped)

        # Download summary
        csv = grouped.to_csv(index=False).encode('utf-8')
        st.download_button("Download Summary CSV", csv, "pay_period_summary.csv", "text/csv")

        # Generate text messages
        st.subheader("Generate Text Messages")
        if st.button("Generate Messages"):
            messages = []
            for name in grouped["Barn Team Member"]:
                entries = filtered[filtered["Barn Team Member"] == name]
                if entries.empty:
                    continue
                message = f"Hey {name}, here’s your hours for {selected_period} ({selected_month}):\n"
                for _, row in entries.iterrows():
                    message += f"- {row['Date']}: {row['Hours Worked']} hrs (${row['Pay']})\n"
                message += f"Total: {entries['Hours Worked'].sum()} hrs – ${entries['Pay'].sum():.2f}"
                messages.append((name, message))

            for name, msg in messages:
                st.markdown(f"**{name}**")
                st.code(msg, language="text")
