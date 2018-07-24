import sys
import dash
from dash.dependencies import Output, State, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import ms5611

baro = ms5611.MS5611()
baro.initialize()
baro.update()
t = [0]
P = [baro.PRES]
T = [baro.TEMP]
t_max = 25
delta = 2

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("It's alive!"),
    html.H3('MS5611 Barometer'),
    dcc.Dropdown(
        id='select',
        options=[
            {'label': 'Pressure', 'value': 'PRES'},
            {'label': 'Temperature', 'value': 'TEMP'}],
        value=['PRES'],
        multi=True),
    dcc.Interval(
        id='timer',
        interval=delta * 1000,
        n_intervals=0),
    html.Div([
        dcc.Graph(
            id='pres_plot',
            animate=False)],
        id='show_pres'),
    html.Div([
        dcc.Graph(
            id='temp_plot',
            animate=False)],
        id='show_temp'),
    html.Div(
        id='data',
        style={'display': 'none'})])


@app.callback(Output('data', 'style'),
              [Input('timer', 'n_intervals')],
              [State('select', 'value')])
def update_data(_, selection):
    global t, P, T, t_max
    t.append(t[-1] + delta)
    baro.update()
    P.append(round(baro.PRES, 3))
    T.append(round(baro.TEMP, 3))
    if t_max - t[-1] <= delta:
        t_max *= 2
    return {'display': 'none'}


@app.callback(Output('show_pres', 'style'),
              [Input('timer', 'n_intervals')],
              [State('select', 'value')])
def show_pres(_, selection):
    return {'display': ('block' if 'PRES' in selection else 'none')}


@app.callback(Output('show_temp', 'style'),
              [Input('timer', 'n_intervals')],
              [State('select', 'value')])
def show_temp(_, selection):
    return {'display': ('block' if 'TEMP' in selection else 'none')}


@app.callback(Output('pres_plot', 'figure'),
              [Input('timer', 'n_intervals')],
              [State('select', 'value')])
def pres_plot(_, selection):
    data, layout = [], go.Layout()
    if 'PRES' in selection:
        data = [go.Scatter(
            x=list(t),
            y=list(P),
            mode='lines+markers')]
        layout = go.Layout(
            xaxis={'range': [0, t_max], 'title': 'time, s'},
            yaxis={'range': [1007, 1008], 'title': 'Pressure, mbar'},
            height=400,
            width=1500)
    return {'data': data, 'layout': layout}


@app.callback(Output('temp_plot', 'figure'),
              [Input('timer', 'n_intervals')],
              [State('select', 'value')])
def temp_plot(_, selection):
    data, layout = [], go.Layout()
    if 'TEMP' in selection:
        data = [go.Scatter(
            x=list(t),
            y=list(T),
            mode='lines+markers')]
        layout = go.Layout(
            xaxis={'range': [0, t_max], 'title': 'time, s'},
            yaxis={'range': [35, 40], 'title': 'Temperature, °C'},
            height=400,
            width=1500)
    return {'data': data, 'layout': layout}


if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0')
