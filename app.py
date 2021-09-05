import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import timeit
import seaborn as sns
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

df = pd.read_csv("vehicle_data.csv")
df.head()

#For Price Column
df['Price'] = df['Price'].apply(lambda a: str(a).replace("Rs",""))
df['Price'] = df['Price'].apply(lambda a: str(a).replace(",",""))
df['Price'] = df['Price'].astype(float)

#For Capacity
df['Capacity'] = df['Capacity'].apply(lambda a: str(a).replace("cc",""))
df['Capacity'] = df['Capacity'].apply(lambda a: str(a).replace(",",""))
df['Capacity'] = df['Capacity'].astype(int)

#For Mileage
df['Mileage'] = df['Mileage'].apply(lambda a: str(a).replace("km",""))
df['Mileage'] = df['Mileage'].apply(lambda a: str(a).replace(",",""))
df['Mileage'] = df['Mileage'].astype(int)

#Cleaned Dataset with Renamed Column
df = df.rename(columns={'Price': 'Price_rs','Capacity': 'Capacity_cc','Mileage': 'Mileage_km'})

#Getting only those Columns that we need, so Drop that we don't need
data = df.drop(['Sub_title','Edition'],axis=1)
data[['Brand','Model']]
data['Brand_Model'] = data['Brand'] + " " + data['Model']
data = data.drop(['Brand','Model'],axis=1)
#Dataset Cleaned for all nan Values and Replaced with MODE
data['Body'] = data['Body'].fillna(data['Body'].mode()[0])

car = data[['Brand_Model','Price_rs','Year','Condition','Transmission','Body','Fuel','Capacity_cc','Mileage_km','Seller_name','Seller_type']]
car['serial'] = car.index
car = car[['serial','Brand_Model','Price_rs','Year','Condition','Transmission','Body','Fuel','Capacity_cc','Mileage_km','Seller_name','Seller_type']]
car.head(1)
car['Year'] = pd.to_datetime(car['Year'].astype(str)).values
car.head(1)
#Getting count of Used, New and Re-Conditioned Cars
print("New Cars :",len(car[car['Condition'] == 'New']))
print("Reconditioned Cars :",len(car[car['Condition'] == 'Reconditioned']))
print("Used Cars :",len(car[car['Condition'] == 'Used']))

# --------------------------- Brand Model Based Analysis ---------------------------------------#

#Price of Cars Brand Model Scatter Plot with Conditions
fig1 = px.bar(car, x=car['Brand_Model'], y=car['Price_rs'],color='Body')
fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
#Pie Char Making for Transmissions
def carConditionData(data):
    rating = data.groupby(['Brand_Model', 'Condition','Transmission']).agg({'serial': 'count'}).reset_index()
    rating = rating[rating['serial'] != 0]
    rating.columns = ['Brand_Model', 'Condition','Transmission','count']
    rating = rating.sort_values('count',ascending=False)
    return rating

car_new = car[car['Condition'] == 'New']
car_re = car[car['Condition'] == 'Reconditioned']
car_use = car[car['Condition'] == 'Used']

car_newdf = carConditionData(car_new)
car_redf = carConditionData(car_re)
car_usedf = carConditionData(car_use)


fig2 = make_subplots(rows=1, cols=3, specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]])

fig2.add_trace(
    go.Pie(labels=car_newdf['Transmission'], values=car_newdf['count']),
    row=1, col=1
)

fig2.add_trace(
    go.Pie(labels=car_redf['Transmission'], values=car_redf['count']),
    row=1, col=2
)

fig2.add_trace(
    go.Pie(labels=car_usedf['Transmission'], values=car_usedf['count']),
    row=1, col=3
)

fig2.update_traces(textposition='outside', hole=.4, hoverinfo="label+percent")
fig2.update_layout(
    title_text="Transmission in Each Conditioned DataFrame",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text='New', x=0.13, y=0.5, font_size=12, showarrow=False),
                 dict(text='Reconditioned', x=0.50, y=0.5, font_size=12, showarrow=False),
                 dict(text='Used', x=0.87, y=0.5, font_size=12, showarrow=False)])


