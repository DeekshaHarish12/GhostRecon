import streamlit as st
import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('db/logs.db')

cursor = conn.cursor()

# Streamlit UI
st.set_page_config(page_title="Honeypot Dashboard", layout="wide")
st.title("🛡️ Honeypot Login Attempt Dashboard")

# Fetch data
query = '''
SELECT id, username, password, ip_address, location_city, location_country, timestamp, prediction
FROM attack_logs
ORDER BY timestamp DESC
'''

df = pd.read_sql_query(query, conn)  # 💡 This line was missing in your code!

# Display data

if df.empty:
    st.warning("No login attempts recorded yet.")
else:
    st.metric("Total Login Attempts", len(df))
    st.dataframe(df[['id', 'username', 'password', 'ip_address', 'location_city', 'location_country', 'timestamp', 'prediction']], use_container_width=True)


    # Show a chart
    counts = df['prediction'].value_counts()
    st.subheader("🔍 Attempt Classification Summary")
    st.bar_chart(counts)

conn.close()
