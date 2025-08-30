from unittest import case
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from flask_caching import Cache
import sqlite3

app = Flask(__name__)
def load_data():
    df1 = pd.read_csv('QAPMDCDD9400.csv', sep=';')
    df1.drop(['workflow','ss-completed','retention-time', 'sum-size', 'copies','ssflags','volume' ], inplace=True, axis=1)
    df1['capacity_(GB)']=(df1['total']/1024/1024/1024).map('{:.2f}'.format)
    return df1

df1= load_data()
conn = sqlite3.connect('backup_dashboard.db')
df1.to_sql('tbl_backup_dashboard', conn, if_exists='replace')
conn.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    # Get filter values from form (or default to empty strings)
    client_filter = request.form.get('client', '')
    savetime_filter = request.form.get('date-time', '')

    # Call query function with those filters
    data = query_data(client_filter, savetime_filter)

    # Render the template with data and filters
    return render_template('home.html', data=data,
                           client=client_filter, savetime=savetime_filter)
def query_data(client_filter, savetime_filter):
    conn = sqlite3.connect('backup_dashboard.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    base_query = "SELECT * FROM tbl_backup_dashboard"
    condition = []
    params = []

    if client_filter:
        condition.append("client LIKE ?")
        params.append(f"%{client_filter}%")
    if savetime_filter:
        condition.append('"date-time" LIKE ?')
        params.append(f"%{savetime_filter}%")

    if condition:
        base_query += " WHERE " + " AND ".join(condition)

    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

if __name__ == '__main__':
    app.run()
