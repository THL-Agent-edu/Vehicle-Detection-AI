import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name='Dữ liệu')

layout = html.Div([
    html.H3("Quản lý Dữ liệu", style={"marginBottom": "0.5rem"}),
    html.P("Tải lên ảnh hoặc video để tiền xử lý và chuẩn bị cho nhận diện phương tiện.", style={"color": "var(--text-secondary)", "marginBottom": "2rem"}),
    
    # Upload Area
    dcc.Upload(
        id='upload-data',
        multiple=True,
        children=html.Div(
            className="card",
            style={
                "borderStyle": "dashed", 
                "borderWidth": "2px", 
                "textAlign": "center", 
                "padding": "4rem 2rem", 
                "backgroundColor": "var(--bg-subtle)", 
                "marginBottom": "2rem",
                "cursor": "pointer"
            },
            children=[
                html.I(className="ph ph-upload-simple", style={"fontSize": "3rem", "color": "var(--text-secondary)", "marginBottom": "1rem", "display": "block"}),
                html.H4("Kéo thả file vào đây hoặc Click để chọn", style={"margin": "0 0 0.5rem 0"}),
                html.P("Hỗ trợ: JPG, PNG, MP4 (Tối đa 50MB)", style={"color": "var(--text-secondary)", "fontSize": "0.85rem", "margin": 0})
            ]
        )
    ),
    
    dbc.Toast(
        id='upload-toast',
        header="Thành công",
        is_open=False,
        dismissable=True,
        icon="success",
        duration=3000,
        style={"position": "fixed", "top": 20, "right": 20, "width": 350, "zIndex": 9999}
    ),
    
    # Header List
    html.Div(
        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1rem"},
        children=[
            html.H4("Danh sách file đã tải", style={"margin": 0, "fontSize": "1.1rem"}),
            html.Button([html.I(className="ph ph-magic-wand"), " Tiền xử lý dữ liệu"], className="btn-primary")
        ]
    ),
    
    # Table
    html.Div(
        className="card",
        style={"padding": 0, "overflow": "hidden"},
        children=[
            html.Table(
                className="custom-table",
                children=[
                    html.Thead(
                        html.Tr([
                            html.Th("Tên File"),
                            html.Th("Định dạng"),
                            html.Th("Dung lượng"),
                            html.Th("Trạng thái"),
                            html.Th("Thao tác", style={"textAlign": "right"})
                        ])
                    ),
                    html.Tbody([
                        html.Tr([
                            html.Td("cam_hwy_01.mp4", style={"fontWeight": "600"}),
                            html.Td("MP4"),
                            html.Td("12.5 MB"),
                            html.Td(html.Span("Chờ xử lý", className="status-badge", style={"color": "var(--warning-text)", "backgroundColor": "var(--warning-bg)"})),
                            html.Td(html.I(className="ph ph-trash", style={"color": "var(--danger-color)", "cursor": "pointer", "fontSize": "1.1rem"}), style={"textAlign": "right"})
                        ]),
                        html.Tr([
                            html.Td("test_img_44.jpg", style={"fontWeight": "600"}),
                            html.Td("JPG"),
                            html.Td("1.2 MB"),
                            html.Td(html.Span("Đã chuẩn hóa", className="status-badge", style={"color": "var(--success-color)", "backgroundColor": "var(--success-bg)"})),
                            html.Td(html.I(className="ph ph-trash", style={"color": "var(--danger-color)", "cursor": "pointer", "fontSize": "1.1rem"}), style={"textAlign": "right"})
                        ])
                    ])
                ]
            )
        ]
    )
])

@callback(
    Output('upload-toast', 'children'),
    Output('upload-toast', 'is_open'),
    Input('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_output(filenames):
    if filenames is not None:
        return f"Đã tải lên {len(filenames)} file thành công!", True
    return "", False
