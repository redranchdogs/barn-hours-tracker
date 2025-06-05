0,0,0,0.1);
        }
        .stButton > button {
            background-color: #a6342d !important;
            color: white !important;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
        }
        .stButton > button:hover {
            background-color: #802720 !important;
        }
        .stSelectbox div, .stDateInput, .stTimeInput, .stMultiselect {
            background-color: #fef3ec !important;
            border: 1px solid #a6342d !important;
            border-radius: 5px;
        }
        .stDownloadButton > button {
            background-color: #a6342d !important;
            color: white !important;
            border-radius: 5px;
        }
        .stDownloadButton > button:hover {
            background-color: #802720 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Barn Team Hours Tracker")

# Barn team names
barn_team_names = ["Sky", "Giselle", "Hannah", "Gabe", "Izzy", "Mia"]

# Generate 30-minute time options from 8:30 AM to 10:00 PM
def generate_time_slots(start, end, interval_minutes):
    times = []
    current = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while current <= end_dt:
        times.append(current.time())
        current += timedelta(minutes=interval_minutes)
    return times

time_options = generate_time_slots(time(8, 30), time(22, 0), 30)

# Inputs
employee = st.selectbox("Barn Team Member", barn_team_names)
date = st.date_input("Date")
hourly_rate = st.selectbox("Hourly Rate", [15, 17])
start_time = st.selectbox("Start Time", time_options, format_func=lambda t: t.strftime("%I:%M %p"))
end_time = st.selectbox("End Time", time_options, format_func=lambda t: t.strftime("%I:%M %p"))

# Validate and Add Entry
if datetime.combine(date, end_time) <= datetime.combine(date, start_time):
    st.warning("End time must be after start time.")
else:
    if st.button("Add Entry"):
        hours_worked = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).seconds / 3600
        total_pay = round(hours_worked * hourly_rate, 2)

        new_entry = {
            "Barn Team Member": employee,
            "Date": date.strftime("%m/%d/%y"),
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

# Show log and delete entries
if "log" in st.session_state and st.session_state.log:
    df = pd.DataFrame(st.session_state.log)

    st.subheader("Logged Entries")
    st.dataframe(df)

    st.subheader("Delete Entries")
    to_delete = st.multiselect("Select rows to delete", df.index, format_func=lambda i: f"{df.iloc[i]['Barn Team Member']} on {df.iloc[i]['Date']}")

    if st.button("Delete Selected"):
        st.session_state.log = [row for i, row in enumerate(st.session_state.log) if i not in to_delete]
        st.success("Selected entries deleted.")
        st.experimental_rerun()

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "barn_team_hours.csv", "text/csv")
