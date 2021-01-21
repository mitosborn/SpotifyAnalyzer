# # import os
# #
# # import dash
# # import dash_core_components as dcc
# # import dash_html_components as html
# # import PlaylistRetriever as pl
#
# # import dash
# # import dash_bootstrap_components as dbc

"""
Dash port of Shiny telephones by region example:
https://shiny.rstudio.com/gallery/telephones-by-region.html
"""
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
            width=10,
        ),
    ],
    row=True,
)

row2 = dbc.Row(dbc.Col([html.H3("Generate a New Playlist"),row2_form],width = 3))

content = html.Div([dbc.Row([dbc.Col(dcc.Graph(id="playlist_graph"),width = 6,style = {'background-color':'red'}),dbc.Col(dcc.Graph(id = "playlist_graph2"),width = 6)],style = {'background-color':'blue'}),row2], style = CONTENT_STYLE)
#content = html.Div(id = 'page-content', style = CONTENT_STYLE)

data = html.Div(id='intermediate-value', style={'display': 'none'})

app.layout = html.Div([sidebar,content,data])



def make_graph(items):
    #global data
    # print("Valid data"+ str(valid_data))
    # print("Current ids" + str(current_ids))
    filter = [x for x in items if (x is not None and x != "")]
    if len(filter) > 0:
        data = PlaylistRetriever.get_user_playlists(filter)
    else:
        data = PlaylistRetriever.get_user_playlists(current_ids)
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

@app.callback(Input("list-container", "children"),Output('intermediate-value','children')
)
def get_data(children):
    pass



@app.callback(
    [
        Output("list-container", "children"),
        Output("new-item", "value"),
        Output("playlist_graph", "figure"),
        Output("playlist_graph2","figure"),

    ],
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
def edit_list(add, add2, clear, new_item, items, items_done):
    print(add,add2,clear)
    print(new_item,items,items_done)
    triggered = [t["prop_id"] for t in dash.callback_context.triggered]
    adding = len([1 for i in triggered if i in ("add.n_clicks", "new-item.n_submit")])
    clearing = len([1 for i in triggered if i == "clear-done.n_clicks"])
    new_spec = [
        (text, done) for text, done in zip(items, items_done)
        if not (clearing and done)
    ]
    print(adding)
    if adding:
        new_spec.append((new_item, []))
    print("new spec:" + str(new_spec))
    new_list = [
        html.Div([
            dcc.Checklist(
                id={"index": i, "type": "done"},
                options=[{"label": "", "value": "done"}],
                value=done,
                style={"display": "inline"},
                labelStyle={"display": "inline"}
            ),
            html.Div(text, id={"index": i}, style=style_done if done else style_todo)
        ], style={"clear": "both"})
        for i, (text, done) in enumerate(new_spec)
    ]
    graph = make_graph([x[0] for x in new_spec])
    y=  [new_list, "" if adding else new_item,graph,graph,html.Div()]
    print(y)
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
    result = "{} of {} items completed".format(count_done, count_all)
    if count_all:
        result += " - {}%".format(int(100 * count_done / count_all))
    return result


if __name__ == "__main__":
    app.run_server(debug=True)

