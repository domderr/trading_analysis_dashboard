import pandas as pd
import yfinance as yf
import datetime
from time import strftime,gmtime
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_table.FormatTemplate as FormatTemplate
import plotly.graph_objs as go
import numpy as np

#list=pd.read_csv('C:/Users/Utente/Python/csv_lists\US1000.csv',sep=";",encoding='latin-1')
d = {'Ticker': ['AAPL', 'MSFT','GOOG','AMZN','IBM'],
     'Name': ['Apple', 'Microsoft','Google','Amazon','Ibm']}
list= pd.DataFrame(data=d)
list_symbols=[]
for symbol in list.Ticker:
    list_symbols.append(symbol)
    
start="2019-7-1"
end="2020-12-31"
mylist= list_symbols

df = yf.download(mylist, start=start,end=end,group_by='Ticker', interval='1D')
df = df.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)
df['counter']=df.groupby(['Ticker']).cumcount()
df['NetCh']=df.groupby('Ticker').Close.pct_change()
df['Avg2']=df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(2, center=False).mean())


#Add column date as string
dates=df.index
df['Date']= dates.strftime('%Y-%m-%d')

today=max(df.Date)
table_df=df[df.Date==today]
table_df=list.merge(table_df)
table_df

app = dash.Dash(__name__)

# We need to construct a dictionary of dropdown values  for the symbols 
Ticker_options = []
for ticker in range(0,len(list)):
    Ticker_options.append({'label':list.Name.loc[ticker],'value':list.Ticker.loc[ticker]})
    
server= app.server

app.layout = html.Div([
    dcc.Tabs([
        
        dcc.Tab(label='Scanner', children=[
            dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": 'Ticker',
             "id": 'Ticker',
             "deletable": False,
             "selectable": False,
             
            },
            {"name": 'Name',
             "id": 'Name',
             "deletable": False,
             "selectable": False,
             
            },
            {"name": 'NetCh',
             "id": 'NetCh',
             "deletable": False,
             "selectable": False,
             'type': 'numeric',
             'format': FormatTemplate.percentage(2)
            },
            
            {"name": 'Open',
             "id": 'Open',
             "deletable": False,
             "selectable": False,
             'type': 'numeric',
             'format': FormatTemplate.money(2)
            },
             {"name": 'High',
             "id": 'High',
             "deletable": False,
             "selectable": False,
              'type': 'numeric',
              'format': FormatTemplate.money(2)
            },
             {"name": 'Low',
             "id": 'Low',
             "deletable": False,
             "selectable": False,
              'type': 'numeric',
              'format': FormatTemplate.money(2)
            },
            {"name": 'Close',
             "id": 'Close',
             "deletable": False,
             "selectable": False,
             'type': 'numeric',
             'format': FormatTemplate.money(2)
            },
             {"name": 'Volume',
             "id": 'Volume',
             "deletable": False,
             "selectable": False
            }
        ],
        data=table_df.to_dict('records'),
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        column_selectable="none",
        row_selectable="none",
        row_deletable=False,
        #column_deletable=False,
        #selected_columns=[],
        #selected_rows=[0],
        page_action="native",
        page_current= 0,
        page_size= 20,
        style_as_list_view=True,
        #style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        #style_cell={
        #    'backgroundColor': 'rgb(50, 50, 50)',
        #    'color': 'white'
        #    },
        hidden_columns=['Adj Close','counter'],
       
        style_header={ 'border': '1px solid black' },
        style_cell={
            'height': 'auto',
            # all three widths are needed
            'minWidth': '50px', 'width': '50px', 'maxWidth': '50px',
            'whiteSpace': 'normal'
            },
        #
        #css=[{'selector': 'table', 'rule': 'table-layout: fixed'}]
        
    )
        ]),
        dcc.Tab(label='Chart', children=[
            
        # dropdown menu
        html.Div([
          dcc.Dropdown(id='ticker-picker',
                       options=Ticker_options,
                       value=list.Ticker.iloc[0],
                       style={
                           'color':'Black',
                           #'border':'2px black solid',
                           'padding':10,
                           'width':1000,
                           'height':50}
                       #direction = "vertical"
                      )]
    ),

    html.Div([
         dcc.Graph(id='graph',
                   style={'color':'black', 'border':'2px black solid',
                                     'borderRadius':5,'padding':10, 'width':1800,'height':700}
                  )]
    )    
                   
            
        ]),
    ])
])


@app.callback(Output('graph', 'figure'),
              [Input('ticker-picker', 'value')])
def update_figure(selected_ticker):                         # la funzione deve seguire ilcomanda @app
    filtered_df = df[df['Ticker'] == selected_ticker]
    
    trace0=go.Bar(
            x=filtered_df.index,
            y=filtered_df.Close,
            xaxis="x",
            yaxis="y",
            visible=True,
            showlegend=False,
            opacity=0,
            #hovertext=df.index
            hoverinfo="none",
    )
    
    
    trace1=go.Candlestick(
            x=filtered_df.counter,
            open=filtered_df.Open,
            high=filtered_df.High,
            low=filtered_df.Low,
            close=filtered_df.Close,
            xaxis="x2",
            yaxis="y",
            visible=True,
            showlegend=False,
            opacity=1,
            #hoverinfo="none",
            hovertext=filtered_df.index.strftime("%D"),
            #name="last:"+str(df.Close.iloc[-1])
    )
    
    trace2 = go.Bar(
        x=filtered_df.counter,
        y=filtered_df.Volume,
        xaxis="x2",
        yaxis="y2",
        name="Volume",
        marker_color='Green', 
        marker_line_color='Green', 
        marker_line_width=1, 
        opacity=0.6
    )
    
    
       
    data=[trace0,trace1,trace2]
    
    layout=go.Layout(
        title=go.layout.Title(text=selected_ticker),
        autosize=True,
        #width=500,
        #height=500,
        xaxis=go.layout.XAxis(
            side="bottom",
            showticklabels=True,
            tickformat = '%Y-%m-%d',
            showgrid = True
            
        ),
        yaxis=go.layout.YAxis(
            side="right",
            range=[min(filtered_df.Low)*.99, max(filtered_df.High)*1.01],# margini verticali
            showticklabels=True,
            showgrid = True,
            domain=[0.30, 1]
        ),
        xaxis2=go.layout.XAxis(
            side="top",
            showticklabels=False,
            rangeslider=go.layout.xaxis.Rangeslider(visible=False),
            showgrid = True,
            tickformat = '%Y-%m-%d',
        ),
        yaxis2=go.layout.YAxis(
            side="right",
            #range=[min(filtered_df.Volume)*.99, max(filtered_df.Volume)*1.01],# margini verticali
            showticklabels=False,
            showgrid = True,
            domain=[0, 0.25]
        ),
        plot_bgcolor ='White'
    )
        
        
    return { 'data': data,'layout': layout}
 
    
if __name__ == '__main__':
    app.run_server()
