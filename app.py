import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from dash.dependencies import Input, Output, State, MATCH, ALL
import PlaylistRetriever
import Visualization

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
current_ids = ['spotify:playlist:28mI8s2FBTx0pzWfQ7dTwA','7s5PGUSUudnrdcueQuxWW0','spotify:playlist:6SeTiLgmsdVbQ4MjOnIJb6']
#data = pd.DataFrame()

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "padding-left": "18rem",
    #"margin-right": "2rem",
    #"padding": "2rem 1rem",
    #'background-color':'red'
}

checklist = html.Div([
    dbc.Input(id="new-item",placeholder='Enter Playlist ID', type = 'text'),
    html.Div([dbc.Button("Add", id="add",style = {'margin':'auto'}),
    dbc.Button("Remove", id="clear-done", style = {'margin':'auto'}) ],style = {'display':'flex','padding-top':'10px','padding-bottom':'5px'}),
    html.Div(id="list-container"),
    html.Div(id="totals")
])

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                html.H4("Enter Playlist IDs",className='display-9'),
                html.Hr(),
                checklist
            ]
        ),
        #checklist,
        html.Hr(),
        html.P(
            "To find a playlist ID, click on the three dots and select 'Copy Spotify URI'",
            className="text-muted",
        ),
    ],
    body=True)

