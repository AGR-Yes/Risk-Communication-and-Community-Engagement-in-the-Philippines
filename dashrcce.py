import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.tools
from shapely.geometry import Point
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
import io
import base64


#Key value pairs for external style sheets from Bootstrap always goes before declaration of app dash
external_stylesheets = [
    {
        'href': 'file.css', 
        'rel':'stylesheet',
        'integrity':'sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor',
        'crossorigin':'anonymous'
     }
]

#app = Dash(__name__, external_stylesheets=external_stylesheets)


owid = pd.read_excel(r'owid-philippines (filtered).xlsx', 'Sheet1')
owid_summary = pd.read_excel(r'owid-philippines (filtered).xlsx', 'summary')
rcce =pd.read_excel(r'RCCE MAIN.xlsx', 'RCCE')
ph = gpd.read_file('gadm40_PHL_shp/gadm40_PHL_1.shp')

rcce_location = rcce[['REGION', 'STATUS', 'LANG_GRP', 'COMM_GRP', 'INFO_GAP', 'Longitude', 'Latitude']]
gdf = gpd.GeoDataFrame(rcce_location, geometry=gpd.points_from_xy(rcce_location.Longitude, rcce_location.Latitude))
newgeo =gdf.dropna().reset_index(drop=True)

rcce_edit =pd.read_excel(r'RCCE_MAIN_GEO_edit.xlsx', 'RCCE')

app = Dash(__name__, external_stylesheets=[dbc.themes.UNITED], suppress_callback_exceptions=True)

#Status (ongoing, planned etc)
status = []
status_list = rcce['STATUS'].unique()

#Nationwide Status
nationwide = rcce[rcce['REGION'] == 'NATIONWIDE']
nationwide.drop(['PROVINCE', 'CITY/MUNICIPALITY', 'Latitude', 'Longitude', 'ACTIVITY', 'START','FINISH'], axis=1, inplace=True)
nn_status = pd.DataFrame(nationwide['STATUS'].value_counts())
status_labels = list(set(nationwide['STATUS']))
status_values = nn_status['STATUS'].tolist()

#Language 

#language = []
language_list = rcce['LANG_GRP'].unique()

language = pd.DataFrame(rcce['LANGUAGE'].value_counts())
language_labels = list(set(rcce['LANGUAGE']))
language_values = language['LANGUAGE'].tolist()
lang_grp_df = rcce['LANG_GRP'].value_counts()
other_lang = rcce[(rcce['LANGUAGE'] != "Filipino") & (rcce['LANGUAGE'] != "English")]
top_12lang = other_lang['LANGUAGE'].value_counts()[:12]

#Comm channels)
cchannels = []
cchannels_list = rcce['COMM_GRP'].unique()

#Nationwide Communication Channels
nn_commgrp = pd.DataFrame(nationwide['COMM_GRP'].value_counts())
commgrp_labels = list(set(nationwide['COMM_GRP']))
commgrp_values = nn_commgrp['COMM_GRP'].tolist()

#Information (Info gap)
infog = []
infog_list = rcce['INFO_GAP'].unique()

#Nationwide Information Gaps
nn_infogrp = pd.DataFrame(nationwide['INFO_GAP'].value_counts())
infogrp_labels = list(set(nationwide['INFO_GAP']))
infogrp_values = nn_infogrp['INFO_GAP'].tolist()

quarter = owid_summary['QUARTER']

#2020
tcase2020 = owid_summary['T_CASES_2020']
tdeath2020 = owid_summary['T_DEATHS_2020']

#2021
tcase2021 = owid_summary['T_CASES_2021']
tdeath2021 = owid_summary['T_DEATHS_2021']

# ------------------------------------------------------------------------------



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
    'background-color':'#faeeeb',
}