#Histogram Plot with Filters to See the Select Car Details (Mileage and Capacity)
def carSelect(carModel,seller):
  selected = car[car['Brand_Model'] == carModel]
  selected = selected[selected['Seller_type'] == seller]
  return selected

#Top Seller Having Most Number of Cars
dataSeller = car[['Price_rs','Seller_name']].groupby('Seller_name').sum()
dataSeller = pd.DataFrame(dataSeller.to_records()) # Multi index to Single Index
dataSeller = dataSeller.sort_values(by=['Price_rs'], ascending=False)
dataSeller = dataSeller[:10]

figSeller = px.bar(dataSeller,x = dataSeller['Seller_name'], y=dataSeller['Price_rs'],color='Price_rs', title = "Top 10 Most Successfull Seller in Sri Lanka having Most Numbers of Cars")
figSeller.update_yaxes(visible =False, showticklabels=False)
figSeller.update_xaxes(visible =False, showticklabels=False)

#----------------------------------------- Condition Based Analysis -------------------------------------------------#
cond = data[['Brand_Model','Price_rs','Year','Condition','Mileage_km']]
def conditionPriceCompare(model):
  result = []
  #New
  data_new = cond[(cond['Brand_Model'] == model) & (car['Condition'] == 'New')]
  data_new = data_new.sort_values(by='Mileage_km',ascending=False)
  if len(data_new) > 0:
    result.append(data_new[:1].values[0])
  else:
    print("Car in this Condition Not Available")
    result.append([model, 0, 0, 'New', 0])
  #Reconditioned 
  data_recond = cond[(cond['Brand_Model'] == model) & (car['Condition'] == 'Reconditioned')]
  data_recond = data_recond.sort_values(by='Mileage_km',ascending=False)
  if len(data_recond) > 0:
    result.append(data_recond[:1].values[0])
  else:
    print("Car in this Condition Not Available")
    result.append([model, 0, 0, 'Reconditioned', 0])
  #Used
  data_used = cond[(cond['Brand_Model'] == model) & (car['Condition'] == 'Used')]
  data_used = data_used.sort_values(by='Mileage_km',ascending=False)
  if len(data_used) > 0:
    result.append(data_used[:1].values[0])
  else:
    print("Car in this Condition Not Available")
    result.append([model, 0, 0, 'Used', 0])
  
  return result

#Which Seller has Most New, Used and Reconditioned Car
new = car[car['Condition'] == 'New']
new_2 = new[['Condition','Seller_name']].groupby('Seller_name').count()
new_2 = pd.DataFrame(new_2.to_records())
new_cars_seller = new_2.sort_values(by='Condition',ascending=False).values[:5]
newdf = pd.DataFrame(new_cars_seller,columns = ['Seller_name','Count'])
newdf['Condition'] = 'New'

old = car[car['Condition'] == 'Used']
old_2 = old[['Condition','Seller_name']].groupby('Seller_name').count()
old_2 = pd.DataFrame(old_2.to_records())
old_cars_seller = old_2.sort_values(by='Condition',ascending=False).values[:5]
olddf = pd.DataFrame(old_cars_seller,columns = ['Seller_name','Count'])
olddf['Condition'] = 'Used'

recon = car[car['Condition'] == 'Reconditioned']
recon = recon[['Condition','Seller_name']].groupby('Seller_name').count()
recon = pd.DataFrame(recon.to_records())
recon_cars_seller = recon.sort_values(by='Condition',ascending=False).values[:5]
recondf = pd.DataFrame(recon_cars_seller,columns = ['Seller_name','Count'])
recondf['Condition'] = 'Reconditioned'

seller_con = pd.concat([newdf, olddf,recondf]).reset_index(drop=True)
seller_con['Count'] = seller_con['Count'].astype(int)

