import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.tools
from shapely.geometry import Point
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc


#Key value pairs for external style sheets from Bootstrap always goes before declaration of app dash
external_stylesheets = [
    {
        'href': 'file.css', 
        'rel':'stylesheet',
        'integrity':'sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor',
        'crossorigin':'anonymous'
     }
]

# ------------------------------------------------------------------------------
owid = pd.read_excel(r'owid-philippines (filtered).xlsx', 'summary')
rcce = pd.read_excel(r'RCCE_MAIN_GEO_edit.xlsx', 'RCCE')
perRegion = pd.read_excel(r'region-province.xlsx', 'Region')
rcce_location = rcce[['REGION',"PROVINCE",'CITY/MUNICIPALITY', 'STATUS', 'LANGUAGE', 'LANG_GRP', 'COMM_GRP', 'COMMUNICATION_CHANNEL', 'INFO_GAP', 'Longitude', 'Latitude']]

gdf = gpd.GeoDataFrame(rcce_location, geometry=gpd.points_from_xy(rcce_location.Longitude, rcce_location.Latitude))
newgeo = gdf.dropna().reset_index(drop=True)
px.set_mapbox_access_token(open(".mapbox_token").read())

#NATIONWIDE
# ------------------------------------------------------------------------------
nationwide = rcce[rcce['REGION'] == 'NATIONWIDE']
nationwide.drop(['PROVINCE', 'CITY/MUNICIPALITY', 'Latitude', 'Longitude', 'ACTIVITY', 'START','FINISH'], axis=1, inplace=True)


#NATIONWIDE STATUS
# ------------------------------------------------------------------------------
nn_status = nationwide['STATUS'].value_counts()
nationwide_status_pie = go.Figure(data=[go.Pie(labels = nn_status.index, values = nn_status.values, hole = .3,
                                               marker_colors=['rgb(255,191,0)', 
                                                 'rgb(251,206,177)', 
                                                 'rgb(255,127,80)'])])
nationwide_status_pie.update_layout(title_text='Nationwide Status')


#NATIONWIDE LANGUAGE
# ------------------------------------------------------------------------------
lang_grp_df = nationwide['LANG_GRP'].value_counts()

lang_tmp = nationwide[nationwide['LANG_GRP'] == "Others"]
other_lang = lang_tmp['LANGUAGE'].value_counts()

nationwide_lang_grp_pie = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])
nationwide_lang_grp_pie.add_trace(go.Pie(title="Language Group", labels=lang_grp_df.index, values=lang_grp_df.values, hole=.3,
                                         marker_colors=['rgb(255,191,0)', 
                                                 'rgb(251,206,177)', 
                                                 'rgb(255,127,80)']),row=1,col=1)
nationwide_lang_grp_pie.add_trace(go.Pie(title="Others", labels=other_lang.index, values=other_lang.values, hole=.3,
                                         marker_colors=['rgb(255,191,0)', 
                                                 'rgb(251,206,177)', 
                                                 'rgb(255,127,80)',
                                                 'rgb(250, 213, 165)',
                                                 'rgb(255, 245, 238)',
                                                 'rgb(192, 64, 0)',
                                                 'rgb(160, 82, 45))',
                                                 'rgb(227, 115, 94)',
                                                 'rgb(255, 229, 180)',
                                                 'rgb(255, 172, 28)',
                                                 'rgb(218, 160, 109)',
                                                 'rgb(139, 64, 0)',
                                                 'rgb(244, 187, 68)']),row=1,col=2)
nationwide_lang_grp_pie.update_traces(textposition='inside')
nationwide_lang_grp_pie.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', title_text="Nationwide Language Groups")


#NATIONWIDE COMMUNICATION CHANNELS
# ------------------------------------------------------------------------------
nationwide_comm_pie = px.sunburst(nationwide, path=['COMM_GRP', 'COMMUNICATION_CHANNEL'],color_discrete_sequence=px.colors.qualitative.Pastel)
nationwide_comm_pie.update_layout(title_text='Nationwide Communication Channels')


#NATIONWIDE INFORMATION GAP
# ------------------------------------------------------------------------------
nn_infogrp = nationwide['INFO_GAP'].value_counts()
nationwide_info_gap_pie = go.Figure(data=[go.Pie(labels = nn_infogrp.index, values = nn_infogrp.values, hole = .3,
                                                 marker_colors=['rgb(255,191,0)', 
                                                 'rgb(251,206,177)', 
                                                 'rgb(255,127,80)',
                                                 'rgb(250, 213, 165)',
                                                 'rgb(255, 245, 238)'])])
nationwide_info_gap_pie.update_layout(title_text='Nationwide Information Gap')
 

