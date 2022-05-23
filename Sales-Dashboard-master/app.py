# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from datetime import datetime
import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")

import dash
import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash import html

# create an app object using dash.Dash
from plotly.subplots import make_subplots

app = dash.Dash(__name__)
server = app.server

# To view all the columns in the dataframe
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)

# Read CSV
df = pd.read_csv("data/sales_data.csv")
df.set_index(['Close Date'])
df['year'] = pd.DatetimeIndex(df['Close Date']).year
df['month'] = pd.DatetimeIndex(df['Close Date']).month
# print(df.head(2))


# ------------- Chart 1 --------------- #

df2 = pd.read_csv("data/USA_CODE.csv")
df2 = df2.set_index('State')

map_df = df.groupby(['Billing State'])['Amount'].agg('sum').sort_values(ascending=False).reset_index()
map_df = map_df.set_index('Billing State')
result = pd.concat([map_df, df2], axis=1, join="inner")

state = result.reset_index().drop(columns=['Traditional Abbreviation'])

map_fig = go.Figure(data=go.Choropleth(
    locations=state['USPS Abbreviation'], z=state['Amount'].astype(float), locationmode='USA-states', colorscale='Blues'

))

map_fig.update_layout(
    title_text='Map: Sales by each city',
    geo_scope='usa'
)