condseller = px.bar(seller_con, x=seller_con['Seller_name'], y=seller_con['Count'],color='Condition',title="Which Seller has Most New, Used and Reconditioned Car? See the Graph Below!")
condseller.update_yaxes(visible =False, showticklabels=False)
condseller.update_xaxes(visible =False, showticklabels=False)

# ---------------------------------------------------------TRANSMISSION and Body --------------------------#
tran = data[['Brand_Model','Condition','Transmission','Body','Mileage_km','Price_rs']]
trandif2 =px.histogram(tran, x=tran['Transmission'],color='Condition',title='All Transmission Based on Conditions, Most Used is "Automatic"')
trandif2.update_yaxes(visible =False, showticklabels=False)
trandif2.update_xaxes(visible =False, showticklabels=False)

bodyfig = px.histogram(tran, x=tran['Body'],color='Condition',title='All Body Type based on Conditions, Most Used is "Hatchback"')
bodyfig.update_yaxes(visible =False, showticklabels=False)
bodyfig.update_xaxes(visible =False, showticklabels=False)


#-------------------------------------------------------------External Style Sheet Added-------------------------#
external_stylesheets = ['E:\\Sensex Prediction\\Car Analysis\\assets\\style.css']
app = dash.Dash(external_stylesheets=[external_stylesheets,dbc.themes.UNITED])
app.title = "FreeBirds Crew : Car Price Analysis and Dashboard"
app = dash.Dash(__name__)
#------------------------------------------------------------------Dash App Layout Work---------------------------------------------------------#
app.layout = dbc.Container(fluid=True, children=[
	#HEADER
    html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🦅", className="header-emoji"),
                html.H1(
                    children="FreeBirds Crew", className="header-title"
                ),
                html.P(
                    children="Analyse the Sri Lanka Car Price Dataset to Filter Out Cars based Brand and Model",
                    className="header-description",
                ),
            ],
            className="header",
        ),
	
	#FILTERS
	html.Div(
    children=[
        html.Div(
            children=[
                html.Div(children="Condition", className="menu-title"),
                dcc.Dropdown(
                    id="conditionfilter",
                    options=[
                        {"label": condition, "value": condition}
                        for condition in np.sort(car.Condition.unique())
                    ],
                    value="New",
                    clearable=False,
                    className="dropdown",
                ),
            ]
        ),
        html.Div(
            children=[
                html.Div(children="Transmission", className="menu-title"),
                dcc.Dropdown(
                    id="transmissionfilter",
                    options=[
                        {"label": Transmission, "value": Transmission}
                        for Transmission in car.Transmission.unique()
                    ],
                    value="Automatic",
                    clearable=False,
                    searchable=False,
                    className="dropdown",
                ),
            ],
        ),
		html.Div(
            children=[
                html.Div(children="Fuel", className="menu-title"),
                dcc.Dropdown(
                    id="fuelfilter",
                    options=[
                        {"label": fuel, "value": fuel}
                        for fuel in car.Fuel.unique()
                    ],
                    value="Petrol",
                    clearable=False,
                    searchable=False,
                    className="dropdown",
                ),
            ],
        ),
        html.Div(
            children=[
                html.Div(
                    children="Date Range",
                    className="menu-title"
                    ),
                dcc.DatePickerRange(
                    id="daterange",
                    min_date_allowed=car.Year.min().date(),
                    max_date_allowed=car.Year.max().date(),
                    start_date=car.Year.min().date(),
                    end_date=car.Year.max().date(),
                ),
            ]
        ),
    ],
    className="menu",
	),
	html.Br(),
	html.Br(),
	#GRAPH_1
	html.Div(
    children=[
        html.Div(
            children=dcc.Graph(
                id="price-chart",
                config={"displayModeBar": False},
                figure=fig1,
            ),
            className="card",
        ),
	]
	),
    #GRAPH_2
    html.Div(
    children=[
        html.Div(
            children=dcc.Graph(
                id="pie-chart",
                config={"displayModeBar": False},
                figure=fig2,
            ),
            className="card",
        ),
    ]
    ),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div(
    children=[
    html.Div(
            children=[
                html.Div(children="Brand Model Name", className="menu-title"),
                dcc.Dropdown(
                    id="modelfilter",
                    options=[
                        {"label": model, "value": model}
                        for model in car.Brand_Model.unique()
                    ],
                    value="Land Rover Range Rover",
                    clearable=False,
                    searchable=False,
                    className="dropdown",
                ),
            ],
        ),
    html.Div(
            children=[
                html.Div(children="Seller Type", className="menu-title"),
                dcc.Dropdown(
                    id="sellertype",
                    options=[
                        {"label": seller, "value": seller}
                        for seller in car.Seller_type.unique()
                    ],
                    value="Member",
                    clearable=False,
                    searchable=False,
                    className="dropdown",
                ),
            ],
        ),
        html.Div(id='dd-output-container', className='modelname')
      ],
      className="menu",
    ),
    html.Br(),
    html.Div(
    children=[
        html.Div(
            children=
            dcc.Graph(id="hist-chart",
                config={"displayModeBar": False},),
            className="card",
            ),
        ]
    ),
    html.Br(),
    html.Div(
    children=[
        html.Div(
            children=
            dcc.Graph(figure=figSeller,
                config={"displayModeBar": False},),
            className="card",
            ),
        ]
    ),
    html.Br(),
    html.Br(),
    #HEADER
    html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🦅", className="header-emoji"),
                html.H1(
                    children="FreeBirds Crew", className="header-title"
                ),
                html.P(
                    children="EDA on the Basis of Condition and Impact on Price",
                    className="header-description",
                ),
            ],
            className="header",
       ),
        html.Div(
        	children=[
        	html.Div(
        		children=[
                html.Div(children="Brand Model Name", className="menu-title"),
                dcc.Dropdown(
                    id="condfilter",
                    options=[
                        {"label": modelcond, "value": modelcond}
                        for modelcond in car.Brand_Model.unique()
                    ],
                    value="Land Rover Range Rover",
                    clearable=False,
                    searchable=False,
                    className="dropdown",
                ),
            ],
        ),
        	html.Div(id='dd-output-container_cond', className='modelname')
      ],
      className="menu",
      ),
        html.Br(),
        html.Br(),
        html.Div(
        	children=[
        	html.Div(
        		children=
            	dcc.Graph(id="condchartmodel",
                	config={"displayModeBar": False},),
            className="card",
            ),
        ]
    ),
    html.Br(),
    html.Div(
    children=[
        html.Div(
            children=
            dcc.Graph(figure=condseller,
                config={"displayModeBar": False},),
            className="card",
            ),
        ]
    ),
    html.Br(),
    html.Br(),
    #HEADER
    html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🦅", className="header-emoji"),
                html.H1(
                    children="FreeBirds Crew", className="header-title"
                ),
                html.P(
                    children="Analysis on the basis of Transmission and Body and Which is Best !",
                    className="header-description",
                ),
            ],
            className="header",
        ),
    
    #FILTERS
    html.Div(
    children=[
    html.Div(
        children=[
        html.Div(children="Transmission2", className="menu-title"),
        dcc.Dropdown(
            id="transmissionfilter2",
                    options=[
                        {"label": Tran, "value": Tran}
                        for Tran in data.Transmission.unique()
                    ],
                    value="Automatic",
                    clearable=False,
                    searchable=False,
                    className="dropdown",
                ),
            ],
        ),
        html.Div(
            children=[
                html.Div(children="Body", className="menu-title"),
                dcc.Dropdown(
                    id="bodyfilter",
                    options=[
                        {"label": body, "value": body}
                        for body in data.Body.unique()
                    ],
                    value="Saloon",
                    clearable=False,
                    searchable=False,
                    className="dropdown",
                ),
            ],
        ),
    ],
    className="menu",
    ),
     html.Br(),
        html.Br(),
        html.Div(
            children=[
            html.Div(
                children=
                dcc.Graph(id="tranchart",
                    config={"displayModeBar": False},),
            className="card",
            ),
        ]
    ),
        html.Br(),
        html.Div(
    children=[
        html.Div(
            children=
            dcc.Graph(figure=trandif2,
                config={"displayModeBar": False},),
            className="card",
            ),
        ]
    ),
        html.Br(),
        html.Div(
    children=[
        html.Div(
            children=
            dcc.Graph(figure=bodyfig,
                config={"displayModeBar": False},),
            className="card",
            ),
        ]
    )


])])
])
])