sidebar = html.Div(
    [
        html.H2("RCCE and Communication in the Philippines", className="heading-3", 
                 style={
                        'color': '#f69941',
                        'font-family': 'montserrat'
                          }),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Status", href="/page-1", active="exact"),
                dbc.NavLink("Language", href="/page-2", active="exact"),
                dbc.NavLink("Communication Channels", href="/page-3", active="exact"),
                dbc.NavLink("Information Gaps", href="/page-4", active="exact"),
                dbc.NavLink("Cases", href="/page-5", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        html.H6("Instructions", 
                style={
                  'color': '#f69941'},),
        html.P(
            "Click from the menu above. Select from the dropdown menu to show the density of each value on the map. ", #className="lead"
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

# ------------------------------------------------------------------------------
px.set_mapbox_access_token(open(".mapbox_token").read())

# App layout

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
                html.H1('What is RCCE?',
                        style={
                          'textAlign':'center',
                          'color': '#f69941',
                          'font-family': 'montserrat'
                          }),
                  html.Div(className='col-12', children=[                 
                  html.H6('Risk Communication and Community Engagement (RCCE) involves engaging and informing the public about risks in their community. This dashboard focuses on the COVID-19 response, method of communication, and issues faced from January 2020 - June 2021.'),
                  html.Hr(),
                  html.H6('To begin, start by selecting an item on the sidebar!')
                  ]),
                ]

    elif pathname == "/page-1":
        return [
                html.H1('Status of Projects',
                        style={
                          'textAlign':'center',
                          'color': '#f69941',
                          'font-family': 'montserrat'
                          }),
                  html.Div(className='col-12', children=[
                  dcc.Dropdown(id='status-dropdown', options=status_list),
                  dcc.Graph(id='status-map'),
                  html.P('From January 2020 to June 2021, you can see and zoom in on certain parts of the Philippines that have planned and completed their RCCE projects. As for the ongoing projects, those were only during the period of the data set. '),
                  dcc.Graph(id='status-donut', 
                  figure=go.Figure(data=[go.Pie(labels = status_labels,values = status_values, hole = .3, 
                                  marker_colors=['rgb(255,191,0)', 
                                                 'rgb(251,206,177)', 
                                                 'rgb(255,127,80)'])],),),
                  html.P('You can see which regions have different statuses regarding their project. However, there are a lot of Nationwide projects. These are visible in the donut chart above. '),
                  ]),
                ]

    elif pathname == "/page-2":
        return [
                html.H1('Language Used',
                        style={
                          'textAlign':'center',
                          'color': '#f69941',
                          'font-family': 'montserrat'
                          }),
                html.Div(className='col-12', children=[
                  dcc.Dropdown(id='language-dropdown', options=language_list),
                  dcc.Graph(id='language-map'),
                  html.P('In these charts, you can see the different languages for the RCCE projects. Apart from English and Filipino, it also shows the top languages used to relay information across the country. '),
                  dcc.Graph(id='language-general', 
                  figure = go.Figure(data=[go.Pie(title="Language Group",labels=lang_grp_df.index, values=lang_grp_df.values, hole=.3, 
                                  marker_colors=['rgb(255,191,0)', 
                                                 'rgb(251,206,177)', 
                                                 'rgb(255,127,80)'])],),),
                  dcc.Graph(id='language-other', 
                  figure = go.Figure(data=[go.Pie(title="Language Group",labels=top_12lang.index, values=top_12lang.values, 
                                       hole=.3,
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
                                                 'rgb(244, 187, 68)'])],),),
                ])
              ]
    elif pathname == "/page-3":
        return [
                html.H1('Communication Channels',
                        style={
                          'textAlign':'center',
                          'color': '#f69941',
                          'font-family': 'montserrat'
                          }),
               html.Div(className='col-12', children=[
                  dcc.Dropdown(id='communication-dropdown', options=cchannels_list),
                  dcc.Graph(id='communication-map'),
                  html.P('The map shows the communication channels utilized to relay information and where it is most used. The chart below shows a data breakdown to further dissect the data on the map.'),
                  dcc.Graph(id='comchannel-sunburst',
                  figure = px.sunburst(nationwide, path=['COMM_GRP', 'COMMUNICATION_CHANNEL'],color_discrete_sequence=px.colors.qualitative.Pastel )),
                  html.P('You can click certain parts of the chart above to see how much each category fills each group.'),
                ]),
                ]
    elif pathname == "/page-4":
        return [
                html.H1('Information Gaps',
                        style={
                          'textAlign':'center',
                          'color': '#f69941',
                          'font-family': 'montserrat'
                          }),
               html.Div(className='col-12', children=[
                  dcc.Dropdown(id='information-dropdown', options=infog_list),
                  dcc.Graph(id='info-map'),
                  html.P('Though communication may be efficient in our time, there is no perfect communication channel that everyone can use. In this section, you can see the information gaps or issues faced during the period per region.'),
                  dcc.Graph(id='info-donut',
                  figure = go.Figure(data=[go.Pie(labels = infogrp_labels, 
                                  values = infogrp_values, hole = .3,
                                   marker_colors=['rgb(255,191,0)', 
                                                 'rgb(251,206,177)', 
                                                 'rgb(255,127,80)',
                                                 'rgb(250, 213, 165)',
                                                 'rgb(255, 245, 238)',])],),),
                  html.P('In the donut chart above, you can see the information gaps nationwide and per region.'),
                ]),
                ]

    elif pathname == "/page-5":
       return [
               html.H1('Cases',
                       style={
                         'textAlign':'center',
                         'color': '#f69941',
                         'font-family': 'montserrat'
                         }),
               dcc.Graph(id='linegraph',
                    figure=px.line(owid,x = quarter, 
                         y = [tcase2020, tcase2021, tdeath2020, tdeath2021],
                              title = "Total Cases and Deaths During the RCCE Period",
                              labels={
                                 "value":"Population",
                                     "x":"Quarter",
                              "variable":"Total"},
                              markers=True,
                         ),       
                ),
                html.P('The chart presents COVID-19 cases and deaths in the Philippines during the RCCE period.'),
                ]
   
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )



@app.callback(
    #id, property
    Output('status-map', 'figure'),
    Input('status-dropdown','value')
)
def status_map(selected_status):
    if selected_status is None:
        # display unfiltered map
        status_df = newgeo

    else:
        # filter data frame
        status_df = newgeo.loc[(rcce['STATUS'] == selected_status)]

        # ax = ph.plot(figsize=(6, 10), color='white', edgecolor='k')
        # status_fig = filtered_status.plot(ax=ax, color='dodgerblue', alpha=0.3)
        # buf = io.BytesIO() # in-memory files
        # plt.savefig(buf, format = "png") # save to the above file object
        # plt.close()
        # status_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        # #status_fig = plotly.tools.mpl_to_plotly(fig)
    
    fig_status = px.scatter_mapbox(status_df,
                        lat=status_df.geometry.y,
                        lon=status_df.geometry.x,
                        hover_name="REGION",
                        center={'lon':122.818, 'lat':12.096 },
                        zoom=4,
                        height=500,
                        mapbox_style='light', 
                        color_discrete_sequence=["#f69941"],)

    return fig_status
    #return "data:image/png;base64,{}".format(status_data)


@app.callback(
    #id, property
    Output('language-map', 'figure'),
    Input('language-dropdown','value')
)
def language_map(selected_language):
    if selected_language is None:
        language_df = newgeo
        # display unfiltered map
        # ax = ph.plot(figsize=(6, 10), color='white', edgecolor='k')
        # lang_fig = gdf.plot(ax=ax, color='dodgerblue', alpha=0.3)
        # buf = io.BytesIO() # in-memory files
        # plt.savefig(buf, format = "png") # save to the above file object
        # plt.close()
        # lang_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        #lang_fig = plotly.tools.mpl_to_plotly(fig)

    else:
        # filter data frame
        language_df = newgeo.loc[(rcce['LANG_GRP'] == selected_language)]

        # ax = ph.plot(figsize=(6, 10), color='white', edgecolor='k')
        # lang_fig = filtered_language.plot(ax=ax, color='dodgerblue', alpha=0.3)
        # buf = io.BytesIO() # in-memory files
        # plt.savefig(buf, format = "png") # save to the above file object
        # plt.close()
        # lang_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        #lang_fig = plotly.tools.mpl_to_plotly(fig)

    fig_language = px.scatter_mapbox(language_df,
                        lat=language_df.geometry.y,
                        lon=language_df.geometry.x,
                        hover_name="REGION",
                        center={'lon':122.818, 'lat':12.096 },
                        zoom=4,
                        height=500,
                        mapbox_style='light', 
                        color_discrete_sequence=["#f69941"],)
                        
    return fig_language
    #return "data:image/png;base64,{}".format(lang_data)


@app.callback(
    #id, property
    Output('communication-map', 'figure'),
    Input('communication-dropdown','value')
)
def communication_map(selected_communication):
    if selected_communication is None:
        communication_df = newgeo
        # display unfiltered map
        # ax = ph.plot(figsize=(6, 10), color='white', edgecolor='k')
        # com_fig = gdf.plot(ax=ax, color='dodgerblue', alpha=0.3)
        # buf = io.BytesIO() # in-memory files
        # plt.savefig(buf, format = "png") # save to the above file object
        # plt.close()
        # com_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        #com_fig = plotly.tools.mpl_to_plotly(fig)

    else:
        # filter data frame
        communication_df = newgeo.loc[(rcce['COMM_GRP'] == selected_communication)]

        # ax = ph.plot(figsize=(6, 10), color='white', edgecolor='k')
        # com_fig = filtered_communication.plot(ax=ax, color='dodgerblue', alpha=0.3)
        # buf = io.BytesIO() # in-memory files
        # plt.savefig(buf, format = "png") # save to the above file object
        # plt.close()
        # com_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        #com_fig = plotly.tools.mpl_to_plotly(fig)

    fig_communication = px.scatter_mapbox(communication_df,
                        lat=communication_df.geometry.y,
                        lon=communication_df.geometry.x,
                        hover_name="REGION",
                        center={'lon':122.818, 'lat':12.096 },
                        zoom=4,
                        height=500,
                        mapbox_style='light', 
                        color_discrete_sequence=["#f69941"],)

    return fig_communication

    #return "data:image/png;base64,{}".format(com_data)


@app.callback(
    #id, property
    Output('info-map', 'figure'),
    Input('information-dropdown','value')
)
def info_map(selected_information):
    if selected_information is None:
        info_df = newgeo
        # display unfiltered map
        # ax = ph.plot(figsize=(6, 10), color='white', edgecolor='k')
        # info_fig = gdf.plot(ax=ax, color='dodgerblue', alpha=0.3)
        # buf = io.BytesIO() # in-memory files
        # plt.savefig(buf, format = "png") # save to the above file object
        # plt.close()
        # info_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        #info_fig = plotly.tools.mpl_to_plotly(fig)

    else:
        # filter data frame
        info_df = newgeo.loc[(rcce['INFO_GAP'] == selected_information)]

        # ax = ph.plot(figsize=(6, 10), color='white', edgecolor='k')
        # info_fig = filtered_information.plot(ax=ax, color='dodgerblue', alpha=0.3)
        # buf = io.BytesIO() # in-memory files
        # plt.savefig(buf, format = "png") # save to the above file object
        # plt.close()
        # info_data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
        #info_fig = plotly.tools.mpl_to_plotly(fig)

    fig_info = px.scatter_mapbox(info_df,
                        lat=info_df.geometry.y,
                        lon=info_df.geometry.x,
                        hover_name="REGION",
                        center={'lon':122.818, 'lat':12.096 },
                        zoom=4,
                        height=500,
                        mapbox_style='light', 
                        color_discrete_sequence=["#f69941"],)

    return fig_info

    #return "data:image/png;base64,{}".format(info_data)




if __name__=='__main__':
    app.run_server(debug=True, port=3000)



    

