import os
import base64
import io
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

# Создание Dash приложения
app = dash.Dash(__name__)

server=app.server

# Макет страницы
app.layout = html.Div([
    dcc.Dropdown(
        id='data-folder-dropdown',
        options=[
            {'label': '06:00', 'value': '06'},
            {'label': '07:00', 'value': '07'},
            {'label': '08:00', 'value': '08'},
            {'label': '09:00', 'value': '09'},
            {'label': '10:00', 'value': '10'},
            {'label': '11:00', 'value': '11'},
            {'label': '12:00', 'value': '12'},
            {'label': '13:00', 'value': '13'},
            {'label': '14:00', 'value': '14'},
            {'label': '15:00', 'value': '15'},
            {'label': '16:00', 'value': '16'},
            {'label': '17:00', 'value': '17'},
            {'label': '18:00', 'value': '18'}
        ],
        value='06',  # Default value is "06"
        placeholder='Выберите папку с данными',
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id='column-dropdown',
        options=[],  # Options will be populated based on folder selection
        value='',   # Default value is an empty string
        multi=True
    ),
    html.Div(id='graphs-container')
])

def get_file_options(selected_folder):
    data_folder = os.path.join(os.getcwd(), selected_folder)
    file_options = []
    if os.path.exists(data_folder) and os.path.isdir(data_folder):
        for file in os.listdir(data_folder):
            if file.endswith('.xls') or file.endswith('.xlsx'):
                file_options.append({'label': file, 'value': file})
    return file_options

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'xls' in filename:
            # Excel file format (older version)
            df = pd.read_excel(io.BytesIO(decoded), engine='xlrd')
        elif 'xlsx' in filename:
            # Excel file format (newer version)
            df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
    except Exception as e:
        print(e)
        return None

    return df

@app.callback(
    Output('column-dropdown', 'options'),
    Input('data-folder-dropdown', 'value')
)
def update_column_dropdown(selected_folder):
    data_folder = os.path.join(os.getcwd(), selected_folder)

    file1 = None
    file2 = None

    for selected_file in os.listdir(data_folder):
        if selected_file.endswith('.xls') or selected_file.endswith('.xlsx'):
            df = pd.read_excel(os.path.join(data_folder, selected_file), engine='xlrd')
            if file1 is None:
                file1 = df
            elif file2 is None:
                file2 = df

    if file1 is not None and file2 is not None:
        combined_df = pd.concat([file1, file2])
        return [{'label': col, 'value': col} for col in combined_df.columns[1:]]
    else:
        return []

@app.callback(
    Output('graphs-container', 'children'),
    [Input('data-folder-dropdown', 'value'),
     Input('column-dropdown', 'value')]
)
def update_graphs(selected_folder, selected_columns):
    data_folder = os.path.join(os.getcwd(), selected_folder)

    graphs = []
    time_column = 'Время'

    file1 = None
    file2 = None

    for selected_file in os.listdir(data_folder):
        if selected_file.endswith('.xls') or selected_file.endswith('.xlsx'):
            df = pd.read_excel(os.path.join(data_folder, selected_file), engine='xlrd')
            if file1 is None:
                file1 = df
            elif file2 is None:
                file2 = df

    if file1 is not None and file2 is not None:
        combined_df = pd.concat([file1, file2])

        for col in selected_columns:
            if col != time_column:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=file1[time_column], y=file1[col], mode='lines', name=f'Генератор - {col}', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=file2[time_column], y=file2[col], mode='lines', name=f'Сеть - {col}', line=dict(color='red')))
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
