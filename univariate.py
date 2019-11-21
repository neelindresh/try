from plotly.offline import iplot, init_notebook_mode
import plotly.graph_objs as go
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.io as pio
import os
import numpy as np
import plotly.offline as plof
import plotly
init_notebook_mode(connected=True)


def univariate(df,x_col,y_col,y_start,y_end,filename):
    N = len(df)
    x = df[x_col]
    #y = y_col>=2 | y_col <= 0
    #y = lien_play[(lien_play['Original Combined LTV'] >= 2) | (lien_play['Original Combined LTV'] <=0 )] ['Original Combined LTV']
    y = df[(df[y_col] >= y_end) | (df[y_col] <=y_start )] [y_col]
    colors = np.random.rand(N)
    sz = np.random.rand(N)*30

    fig = go.Figure()
    fig.add_scatter(x=x,
                    y=y,
                    mode='markers',
                    marker={'size': sz,
                            'color': colors,
                            'opacity': 0.6,
                            'colorscale': 'Viridis'
                           });
    
    plotly.offline.plot(fig, filename = filename, auto_open=False)
    

def boxplot(df,column,filename):
    y0 = df[column]
    trace0 = go.Box(
        y=y0,
        name=column
    )

    data = [trace0]
    plotly.offline.plot(data, filename = filename, auto_open=False)  
    
def distplot(df,x_col,y_col,filename):    
    # Add histogram data
    x1 = df[x_col].dropna()
    x2 = df[y_col].dropna() 
    #x1 = lien_play[lien_play['Original Combined LTV'] > 2]['Original Combined LTV'].dropna() 
    #x2 = lien_play['Original Combined LTV'].dropna()  

    # Group data together
    hist_data = [x1, x2]

    group_labels = ['Group 1', 'Group 2']

    # Create distplot with custom bin_size
    fig = ff.create_distplot(hist_data, group_labels, bin_size=.2)

    # Plot!
    plotly.offline.plot(fig, filename = filename, auto_open=False)   

def bplot(df,x_col,y_col,filename):    
    # Add histogram data
    x1 = df[x_col].dropna()
    x2 = df[y_col].dropna() 
    #x1 = lien_play[lien_play['Original Combined LTV'] > 2]['Original Combined LTV'].dropna() 
    #x2 = lien_play['Original Combined LTV'].dropna()  

    trace0 = go.Box(
        y=x1
    )
    trace1 = go.Box(
        y=x2
    )
    data = [trace0, trace1]
    #py.iplot(data)

    # Plot!
    plotly.offline.plot(data, filename = filename, auto_open=False)   
