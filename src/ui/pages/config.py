import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/config', name='Cài đặt')

layout = html.Div([
    html.H3("Cấu hình Hệ thống", style={"marginBottom": "0.5rem"}),
    html.P("Quản lý cấu hình AI Model, lưu trữ File và hiển thị giao diện.", style={"color": "var(--text-secondary)", "marginBottom": "2rem"}),
    
    html.Div(
        className="card",
        children=[
            html.H4("🧠 AI Model Settings", style={"fontSize": "1.1rem", "marginBottom": "1.5rem"}),
            html.Div(style={"display": "flex", "gap": "2rem", "marginBottom": "1.5rem"}, children=[
                html.Div(style={"flex": 1}, children=[
                    html.Label("Model Selection", style={"fontWeight": "600", "fontSize": "0.9rem", "marginBottom": "0.5rem", "display": "block"}),
                    dcc.Dropdown(options=["YOLOv8 Medium (Balanced)", "YOLOv8 Large (High Accuracy)", "YOLOv8 Nano (Fast)"], value="YOLOv8 Medium (Balanced)")
                ]),
                html.Div(style={"flex": 1}, children=[
                    html.Label("Confidence Threshold (%)", style={"fontWeight": "600", "fontSize": "0.9rem", "marginBottom": "0.5rem", "display": "block"}),
                    dcc.Slider(min=0, max=100, step=5, value=85, marks={0: '0', 50: '50', 100: '100'})
                ])
            ]),
            
            html.Hr(style={"borderColor": "var(--border-color)", "marginBottom": "1.5rem"}),
            
            html.H4("💾 File Storage Settings", style={"fontSize": "1.1rem", "marginBottom": "1.5rem"}),
            html.Div(style={"marginBottom": "1.5rem"}, children=[
                html.Label("Upload Directory", style={"fontWeight": "600", "fontSize": "0.9rem", "marginBottom": "0.5rem", "display": "block"}),
                dcc.Input(type="text", value="/mnt/data/uploads", style={"width": "100%", "padding": "0.5rem", "borderRadius": "4px", "border": "1px solid var(--border-color)"})
            ]),
            html.Div(style={"display": "flex", "gap": "2rem", "marginBottom": "1.5rem"}, children=[
                html.Div(style={"flex": 1}, children=[
                    html.Label("Giới hạn dung lượng", style={"fontWeight": "600", "fontSize": "0.9rem", "marginBottom": "0.5rem", "display": "block"}),
                    dcc.Dropdown(options=["50 MB", "500 MB", "1 GB", "Không giới hạn"], value="500 MB")
                ]),
                html.Div(style={"flex": 1}, children=[
                    html.Label("Tự động dọn dẹp", style={"fontWeight": "600", "fontSize": "0.9rem", "marginBottom": "0.5rem", "display": "block"}),
                    dcc.Dropdown(options=["Ngay khi phân tích xong", "Giữ lại 7 ngày", "Giữ lại 30 ngày", "Không bao giờ xóa"], value="Giữ lại 7 ngày")
                ])
            ]),
            
            html.Hr(style={"borderColor": "var(--border-color)", "marginBottom": "1.5rem"}),
            
            html.H4("🔤 Format & OCR Settings", style={"fontSize": "1.1rem", "marginBottom": "1.5rem"}),
            html.Div(style={"marginBottom": "1.5rem"}, children=[
                html.Label("Plate Formatting Regex", style={"fontWeight": "600", "fontSize": "0.9rem", "marginBottom": "0.5rem", "display": "block"}),
                dcc.Input(type="text", value="^[0-9]{2}[A-Z]{1,2}-[0-9]{4,5}$", style={"width": "100%", "padding": "0.5rem", "borderRadius": "4px", "border": "1px solid var(--border-color)"})
            ]),
            dcc.Checklist(
                options=[{'label': ' Tự động loại bỏ ký tự đặc biệt khỏi kết quả OCR', 'value': '1'}],
                value=['1'],
                style={"marginBottom": "0.5rem", "fontSize": "0.9rem"}
            ),
            dcc.Checklist(
                options=[{'label': ' Tự động sửa lỗi sai phổ biến (Auto-correct OCR errors)', 'value': '1'}],
                value=['1'],
                style={"marginBottom": "1.5rem", "fontSize": "0.9rem"}
            ),
            
            html.Hr(style={"borderColor": "var(--border-color)", "marginBottom": "1.5rem"}),
            html.Button("💾 Lưu Cấu Hình", id="btn-save-config", className="btn-primary")
        ]
    ),
    
    dbc.Toast(
        "Cấu hình đã được lưu lại thành công!",
        id="toast-config",
        header="Thành công",
        is_open=False,
        dismissable=True,
        icon="success",
        duration=3000,
        style={"position": "fixed", "top": 20, "right": 20, "width": 350, "zIndex": 9999}
    )
])

@callback(
    Output("toast-config", "is_open"),
    Input("btn-save-config", "n_clicks"),
    prevent_initial_call=True
)
def save_config(n):
    if n:
        return True
    return False
