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
data = pd.DataFrame()

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
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

checklist = html.Div([
    html.Div('Dash To-Do list'),
    dcc.Input(id="new-item"),
    html.Button("Add", id="add"),
    html.Button("Clear Done", id="clear-done"),
    html.Div(id="list-container"),
    html.Div(id="totals")
])

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                html.H4("Enter Playlist IDs",className='display-9'),
                html.Hr(),
                dbc.Input(id = 'pl_id_1',placeholder='Enter Playlist ID', type = 'text'),
                dbc.Input(id = 'pl_id_2',placeholder='Enter Playlist ID', type = 'text'),
                dbc.Input(id='pl_id_3', placeholder='Enter Playlist ID', type='text'),
                dbc.Button("Submit",id = 'submit',block = True)
            ]
        ),
        # checklist,
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

content = html.Div([dcc.Graph(id="playlist_graph")], style = CONTENT_STYLE)
#content = html.Div(id = 'page-content', style = CONTENT_STYLE)

app.layout = html.Div([sidebar,content])


@app.callback(
    Output("playlist_graph", "figure"), [Input("pl_id_1", "value"),Input("pl_id_2", "value"),Input("pl_id_3", "value"),Input("submit", "n_clicks")]
)
def make_graph(pl_id1, pl_id2, pl_id3, submit):
    global data
    global current_ids
    print(pl_id1,pl_id2,pl_id3)
    valid_data = [x for x in [pl_id1,pl_id2,pl_id3] if (x is not None and x != '')]
    print("Valid data"+ str(valid_data))
    if current_ids != valid_data and len(valid_data) > 0:
        current_ids = valid_data
        data = PlaylistRetriever.get_user_playlists(current_ids)
    elif data.empty:
        data = PlaylistRetriever.get_user_playlists(current_ids)
    print("got here")
    return Visualization.make_radar_chart(data)

style_todo = {"display": "inline", "margin": "10px"}
style_done = {"textDecoration": "line-through", "color": "#888"}
style_done.update(style_todo)


@app.callback(
    [
        Output("list-container", "children"),
        Output("new-item", "value")
    ],
    [
        Input("add", "n_clicks"),
        Input("new-item", "n_submit"),
        Input("clear-done", "n_clicks")
    ],
    [
        State("new-item", "value"),
        State({"index": ALL}, "children"),
        State({"index": ALL, "type": "done"}, "value")
    ]
)
def edit_list(add, add2, clear, new_item, items, items_done):
    triggered = [t["prop_id"] for t in dash.callback_context.triggered]
    adding = len([1 for i in triggered if i in ("add.n_clicks", "new-item.n_submit")])
    clearing = len([1 for i in triggered if i == "clear-done.n_clicks"])
    new_spec = [
        (text, done) for text, done in zip(items, items_done)
        if not (clearing and done)
    ]
    if adding:
        new_spec.append((new_item, []))
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
    return [new_list, "" if adding else new_item]


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

