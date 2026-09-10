import dash
from dash import html, dcc, Input, Output, clientside_callback
import dash_bootstrap_components as dbc

import os

# Đường dẫn tuyệt đối đến thư mục chứa app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Khởi tạo ứng dụng Dash với tính năng Multi-page và giao diện Bootstrap/Phosphor Icons
app = dash.Dash(
    __name__, 
    use_pages=True, 
    pages_folder=os.path.join(BASE_DIR, 'pages'),
    assets_folder=os.path.join(BASE_DIR, 'assets'),
    external_stylesheets=[
        dbc.themes.BOOTSTRAP, 
        "https://unpkg.com/@phosphor-icons/web"
    ],
    suppress_callback_exceptions=True
)

app.layout = html.Div(
    className="dashboard-layout",
    children=[
        # Sidebar
        html.Div(
            className="sidebar",
            children=[
                html.Div(
                    className="sidebar-header",
                    children=[
                        html.H2("V-AI SYSTEM", style={"margin": 0, "fontSize": "1.5rem", "fontWeight": "800", "color": "var(--primary-color)"}),
                        html.P("V-AI MONITORING", style={"fontSize": "0.7rem", "letterSpacing": "1px", "color": "var(--text-secondary)", "marginTop": "5px"})
                    ]
                ),
                html.Div(
                    className="sidebar-nav",
                    children=[
                        dbc.NavLink([html.I(className="ph ph-database"), " Dữ liệu"], href="/", active="exact", className="nav-link"),
                        dbc.NavLink([html.I(className="ph ph-video-camera"), " Nhận diện"], href="/monitor", active="exact", className="nav-link"),
                        dbc.NavLink([html.I(className="ph ph-info"), " Thông tin"], href="/history", active="exact", className="nav-link"),
                        dbc.NavLink([html.I(className="ph ph-chart-bar"), " Báo cáo"], href="/analytics", active="exact", className="nav-link"),
                        dbc.NavLink([html.I(className="ph ph-gear"), " Cấu hình"], href="/config", active="exact", className="nav-link")
                    ]
                )
            ]
        ),
        
        # Main Content
        html.Div(
            className="main-content",
            children=[
                # Topbar
                html.Div(
                    className="topbar",
                    children=[
                        html.Div(), # Placeholder
                        html.Div(
                            style={"display": "flex", "gap": "1.5rem", "alignItems": "center", "fontSize": "1.2rem", "color": "var(--text-secondary)"},
                            children=[
                                html.Div(
                                    id="theme-toggle-container",
                                    style={"display": "flex", "alignItems": "center", "gap": "8px", "cursor": "pointer", "backgroundColor": "var(--bg-color)", "padding": "6px 12px", "borderRadius": "20px", "fontSize": "0.95rem", "border": "1px solid var(--border-color)"},
                                    children=[
                                        html.I(id="theme-toggle", className="ph ph-moon"),
                                        html.Span("Giao diện", style={"fontWeight": "600"})
                                    ]
                                ),
                                html.I(className="ph ph-bell", style={"cursor": "pointer"}),
                                html.I(className="ph ph-gear", style={"cursor": "pointer"}),
                            ]
                        )
                    ]
                ),
                
                # Page Content Router
                html.Div(
                    className="page-content",
                    children=dash.page_container
                )
            ]
        )
    ]
)

clientside_callback(
    """
    function(n_clicks) {
        let currentTheme = document.documentElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'light');
            return 'ph ph-moon';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            return 'ph ph-sun';
        }
    }
    """,
    Output("theme-toggle", "className"),
    Input("theme-toggle-container", "n_clicks"),
    prevent_initial_call=True
)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8050)
