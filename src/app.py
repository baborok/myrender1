import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Чтение данных из файлов Excel
df1 = pd.read_excel('06 (1).xls')
df2 = pd.read_excel('06.xls')

# Создание Dash приложения
app = dash.Dash(__name__)
server=app.server

# Макет страницы
app.layout = html.Div([
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in df1.columns[1:]],
        value=df1.columns[1],
        multi=True
    ),
    html.Div(id='graphs-container')
])

# Обновление графиков при выборе столбца(ов) из выпадающего списка
@app.callback(
    Output('graphs-container', 'children'),
    [Input('column-dropdown', 'value')]
)
def update_graphs(selected_columns):
    graphs = []
    time_column = 'Время'

    for col in selected_columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df1[time_column], y=df1[col], mode='lines', name=f'Файл 1 - {col}', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df2[time_column], y=df2[col], mode='lines', name=f'Файл 2 - {col}', line=dict(color='red')))
        fig.update_layout(title=f'График {col} по времени',
                          xaxis_title='Время',
                          yaxis_title=col)

        graphs.append(
            dcc.Graph(
                id=f'graph-{col}',
                figure=fig
            )
        )

    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)