# ------------- Chart 2 --------------- #
# Group data by year and by country ['Year-Month', 'Country'] in OrderValue
sales = df.groupby(['Billing Region'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')
print(sales.head())

# Create the line graph
bar_graph = px.bar(data_frame=sales, title='Total Sales by Region', x='Billing Region',
                   y='Total Sales ($)', color='Billing Region')

# ------------- Chart 3 --------------- #

sales_by_month = df.groupby(['month', 'Billing Region'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')

# Create the line graph
# line chart to show the sales by each region in every month and filter will be year
line_graph = px.line(data_frame=sales_by_month, title='Total Sales by Region each month', x='month',
                     y='Total Sales ($)', color='Billing Region', markers=True)
line_graph.update_layout({'xaxis': {'dtick': 1}})

# ------------- Chart 4 --------------- #

sales_by_m = df.groupby(['month', 'year'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')

sales_2011 = sales_by_m[sales_by_m['year'] == 2011].reset_index().drop(columns='index')
sales_2012 = sales_by_m[sales_by_m['year'] == 2012].reset_index().drop(columns='index')
sales_2013 = sales_by_m[sales_by_m['year'] == 2013].reset_index().drop(columns='index')
sales_2014 = sales_by_m[sales_by_m['year'] == 2014].reset_index().drop(columns='index')
sales_2015 = sales_by_m[sales_by_m['year'] == 2015].reset_index().drop(columns='index')

sub_line = make_subplots(rows=5, cols=1,shared_xaxes=True)
sub_line.add_trace(go.Scatter(x=sales_2011['month'], y= sales_2011['Total Sales ($)'],
                         mode='lines+markers', name='2011',marker_color='blue'), row=1, col=1)

sub_line.add_trace(go.Scatter(x=sales_2012['month'], y= sales_2012['Total Sales ($)'],
                         mode='lines+markers', name='2012',marker_color='green'), row=2, col=1)

sub_line.add_trace(go.Scatter(x=sales_2013['month'], y= sales_2013['Total Sales ($)'],
                         mode='lines+markers', name='2013',marker_color='red'), row=3, col=1)

sub_line.add_trace(go.Scatter(x=sales_2014['month'], y= sales_2014['Total Sales ($)'],
                         mode='lines+markers', name='2014',marker_color='black'), row=4, col=1)
sub_line.add_trace(go.Scatter(x=sales_2015['month'], y= sales_2015['Total Sales ($)'],
                         mode='lines+markers', name='2015',marker_color='purple'), row=5, col=1)


sub_line.update_layout(template='simple_white',height = 1000,
                   title='Sales per month')



line = px.line(data_frame=sales_2011, x='month', y='Total Sales ($)')


# ------------- Chart 5 --------------- #

sales_per = df.groupby(['year', 'month', 'Billing Region'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')
a = sales_per.groupby(['Billing Region'])['Total Sales ($)'].agg('sum')
b = sales_per.groupby(['Billing Region'])['Total Sales ($)'].agg('count')
b = sales_per.groupby(['year', 'Billing Region'])['Total Sales ($)'].agg('sum')
c = sales_per.groupby(['year'])['Total Sales ($)'].agg('sum')
z = b / c * 100
z = z.reset_index(name='% Total Sales ($)')

stack_bar_sales_percentage = px.bar(z, x="year", y="% Total Sales ($)", color="Billing Region",
                                    title="Sales % in each year in each region")

# ------------- Chart 6 --------------- #

prod_grp = df.groupby(['Product Name'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')
prod_grp['Total Sales in Million ($)'] = prod_grp['Total Sales ($)'] / 10000
prod_grp['prod_perc'] = prod_grp['Total Sales ($)'].transform(lambda x: x / x.sum() * 100)

y_saving = prod_grp['prod_perc'].to_list()
y_net_worth = prod_grp['Total Sales in Million ($)'].to_list()
x = prod_grp['Product Name'].to_list()

# Creating two subplots
fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                    shared_yaxes=False, vertical_spacing=0.001)

fig.append_trace(go.Bar(
    x=y_saving,
    y=x,
    marker=dict(
        color='rgba(50, 171, 96, 0.6)',
        line=dict(
            color='rgba(50, 171, 96, 1.0)',
            width=1),
    ),
    name='Product percentage of sales',
    orientation='h',
), 1, 1)

fig.append_trace(go.Scatter(
    x=y_net_worth, y=x,
    mode='lines+markers',
    line_color='rgb(128, 0, 128)',
    name='net worth, Million USD/10000 to fit the graph',
), 1, 2)

fig.update_layout(
    title='Product Contribution and Total Sales by Product Comparision',
    yaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=True,
        domain=[0, 0.85],
    ),
    yaxis2=dict(
        showgrid=False,
        showline=True,
        showticklabels=False,
        linecolor='rgba(102, 102, 102, 0.8)',
        linewidth=2,
        domain=[0, 0.85],
    ),
    xaxis=dict(
        zeroline=False,
        showline=False,
        showticklabels=True,
        showgrid=True,
        domain=[0, 0.42],
    ),
    xaxis2=dict(
        zeroline=False,
        showline=False,
        showticklabels=True,
        showgrid=True,
        domain=[0.47, 1],
        side='top',
        dtick=25000,
    ),
    legend=dict(x=0.029, y=1.038, font_size=10),
    margin=dict(l=100, r=20, t=70, b=70),
    paper_bgcolor='rgb(248, 248, 255)',
    plot_bgcolor='rgb(248, 248, 255)',
)

annotations = []

y_s = np.round(y_saving, decimals=2)
y_nw = np.rint(y_net_worth)

# Adding labels
for ydn, yd, xd in zip(y_nw, y_s, x):
    # labeling the scatter savings
    annotations.append(dict(xref='x2', yref='y2',
                            y=xd, x=ydn - 20000,
                            text='{:,}'.format(ydn) + 'M',
                            font=dict(family='Arial', size=12,
                                      color='rgb(128, 0, 128)'),
                            showarrow=False))
# labeling the bar net worth
annotations.append(dict(xref='x1', yref='y1',
                        y=xd, x=yd + 3,
                        text=str(yd) + '%',
                        font=dict(family='Arial', size=12,
                                  color='rgb(50, 171, 96)'),
                        showarrow=False))
# Source
annotations.append(dict(xref='paper', yref='paper',
                        x=-0.2, y=-0.109,
                        # text='OECD "' +
                        #      '(2015), Household savings (indicator), ' +
                        #      'Household net worth (indicator). doi: ' +
                        #      '10.1787/cfc6f499-en (Accessed on 05 June 2015)',
                        font=dict(family='Arial', size=10, color='rgb(150,150,150)'),
                        showarrow=False))

fig.update_layout(annotations=annotations)

# ------------- Chart 7 --------------- #
acc = df.groupby(['Product Name', 'Account Name'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')
top_acc = acc.sort_values(by=['Total Sales ($)'], ascending=False)
top_5 = top_acc.head(5)
print(top_5)

# Create the basic box plot
fig_box = px.box(data_frame=top_5, y='Total Sales ($)', color='Account Name')

# ------------- Chart 8 --------------- #
# Sunburst
sun_brust = df.groupby(['Billing Region', 'Opportunity Type', 'Product Name'])['Amount'].agg('sum').reset_index(
    name='Total Sales ($)')

pie = px.sunburst(sun_brust, path=['Billing Region', 'Opportunity Type', 'Product Name'],
                  values='Total Sales ($)', color='Billing Region',
                  hover_data=['Total Sales ($)'])
pie.update_layout(margin=dict(t=40, l=0, r=0, b=0),
                  title='Sales Distribution',
                  height=700,
                  # width=410,
                  paper_bgcolor='#ffffff',
                  font={'size': 16}
                  )

# ------------- Chart 9 --------------- #
# Sub Plot
prod_grp1 = df.groupby(['Stage'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')
prod_grp1['prod_perc'] = prod_grp1['Total Sales ($)'].transform(lambda x: x / x.sum() * 100)
labels = prod_grp1['Stage'].to_list()
values = prod_grp1['Total Sales ($)'].to_list()
doughnut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.7)])

# ------------- Chart 10 --------------- #
# Top Accounts

acc = df.groupby(['Billing Region','Product Name', 'Account Name'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')
top_acc = acc.sort_values(by=['Total Sales ($)'], ascending=False)
top_5_acc = top_acc.iloc[0:10]
# Create the basic box plot for checking
fig_box1 = px.bar(data_frame=top_5_acc, x ='Total Sales ($)', y = 'Account Name', color='Account Name', orientation='h')


salePerson = df.groupby(['Billing Region','Product Name', 'Account Owned By'])['Amount'].agg('sum').reset_index(name='Total Sales ($)')
top_acc = salePerson.sort_values(by=['Total Sales ($)'], ascending=False)
top_5_salesPer = top_acc.iloc[0:10]

fig_box = px.bar(data_frame=top_5_salesPer, x ='Total Sales ($)', y = 'Account Owned By', color='Account Owned By', orientation='h')

fig_box.update_layout({'bargap': 0.1})
# fig_box.show()

# Now, let's plot a Sub-plot
sub = make_subplots(rows=1, cols=2, subplot_titles=("Plot1: Top 10 Customer", "Plot2: Top 10 Sales Person"), shared_xaxes=True,
                    shared_yaxes=False, vertical_spacing=0.001 )
sub.append_trace(go.Bar(x= top_5_acc['Total Sales ($)'], y= top_5_acc['Account Name'], orientation='h'), 1, 1)
sub.append_trace(go.Bar(x= top_5_salesPer['Total Sales ($)'], y= top_5_salesPer['Account Owned By'], orientation='h'), 1, 2)

sub.update_layout(showlegend=False)

# ----------------------------------------------------------------
# App Layout
app.layout = html.Div(children=
[
    html.H1("Sales Performance Dashboard"),
    html.Span(children=[
        f"Prepared: {datetime.now().date()}",
        " by ", html.Br(),
        html.B("Sivasankari Kuppusamy, "),
        html.I(" Data Scientist")],
        style={'font-size': 14}
    ),
    dcc.Graph(id='map_fig', figure=map_fig),
    html.Span(children=[
        html.I("Chart 1: This shows the overall sales performance in each state of USA.")]),
    dcc.Graph(id='my-line-graph', figure=bar_graph),
    html.Span(children=[
        html.I("Chart 2: Executive Summary of Sales in all 5 region.")]),
    dcc.Graph(id='bar-graph', figure=line_graph),
    html.Span(children=[html.I("Chart 3: This shows the overall sales performance comapring sales of different region in every months.")]),
    dcc.Graph(id='dist-chart', figure=sub_line),
    html.Span(children=[
        html.I("Chart 4: This shows the overall sales performance in each year every months.")]),
    dcc.Graph(id='stack_bar_sales_percentage', figure=stack_bar_sales_percentage),
    html.Span(children=[
        html.I("Chart 5: This shows the percentage contribution by region in each year.")]),
    dcc.Graph(id='fig', figure=fig),
    html.Span(children=[
        html.I("Chart 6: Product Performance and it's sale contribution.")]),
    dcc.Graph(id='fig_box', figure=fig_box),
    html.Span(children=[
        html.I("Chart 7: This shows the Top 10 SalesPerson of our company who handles the biggest account.")]),
    dcc.Graph(id='pie', figure=pie),
    html.Span(children=[
        html.I("Chart 8: Sales distribution with type of industry we are in and type of product given as service")]),
    dcc.Graph(id='doughnut', figure=doughnut),
    html.Span(children=[
        html.I("Chart 9: Different types of Stages in the Product LifeCycle. ")]),
    dcc.Graph(id='sub', figure=sub),
    html.Span(children=[
        html.I("Chart 10: Comparision of Top 10 Customer and Top 10 SalesPerson.")]),


], style={'text-align': 'center', 'font-size': 22})

if __name__ == '__main__':
    app.run_server(debug=True)