#OWID SUMMARY
# ------------------------------------------------------------------------------
quarter = owid['QUARTER']

#2020
tcase2020 = owid['T_CASES_2020']
tdeath2020 = owid['T_DEATHS_2020']

#2021
tcase2021 = owid['T_CASES_2021']
tdeath2021 = owid['T_DEATHS_2021']

total_cases_and_deaths = px.line(owid,
              x = quarter, 
              y = [tcase2020, tcase2021, tdeath2020, tdeath2021],
              title = "Total Cases and Deaths During the RCCE Period",
              labels={
                  "value":"Population",
                  "QY":"Quarter",
                  "variable":"Total"},
              markers=True
              )


# ------------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.UNITED], suppress_callback_exceptions=True)

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#fdf9de",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    'backgroundColor':'#faeeeb',
}


# ------------------------------------------------------------------------------
sidebar = html.Div(
    [
        html.H2(
            "RCCE and Communication in the Philippines",
            className="heading-3", 
            style={
                'color': '#f69941',
                'font-family': 'montserrat'
                }
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Status", href="/", active="exact"),
                dbc.NavLink("Language", href="/page-1", active="exact"),
                dbc.NavLink("Communication Channels", href="/page-2", active="exact"),
                dbc.NavLink("Information Gaps", href="/page-3", active="exact"),
                dbc.NavLink("Cases", href="/page-4", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        html.H6("Instructions",style={'color': '#f69941'}),
        html.P("Click from the menu above. Select from the dropdown menu to show the density of each value on the map.", className="lead"),
    ],
    style=SIDEBAR_STYLE
)


# ------------------------------------------------------------------------------
modal = html.Div(
    [
        dbc.Button("WHAT IS RCCE?", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("WHAT IS RCCE?")),
                dbc.ModalBody('Risk Communication and Community Engagement (RCCE) involves engaging and informing the public about risks in their community. This dashboard focuses on COVID-19 response and lists activities from January 2020 - June 2021.'),
                dbc.ModalBody('To begin, start by selecting an item on the sidebar!'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ],
    style = {
        'position':'fixed',
        'top':'2vh',
        'right':'2vw'
        }
)


# ------------------------------------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        sidebar,
        html.Div(
            id='main-page',
            style=CONTENT_STYLE
        ),
        modal
    ]
)


# ------------------------------------------------------------------------------
#Status (ongoing, planned etc)
status = []
status_list = rcce['STATUS'].unique()

#Language 
language = []
language_list = rcce['LANG_GRP'].unique()

#Comm channels)
cchannels = []
cchannels_list = rcce['COMM_GRP'].unique()

#Information (Info gap)
infog = []
infog_list = rcce['INFO_GAP'].unique()


# ------------------------------------------------------------------------------
@app.callback(
    Output("map-plot", "figure"),
    Output("data-plot", "figure"),
    Input("url", "pathname"),
    Input("data-dropdown", "value"),
    Input("region-dropdown", "value")
)
def render_page_content(pathname,value,region):
    
    if region==None:
        map_center = {'lon':122.818, 'lat':12.096}
        z = 4
        map_plot_data = newgeo

        if pathname == "/":
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['STATUS'] == value)]
            plot_graph = nationwide_status_pie
        elif pathname == "/page-1":
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['LANG_GRP'] == value)]
            plot_graph = nationwide_lang_grp_pie
        elif pathname == "/page-2":
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['COMM_GRP'] == value)]
            plot_graph = nationwide_comm_pie
        elif pathname == "/page-3":
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['INFO_GAP'] == value)]
            plot_graph = nationwide_info_gap_pie
    else:
        map_center = {
            'lon':perRegion[perRegion['Region']==region].Longitude.values[0],
            'lat':perRegion[perRegion['Region']==region].Latitude.values[0]
            }
        z = 5            
        
        map_plot_data = newgeo.loc[(newgeo['REGION'] == region)]

        if pathname == "/":
            tmp = map_plot_data['STATUS'].value_counts()
            plot_graph = go.Figure(data=[go.Pie(labels = tmp.index, values = tmp.values, hole = .3)])
            plot_graph.update_layout(title_text=(region + ' Status'))
            
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['STATUS'] == value)]            
            
        elif pathname == "/page-1":
            lang_grp_df = map_plot_data['LANG_GRP'].value_counts()

            lang_tmp = map_plot_data[map_plot_data['LANG_GRP'] == "Others"]
            other_lang = lang_tmp['LANGUAGE'].value_counts()

            plot_graph = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])
            plot_graph.add_trace(go.Pie(title="Language Group", labels=lang_grp_df.index, values=lang_grp_df.values, hole=.3), row=1,col=1)
            plot_graph.add_trace(go.Pie(title="Others", labels=other_lang.index, values=other_lang.values, hole=.3),row=1,col=2)
            plot_graph.update_traces(textposition='inside')
            plot_graph.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', title_text=(region + ' Language Groups'))
                        
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['LANG_GRP'] == value)]
            
        elif pathname == "/page-2":
            tmp = map_plot_data['COMM_GRP'].value_counts()
            plot_graph = px.sunburst(map_plot_data, path=['COMM_GRP', 'COMMUNICATION_CHANNEL'])
            plot_graph.update_layout(title_text=(region + ' Communication Channels'))
            
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['COMM_GRP'] == value)]
        
        elif pathname == "/page-3":
            tmp = map_plot_data['INFO_GAP'].value_counts()
            plot_graph = go.Figure(data=[go.Pie(labels = tmp.index, values = tmp.values, hole = .3)])
            plot_graph.update_layout(title_text=(region + ' Information Gaps'))
            
            if value!=None: map_plot_data = map_plot_data.loc[(map_plot_data['INFO_GAP'] == value)]

    if pathname == "/page-4":
        plot_graph = None

    if pathname == "/":
        color = 'STATUS'
    elif pathname == "/page-1":
        color = 'LANG_GRP'
    elif pathname == "/page-2":
        color = 'COMM_GRP'
    elif pathname == "/page-3":
        color = 'INFO_GAP'
    
    
    map_plot_data['x'] = map_plot_data.geometry.x
    map_plot_data['y'] = map_plot_data.geometry.y
    map_plot_data['nameLabel'] =  map_plot_data['CITY/MUNICIPALITY'] + ', ' + map_plot_data['PROVINCE'] + ', ' + map_plot_data['REGION']
    
    fig_map = px.scatter_mapbox(
        map_plot_data,
        lat=map_plot_data['y'],
        lon=map_plot_data['x'],
        hover_name="nameLabel",
        hover_data={
            'STATUS':True,
            'LANG_GRP':True,
            'COMM_GRP':True,
            'INFO_GAP':True,
            'x':False,
            'y':False
        },
        center=map_center,
        zoom=z,
        height=500,
        mapbox_style='light', 
        color_discrete_sequence=["#f69941"]
        )

    fig_map.layout.update(showlegend=False)
    
    return fig_map, plot_graph

