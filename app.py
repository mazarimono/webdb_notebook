import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import plotly.express as px

from dash.dependencies import Input, Output, State, MATCH


df = pd.read_csv("data/kakei_data.csv", index_col=0, parse_dates=["date"])
df.iloc[:, :-1] = df.iloc[:, :-1].astype("float")
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.Button(id="my_button", children="PUSH ME"),
        html.Div(id="my_div", children=[]),
    ]
)


@app.callback(
    Output("my_div", "children"),
    [Input("my_button", "n_clicks")],
    [State("my_div", "children")],
    prevent_initial_call=True,
)
def add_components(n_clicks, children):
    new_components = html.Div(
        [
            dcc.Dropdown(
                id={"type": "graph_dropdown", "index": n_clicks},
                options=[{"label": c, "value": c} for c in list(df.columns[:-1])],
                value=[df.columns[:-1][n_clicks]],
                multi=True,
            ),
            dcc.Graph(id={"type": "my_graph", "index": n_clicks}),
        ]
    )
    children.append(new_components)
    return children


@app.callback(
    Output({"type": "my_graph", "index": MATCH}, "figure"),
    [Input({"type": "graph_dropdown", "index": MATCH}, "value")],
)
def update_graph(selected_value):
    return px.line(df, x="date", y=selected_value)


app.run_server(debug=True)
