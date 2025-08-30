from unittest import case
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from flask_caching import Cache


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Load data once and cache it
@cache.cached(timeout=300)
def load_data():
    df1 = pd.read_csv('QAPMDCDD9400.csv', sep=';')
    df1.drop(['workflow','ss-completed','retention-time', 'sum-size', 'copies','ssflags','volume' ], inplace=True, axis=1)
    df1['capacity_(GB)']=(df1['total']/1024/1024/1024).map('{:.2f}'.format)
    return df1

@app.route('/', methods=['GET', 'POST'])
def home():
    df1 = load_data()
    filter_df1 = df1.copy()
    df1_client_filter = ''
    df1_savetime_filter = ''

    if request.method == 'POST':
        df1_client_filter = request.form['client']
        df1_savetime_filter = request.form['savetime']

        if df1_client_filter:
            filter_df1 = filter_df1[filter_df1['client'].str.contains(df1_client_filter, case=False,na=False)]
        if df1_savetime_filter:
            filter_df1 = filter_df1[filter_df1['savetime'].str.contains(df1_savetime_filter, case=False)]
    return render_template('home.html', data=filter_df1.to_dict(orient='records'),
                           client=df1_client_filter, savetime=df1_savetime_filter)
if __name__ == '__main__':
    app.run()




