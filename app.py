from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
import pandas as pd

app = Flask(__name__)



@app.route('/')
def main():
  return redirect('/index')

@app.route('/index',methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('userinput.html')
    else:
        app.ticker = request.form['ticker']
        app.close_price = 'close' in request.form
        app.open_price = 'open' in request.form
        app.adj_close_price = 'adj_close' in request.form
        app.adj_open_price = 'adj_open' in request.form
        return redirect('/graph')
  
@app.route('/graph',methods = ['GET'])        
def graph():
    try:
        script, div = plotdata(app.ticker,app.close_price,app.open_price,app.adj_close_price,app.adj_open_price)
    except: 
        return render_template('errorpage.html')
    return render_template('opengraph.html',ticker=app.ticker,graphdiv=div, graphscript=script)

def plotdata(ticker, close_price='0', open_price='0', adj_close_price='0', adj_open_price='0'):
    '''Plot in Bokeh using ticker, close_price, open_price, adj_close_price, adj_open_price as inputs'''
    r=requests.get('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker='+ticker+'&qopts.columns=date,open,close,adj_open,adj_close&api_key=uxXc_yF5_QD-nhv_EbyK')
    j=r.json()['datatable']
    df = pd.DataFrame(j['data'])
    from pandas.io.json import json_normalize
    df.columns = json_normalize(j['columns'])['name']
    from bokeh.plotting import figure,show
    from bokeh.models import Range1d
    from bokeh.embed import components
   
    TOOLS="pan,wheel_zoom,box_zoom,reset,save"
    df['date']=pd.to_datetime(df['date'])
    
    xr1 = Range1d(start=min(df['date']), end = max(df['date']))
    # build our figures
    p= figure(x_range=xr1, tools=TOOLS, plot_width=600, plot_height=600)
    if open_price: 
        p.line(df['date'],df['open'],color='red',legend=': open')
    if close_price: 
        p.line(df['date'],df['close'],color='yellow', legend=': close')
    if adj_open_price: 
        p.line(df['date'],df['adj_open'],color='black',legend=': adj_open')
    if adj_close_price: 
        p.line(df['date'],df['adj_close'],color='blue',legend=': adj_close')
    script, div = components(p)
    return script, div


if __name__ == '__main__':
  app.run(port=33507)
