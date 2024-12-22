from typing import List, Dict, Any
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objs as go

# Наши модули
from weather_service import get_city_data, get_extended_forecast
from forecast_parser import process_forecast_data
from map_builder import generate_map_chart

app = Dash(__name__)
app.title = "SkyObserver: Weather & Routes"

# -----------------------------------------------------------------------------
# Стиль страницы
# -----------------------------------------------------------------------------
app_layout_style = {
    "backgroundColor": "#ECEFF1",  # светлый фон всей страницы
    "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    "padding": "20px"
}

# Стиль заголовка
header_style = {
    "textAlign": "center",
    "fontSize": "2em",
    "color": "#37474F",
    "marginBottom": "30px"
}

# Стиль «карточки», где находятся контролы ввода
card_style = {
    "backgroundColor": "#FFFFFF",
    "borderRadius": "10px",
    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
    "padding": "20px",
    "marginBottom": "25px"
}

# -----------------------------------------------------------------------------
# Макет Dash-приложения
# -----------------------------------------------------------------------------
app.layout = html.Div(style=app_layout_style, children=[
    html.H1("SkyObserver: Мировой прогноз и карта", style=header_style),

    # Блок с «карточкой» для ввода
    html.Div([
        html.Label("Введи города (через запятую):"),
        dcc.Input(
            id="user-input-cities",
            type="text",
            value="Moscow, Saint Petersburg",
            style={"width": "100%", "marginBottom": "15px"}
        ),
        html.Label("Период прогноза (дни):"),
        dcc.RadioItems(
            id="forecast-range-radio",
            options=[
                {"label": "1 день", "value": 1},
                {"label": "3 дня", "value": 3},
                {"label": "5 дней", "value": 5},
            ],
            value=3,
            labelStyle={"display": "inline-block", "marginRight": "15px"}
        ),
        html.Button(
            "Показать результаты",
            id="submit-btn",
            n_clicks=0,
            style={
                "backgroundColor": "#00897B",
                "color": "#FFFFFF",
                "border": "none",
                "padding": "10px 20px",
                "borderRadius": "5px",
                "cursor": "pointer",
                "marginTop": "10px"
            }
        )
    ], style=card_style),

    dcc.Loading(
        id="loading-wrapper",
        type="circle",
        children=html.Div(id="content-block", style={"marginTop": "20px"})
    )
])


# -----------------------------------------------------------------------------
# Callback
# -----------------------------------------------------------------------------
@app.callback(
    Output("content-block", "children"),
    Input("submit-btn", "n_clicks"),
    State("user-input-cities", "value"),
    State("forecast-range-radio", "value")
)
def display_weather_information(n_clicks: int, entered_cities: str, forecast_days: int):
    """Обрабатывает ввод пользователя и отображает погоду + карту."""
    if n_clicks == 0:
        return html.Div(
            "Пока данных нет. Нажмите «Показать результаты», чтобы загрузить прогноз.",
            style={"textAlign": "center", "color": "#607D8B"}
        )

    # Разделяем города, убирая пустые строки
    city_names: List[str] = [city.strip() for city in entered_cities.split(",") if city.strip()]
    map_points: List[Dict[str, Any]] = []
    charts = []

    for city in city_names:
        try:
            city_info = get_city_data(city)
            map_points.append({
                "name": city_info["city_name"],
                "lat": city_info["latitude"],
                "lon": city_info["longitude"]
            })

            # Получаем прогноз
            raw_forecast = get_extended_forecast(city_info["city_key"], forecast_days)
            forecast_parsed = process_forecast_data(raw_forecast)

            # Создаём графики Plotly
            trace_min_temp = go.Scatter(
                x=forecast_parsed["dates"],
                y=forecast_parsed["min_temps"],
                mode="lines+markers",
                name="Мин. температура",
                line=dict(color="#2196F3"),
                marker=dict(color="#2196F3")
            )
            trace_max_temp = go.Scatter(
                x=forecast_parsed["dates"],
                y=forecast_parsed["max_temps"],
                mode="lines+markers",
                name="Макс. температура",
                line=dict(color="#FB8C00"),
                marker=dict(color="#FB8C00")
            )
            trace_wind_speed = go.Bar(
                x=forecast_parsed["dates"],
                y=forecast_parsed["winds"],
                name="Ветер",
                marker=dict(color="rgba(255,0,0,0.4)"),
                yaxis="y2"
            )

            layout_config = go.Layout(
                title=f"Прогноз в {city}",
                xaxis={"title": "Дата"},
                yaxis={"title": "Температура (°C)"},
                yaxis2={
                    "title": "Скорость ветра (м/с)",
                    "overlaying": "y",
                    "side": "right"
                },
                # фон легенды и графика
                plot_bgcolor="#F1F8E9",
                paper_bgcolor="#F1F8E9",
                legend=dict(x=0, y=1.1),
                margin={"l": 50, "r": 50, "t": 80, "b": 50}
            )

            weather_figure = go.Figure(
                data=[trace_min_temp, trace_max_temp, trace_wind_speed],
                layout=layout_config
            )

            charts.append(
                html.Div([
                    dcc.Graph(figure=weather_figure)
                ], style={
                    "backgroundColor": "#FFFFFF",
                    "borderRadius": "10px",
                    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                    "padding": "20px",
                    "marginBottom": "30px"
                })
            )

        except Exception as err:
            charts.append(html.Div(
                f"Ошибка при загрузке данных для {city}: {err}",
                style={"color": "red", "marginBottom": "20px"}
            ))

    # Отображаем карту, если есть города
    if map_points:
        map_figure = generate_map_chart(map_points)
        # Ставим карту в начало
        charts.insert(
            0,
            html.Div([
                dcc.Graph(figure=map_figure)
            ], style={
                "backgroundColor": "#FFFFFF",
                "borderRadius": "10px",
                "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                "padding": "20px",
                "marginBottom": "30px"
            })
        )

    return html.Div(charts)


# -----------------------------------------------------------------------------
# Запуск приложения
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
