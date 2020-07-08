# パッケージ呼び出し部分
import dash
import os 

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


px.set_mapbox_access_token(
    'your-token'
)

## 処理に用いる関数
### コールバックで追加する新たなレイアウトを作成する
### 引数は各コンポーネントのIDとボタンのクリック回数
def two_graphs(dropdown_id, graph1_id, graph2_id, button_id, click_count):
    prefs = df["居住都道府県"].unique()
    two_graphs_parts = html.Div(
        [
            dcc.Dropdown(
                id=dropdown_id,
                options=[{"label": i, "value": i} for i in prefs],
                value=[prefs[click_count]],
                multi=True,
            ),
            html.Div(
                [
                    dcc.Graph(id=graph1_id),
                ],
                style=half_div,
            ),
            html.Div(
                [
                    dcc.Graph(id=graph2_id),
                ],
                style=half_div,
            ),
            html.Button("各都道府県のデータを調べる", id=button_id, n_clicks=0),
        ]
    )
    return two_graphs_parts

## CSS
### カウンター用
box_style = {
    "width": "30%",
    "display": "inline-block",
    "verticalAlign": "top",
    "textAlign": "center",
    "backgroundColor": 'lime',
    'margin': '1%'
}
### グラフを2つ横に並べる
half_div = {"width": "48%", "margin": "1%", "display": "inline-block", "verticalAlign": "top"}

## データの読み込み

df = pd.read_csv("data/covid19_data.csv", index_col=0, parse_dates=["確定日"])
## 都道府県でグループバイしたものをカウントしたものと都道府県の座標を平均したものを
## 作成し、マージする。
df1 = df.groupby("居住都道府県", as_index=False)["count"].count()
df2 = df.groupby("居住都道府県", as_index=False)[["X", "Y"]].mean()
df3 = df1.merge(df2)

### データの作成

total_count = len(df)
new_date = df["確定日"].max()
new_total = len(df[df["確定日"] == new_date])

### 日本全体のダッシュボードのツリーマップで用いるデータの作成
df_age_sex = df.groupby(["年代", "性別"], as_index=False).sum()
df_age_sex["日本"] = "日本"

ex_sheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=ex_sheets)

# レイアウト部分

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("新型コロナ:日本の感染者数"),
                html.H3(f"更新日: {new_date.date()}"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "全国の総感染者数",
                                    style={"textAlign": "center", "padding": 0},
                                ),
                                html.H1(
                                    f"{total_count}人",
                                    style={"textAlign": "center", "padding": 0},
                                ),
                            ],
                            style=box_style,
                        ),
                        html.Div(
                            [
                                html.H3(
                                    "全国の新規感染者数",
                                    style={"textAlign": "center", "padding": 0},
                                ),
                                html.H1(
                                    f"{new_total}人",
                                    style={"textAlign": "center", "padding": 0},
                                ),
                            ],
                            style=box_style,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id="jp_radio",
                                    options=[
                                        {"label": i, "value": i} for i in ["累計", "日別"]
                                    ],
                                    value="累計",
                                ),
                                dcc.Graph(id="graph1"),
                            ],
                            style=half_div,
                        ),
                        html.Div([
                            dcc.Graph(figure=px.treemap(
                            df_age_sex, path=["日本", "年代", "性別"], values="count",
                        )),], style=half_div,),
                    ]
                ),
                html.Div(
                    [
                        # ここに地図を載せたいがどうしたらよいか考える
                        dcc.Graph(
                            figure=px.scatter_mapbox(
                                df3,
                                lat="Y",
                                lon="X",
                                size="count",
                                hover_name="居住都道府県",
                                color="count",
                                zoom=3,
                                center={"lat": 35.6706, "lon": 139.772},
                            )
                        )
                    ]
                ),
                html.Div(
                    [
                        html.Button(
                            "各都道府県のデータを調べる", id={"type": "add_data", "index": 0}
                        ),
                        html.Div(id="add_tools", children=[]),
                    ]
                ),
            ],
            style={"padding": "3%"},
        ),
    ],
    style={"padding": "3%"},
)


# コールバック１　
## 全国のダッシュボードの累計感染者数、新規感染者数のグラフの切り替え
@app.callback(Output("graph1", "figure"), [Input("jp_radio", "value")])
def update_graph1(selected_value):
    jp_df = df.groupby("確定日", as_index=False).sum()
    jp_df["確定日"] = pd.to_datetime(jp_df["確定日"])
    jp_df = jp_df.sort_values("確定日")
    jp_df["cumsum"] = jp_df["count"].cumsum()

    if selected_value == "日別":
        return px.bar(jp_df, x="確定日", y="count", title="新規感染者数")
    return px.area(jp_df, x="確定日", y="cumsum", title='累計感染者数')

# コールバック2
## ボタンをクリックすると新たなレイアウトが生成される
@app.callback(
    Output("add_tools", "children"),
    [Input({"type": "add_data", "index": ALL}, "n_clicks")],
    [State("add_tools", "children")],
    prevent_initial_call=True,
)
def add_tools(n_list, existing_children):
    n_clicks = sum(n_list)
    if n_clicks > 57:
        raise dash.exceptions.PreventUpdate
    add_div_tool = two_graphs(
        {"type": "drop_down", "index": n_clicks},
        {"type": "bar_graph", "index": n_clicks},
        {"type": "tree_map", "index": n_clicks},
        {"type": "add_data", "index": n_clicks},
        n_clicks,
    )
    existing_children.append(add_div_tool)
    return existing_children

## コールバック3
### 新たに追加されたレイアウトでの、ドロップダウンの選択をグラフに反映する
@app.callback(
    [
        Output({"type": "bar_graph", "index": MATCH}, "figure"),
        Output({"type": "tree_map", "index": MATCH}, "figure"),
    ],
    [
        Input({"type": "drop_down", "index": MATCH}, "value"),
    ],
)
def update_tools(dropdown_value):
    if dropdown_value:
        df_pref = df[df["居住都道府県"].isin(dropdown_value)]
        df_pref_date = df_pref.groupby(['確定日', '居住都道府県'], as_index=False).sum()
        df_pref_groupby_date_sex = df_pref.groupby(['居住都道府県', "年代", "性別"], as_index=False).sum()
        df_pref_groupby_date_sex['選択都道府県'] = '選択都道府県'
        return (
                px.bar(df_pref_date, x="確定日", y="count", color='居住都道府県'),
                px.treemap(df_pref_groupby_date_sex, path=['選択都道府県', '居住都道府県', "年代", "性別"], values="count"),
            )
    
    return dash.no_update



if __name__ == "__main__":
    app.run_server()