@app.callback(
    Output("main-page", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/page-4":
        return [
            html.H1(
                'Cases',
                style={
                    'textAlign':'center',
                    'color': '#f69941',
                    'font-family': 'montserrat'
                }
            ),
            dcc.Graph(figure=total_cases_and_deaths),
            html.Br(),
            html.P("The chart presents COVID-19 cases and deaths in the Philippines during the RCCE period.")
        ]
    else:
        if pathname == "/":
            title = "Status of Projects"
            text1 = "From January 2020 to June 2021, you can see and zoom in on certain parts of the Philippines that have planned and completed their RCCE projects. As for the ongoing projects, those were only during the period of the data set."
            text2 = "You can see which regions have different statuses regarding their project. However, there are a lot of Nationwide projects. These are visible in the donut chart below."
            options_page = status_list           
        elif pathname == "/page-1":
            title = "Language Used"
            text1 = 'In these charts, you can see the different languages for the RCCE projects. Apart from English and Filipino, it also shows the top languages used to relay information across the country.'
            text2 = ''
            options_page = language_list
        elif pathname == "/page-2":
            title = "Communication Channels"
            text1 = 'The map shows the communication channels utilized to relay information and where it is most used. The chart below shows a data breakdown to further dissect the data on the map.'
            text2 = 'You can click certain parts of the chart below to see how much each category fills each group.'
            options_page = cchannels_list
        elif pathname == "/page-3":
            title = "Information Gaps"
            text1 = 'Though communication may be efficient in our time, there is no perfect communication channel that everyone can use. In this section, you can see the information gaps or issues faced during the period per region.'
            text2 = 'In the donut chart below, you can see the information gaps nationwide and per region.'
            options_page = infog_list
            
        return [
            html.H1(
                title,
                style={
                    'textAlign':'center',
                    'color': '#f69941',
                    'font-family': 'montserrat'
                }
            ),
            dcc.Dropdown(id='data-dropdown', options=options_page),
            dcc.Graph(id='map-plot'),
            dcc.Dropdown(id='region-dropdown', options=perRegion['Region'], placeholder="Select Region...", style=dict(width='50%')),
            html.Br(),
            html.P(text1),
            html.P(text2),
            dcc.Graph(id='data-plot')
        ]


# ------------------------------------------------------------------------------
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


if __name__=='__main__':
    app.run_server(debug=True)



    