@app.callback(
    dash.dependencies.Output('condchartmodel', 'figure'),
    [dash.dependencies.Input('condfilter', 'value')])
def cond_ModeDetail(modelcondfilter):
    res = conditionPriceCompare(modelcondfilter)
    df_cond = pd.DataFrame(res,columns =['Brand_Model', 'Price_rs','Year','Condition','Mileage_km'])
    figc1 = px.bar(df_cond,x = df_cond['Mileage_km'], y=df_cond['Price_rs'],color='Condition', title='Get to know the Price Distribution in different conditions and impact on Price by Mileage_Km')
    return figc1


@app.callback(Output("price-chart", "figure"),
    [
        Input("conditionfilter", "value"),
        Input("transmissionfilter", "value"),
		Input("fuelfilter", "value"),
        Input("daterange", "start_date"),
        Input("daterange", "end_date"),
    ],
)

def update_charts(condition, Transmission, fuel, start_date, end_date):
    mask = (
        (car.Condition == condition)
        & (car.Transmission == Transmission)
		& (car.Fuel == fuel)
        & (car.Year >= start_date)
        & (car.Year <= end_date)
		
    )
    filtered_data = car.loc[mask, :]
    updated_fig1 = {
        "data": [
            {
                "x": filtered_data["Brand_Model"],
                "y": filtered_data["Price_rs"],
                "type": "bar",
				"color" : "Body",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Car Brand Model Shows Up with Price Based on Condition - Transmission - Fuel - Date Range",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }
    return updated_fig1


@app.callback(
    Output("hist-chart", "figure"), 
    [Input("modelfilter", "value"), 
     Input("sellertype", "value")])

def carModeDetail(modelfilter, sellertype):
    carSelected = carSelect(modelfilter,sellertype)
    carSelected = carSelected.sort_values(by=['Mileage_km'], ascending=False)
    fig3 = px.bar(carSelected[:10], x='Mileage_km', y='Price_rs', color='Condition', title="Top 10 Cars with Price Sorted by Best Mileage Filter out using Seller Type and Brand Model.")
    fig3.update_yaxes(visible =False, showticklabels=False)
    fig3.update_xaxes(visible =False, showticklabels=False)
    return fig3

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('modelfilter', 'value')])
def update_output(value):
    return 'Your Select Brand Model - "{}"'.format(value)


@app.callback(
    dash.dependencies.Output('dd-output-container_cond', 'children'),
    [dash.dependencies.Input('condfilter', 'value')])
def update_output_cond(value):
    return 'Your Select Brand Model - "{}"'.format(value)

tran = data[['Brand_Model','Condition','Transmission','Body','Mileage_km','Price_rs']]

@app.callback(
    Output("tranchart", "figure"), 
    [Input("transmissionfilter2", "value"), 
     Input("bodyfilter", "value")])

def TranModel(trantype, bodytype):
    data_new = tran[(tran['Transmission'] == trantype) & (tran['Body'] == bodytype)]
    data_new = data_new.sort_values(by='Price_rs',ascending=False)
    print(data_new[:10])
    tranfig = px.bar(data_new[:10], x='Brand_Model', y='Price_rs', color='Condition', title="Top Transmission Based Cars wuth Condition and Body Based along with Price!")
    tranfig.update_yaxes(visible =False, showticklabels=False)
    tranfig.update_xaxes(visible =False, showticklabels=False)
    return tranfig


if __name__ == "__main__":
    app.run_server(debug=False)