sidebar = html.Div(
    [
        html.H2("Spotify Playlist Analyzer",className='display-9'),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

row2_form= dbc.FormGroup(
    [
        dbc.Label("Email", html_for="example-email-row", width=2),
        dbc.Col(
            dbc.Input(
                type="email", id="example-email-row", placeholder="Enter email"
            ),
            width=12,
        ),
    dbc.Label("Select Playlist Profiles to Include", html_for="example-email-row", width=12),
        dbc.Col(dcc.Checklist(id = 'pl_checklist',
    options=[
        {'label': 'New York City', 'value': 'NYC'},
        {'label': 'Montréal', 'value': 'MTL'},
        {'label': 'San Francisco', 'value': 'SF'}
    ],
    value=['NYC', 'MTL']
),width = 8)
    ],
    row=True,
)

row2 = dbc.Row([dbc.Col([html.H3("Generate a New Playlist"),row2_form],width = 3),dbc.Col([dcc.Graph(id = 'table')],width=9)])

content = html.Div([dbc.Row([dbc.Col(dcc.Graph(id="playlist_graph"),width = 6,style = {'background-color':'red'}),dbc.Col(dcc.Graph(id = "playlist_graph2"),width = 6)],style = {'background-color':'blue'}),row2], style = CONTENT_STYLE)
#content = html.Div(id = 'page-content', style = CONTENT_STYLE)

data = dcc.Store(id='playlist_data')
playlist_ids = dcc.Store(id='playlist_ids')
playlist_ids_mappings = dcc.Store(id='playlist_id_mappings')
checklist_contents = dcc.Store(id='checklist')
app.layout = html.Div([sidebar,content,data,playlist_ids,playlist_ids_mappings,checklist_contents])



def get_radar_graph(data):
    #global data
    # print("Valid data"+ str(valid_data))
    # print("Current ids" + str(current_ids))
    # if len(filter) > 0:
    #     data = PlaylistRetriever.get_user_playlists(filter)
    # else:
    #     data = PlaylistRetriever.get_user_playlists(current_ids)
    print("got here")

    fig = Visualization.make_radar_chart(data)
    fig.update_layout(
        margin=dict(l=100, r=0, t=0, b=0),
        paper_bgcolor="LightSteelBlue"
    )
    fig.update_layout(legend=dict(
        yanchor="top",
        #y=0.99,
        xanchor="left",
        #x=0.01
    ))
    return fig



style_todo = {"display": "inline", "margin": "10px"}
style_done = {"textDecoration": "line-through", "color": "#888"}
style_done.update(style_todo)

@app.callback(Output('playlist_data','data'),Input('checklist', 'data'),State('playlist_id_mappings','data'))
def get_data(id_tup,mapping):
    print(mapping)
    print("Inside get data")
    print(id_tup)
    #print(new_ids)
    #If the user has entered an id
    if len(id_tup[0]) != 0:
        #Our data is stored in the format [data_list, boolean], where the boolean is used by our checklist to manage data
        #Each item in data_list is stored as a tuple (id, boolean), where the boolean indicates whether to remove the item
        #We only need the id, which we extract using list comprehension
        ids = [x[0] for x in id_tup[0]]

        #If the mapping is not None, some of the inputted ids will be playlist names and not Spotify ids.
        #Thus, we must convert them back so that our API can retrieve the data.
        if mapping[0]:
            ids = [mapping[0][x] if x in mapping[0].keys() else x for x in ids]
        data = PlaylistRetriever.get_user_playlists(ids)
    #The list is empty; display the default data
    else:
        data = PlaylistRetriever.get_user_playlists(current_ids)
    #print(data)
    return data.reset_index().to_json()

@app.callback(
        Output('checklist','data'),
    [
        Input("add", "n_clicks"),
        Input("new-item", "n_submit"),
        Input("clear-done", "n_clicks"),
    ],
    [
        State("new-item", "value"),
        State({"index": ALL}, "children"),
        State({"index": ALL, "type": "done"}, "value")
    ]
)
def get_list_content(add, add2, clear, new_item, items, items_done):
    #This needs to add to id list (new_item)
    print(add, add2, clear)
    print(new_item, items, items_done)
    triggered = [t["prop_id"] for t in dash.callback_context.triggered]
    adding = len([1 for i in triggered if i in ("add.n_clicks", "new-item.n_submit")])
    clearing = len([1 for i in triggered if i == "clear-done.n_clicks"])
    new_spec = [
        (text, done) for text, done in zip(items, items_done)
        if not (clearing and done)
    ]
    # # If both clearing and done on this index, remove this id]
    # current_ids = [id for id, done in zip(ids, items_done) if not (clearing and done)]

    print(adding)
    if adding:
        new_spec.append((new_item, []))
        #current_ids.append(new_item)
    print("new spec:" + str(new_spec))
    #Tuple (names of playlists, new_item,playlist ID list)
    return new_spec, "" if adding else new_item

"""
Creates two mappings: playlist_id to playlist name and the reverse

Input: dataframe containing playlist data
Output: Tuple containing two dictionaries
"""
@app.callback(Output('playlist_id_mappings','data'),Input('playlist_data','data'),
              state = [State(component_id='playlist_data',component_property='data')])
def store_playlist_id_mapping(df, df2):
    print(df, df2)
    if df is None:
        return dict(), dict()
    df = pd.read_json(df)
    dictionary = (pd.Series(df['playlist_id'].values, index=df['playlist']).to_dict(), pd.Series(df['playlist'].values, index=df['playlist_id']).to_dict())
    return dictionary

@app.callback(Output('pl_checklist','options'),Input('playlist_id_mappings','data'))
def update_suggestion_checklist(dictionary):
    names = dictionary[0]
    to_return = []
    for key, value in names.items():
        to_return.append({'label':key,'value':value})
    return to_return



def create_playlist_id_mapping(dataframe):
    dictionary = {row['playlist_id']: row['playlist'] for index, row in dataframe.iterrows()}
    return dictionary


@app.callback(
    [
        Output("list-container", "children"),
        Output("new-item", "value"),
        Output("playlist_graph", "figure"),
        Output("playlist_graph2", "figure")
    ],
    [
        Input('playlist_data','data'),
        Input('checklist','data'),
        Input('playlist_id_mappings','data')
    ]
)
def edit_list(dataframe, playlist_ids,mapping):
    dataframe = pd.read_json(dataframe)
    print('playlist_ids'+str(playlist_ids))
    print("Pl_name_Dict" + str(mapping))
    adding  = playlist_ids[1]
    new_spec = playlist_ids[0]
    pl_name_dict = mapping[1]
    new_list = [
        html.Div([
            dcc.Checklist(
                id={"index": i, "type": "done"},
                options=[{"label": "", "value": "done"}],
                value=done,
                style={"display": "inline"},
                labelStyle={"display": "inline"}
            ),
            html.Div((lambda x: pl_name_dict[x] if x in pl_name_dict.keys() else x)(text), id={"index": i}, style=style_done if done else style_todo)
        ], style={"clear": "both"})
        for i, (text, done) in enumerate(new_spec)
    ]
    radar_graph = get_radar_graph(dataframe)
    bar_graph = Visualization.make_bar_graph(dataframe)
    y=  [new_list, adding, radar_graph, bar_graph]
    #print(y)
    return y


@app.callback(
    Output({"index": MATCH}, "style"),
    Input({"index": MATCH, "type": "done"}, "value")
)
def mark_done(done):
    return style_done if done else style_todo


@app.callback(
    Output("totals", "children"),
    Input({"index": ALL, "type": "done"}, "value")
)
def show_totals(done):
    count_all = len(done)
    count_done = len([d for d in done if d])
    result = "Remove {} of {} playlists".format(count_done, count_all)
    # if count_all:
    #     result += " - {}%".format(int(100 * count_done / count_all))
    return result

@app.callback(Output('table','figure'),Input('playlist_data','data'))
def suggest_playlist(dataframe):
    df = pd.read_json(dataframe)
    df.set_index("name",inplace=True)
    print("suggest playlist")
    print(df.columns)
    return go.Figure(data=[go.Table(
        header=dict(values=df.columns,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])


if __name__ == "__main__":
    app.run_server(debug=True)

