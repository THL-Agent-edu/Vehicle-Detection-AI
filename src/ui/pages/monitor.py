import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import time

dash.register_page(__name__, path='/monitor', name='Nhận diện')

layout = html.Div([
    html.Div(
        style={"display": "flex", "alignItems": "center", "marginBottom": "1.5rem", "gap": "10px"},
        children=[
            html.Div(style={"width": "10px", "height": "10px", "borderRadius": "50%", "backgroundColor": "var(--primary-color)"}),
            html.Span("OFFLINE PROCESSING // SOURCE: FILE", style={"color": "var(--text-secondary)", "fontWeight": "600", "letterSpacing": "1px", "fontSize": "0.85rem"})
        ]
    ),
    
    html.Div(
        style={"display": "grid", "gridTemplateColumns": "1fr 3fr 1fr", "gap": "2rem"},
        children=[
            # Left: Camera Nodes
            html.Div([
                html.H4("INPUT SOURCES", style={"fontSize": "0.85rem", "color": "var(--text-secondary)", "letterSpacing": "1px", "marginBottom": "1rem"}),
                
                html.Div(className="card", style={"padding": "1rem", "marginBottom": "1rem", "borderColor": "var(--primary-color)", "backgroundColor": "var(--primary-bg)"}, children=[
                    html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, children=[
                        html.Span("CAM_01_HWY_NORTH", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                        html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%", "backgroundColor": "var(--primary-color)"})
                    ]),
                    html.Div("ACTIVE // 4K", style={"fontSize": "0.75rem", "color": "var(--primary-color)", "marginTop": "0.25rem"})
                ]),
                
                html.Div(className="card", style={"padding": "1rem", "marginBottom": "1rem"}, children=[
                    html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, children=[
                        html.Span("CAM_02_HWY_SOUTH", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                        html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%", "backgroundColor": "var(--text-secondary)"})
                    ]),
                    html.Div("STANDBY", style={"fontSize": "0.75rem", "color": "var(--text-secondary)", "marginTop": "0.25rem"})
                ]),
                
                html.Div(className="card", style={"padding": "1rem", "marginBottom": "1rem"}, children=[
                    html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, children=[
                        html.Span("CAM_04_EXIT", style={"fontWeight": "600", "fontSize": "0.9rem"}),
                        html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%", "backgroundColor": "var(--danger-color)"})
                    ]),
                    html.Div("OFFLINE", style={"fontSize": "0.75rem", "color": "var(--text-secondary)", "marginTop": "0.25rem"})
                ]),
            ]),
            
            # Middle: Monitor
            html.Div([
                html.Div(style={"display": "flex", "gap": "1rem", "marginBottom": "1rem"}, children=[
                    html.Button([html.I(className="ph ph-scan"), " Phát hiện phương tiện"], id="btn-detect", className="btn-primary", style={"display": "flex", "alignItems": "center", "gap": "5px"}),
                    html.Button([html.I(className="ph ph-text-t"), " Nhận diện biển số"], className="btn-secondary", style={"display": "flex", "alignItems": "center", "gap": "5px"})
                ]),
                
                dcc.Loading(
                    id="loading-monitor",
                    type="circle",
                    color="var(--primary-color)",
                    children=html.Div(
                        id="monitor-result",
                        className="card", 
                        style={"height": "400px", "backgroundColor": "black", "position": "relative", "display": "flex", "alignItems": "center", "justifyContent": "center", "overflow": "hidden"},
                        children=[
                            html.Img(src="https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=1000&q=80", style={"width": "100%", "opacity": "0.6"}),
                            html.H3("Sẵn sàng phân tích", style={"position": "absolute", "color": "white", "opacity": "0.5"})
                        ]
                    )
                )
            ]),
            
            # Right: Results
            html.Div([
                html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1rem"}, children=[
                    html.H4("Kết quả nhận diện", style={"margin": 0, "fontSize": "1rem"}),
                    html.I(className="ph ph-funnel", style={"color": "var(--text-secondary)", "cursor": "pointer"})
                ]),
                
                # Result Card 1
                html.Div(className="card", style={"padding": "0.75rem", "marginBottom": "1rem", "backgroundColor": "var(--danger-bg)", "borderColor": "var(--danger-color)"}, children=[
                    html.Div(style={"display": "flex", "gap": "10px"}, children=[
                        html.Div(style={"width": "60px", "height": "40px", "backgroundColor": "#1f2937", "borderRadius": "4px"}), # Thumbnail
                        html.Div(style={"flex": 1}, children=[
                            html.Div("29C-998.12", style={"color": "var(--danger-color)", "fontWeight": "700", "fontSize": "0.9rem"}),
                            html.Div("TRUCK (BLACKLIST)", style={"color": "var(--danger-color)", "fontSize": "0.7rem", "fontWeight": "600"})
                        ]),
                        html.Div("14:02:11", style={"fontSize": "0.7rem", "color": "var(--text-secondary)"})
                    ])
                ]),
                
                # Result Card 2
                html.Div(className="card", style={"padding": "0.75rem", "marginBottom": "1rem"}, children=[
                    html.Div(style={"display": "flex", "gap": "10px"}, children=[
                        html.Div(style={"width": "60px", "height": "40px", "backgroundColor": "#9ca3af", "borderRadius": "4px"}), # Thumbnail
                        html.Div(style={"flex": 1}, children=[
                            html.Div("51H-123.45", style={"fontWeight": "700", "fontSize": "0.9rem"}),
                            html.Div("CAR", style={"color": "var(--text-secondary)", "fontSize": "0.7rem", "fontWeight": "600"})
                        ]),
                        html.Div("14:02:08", style={"fontSize": "0.7rem", "color": "var(--text-secondary)"})
                    ])
                ])
            ])
        ]
    )
])

@callback(
    Output("monitor-result", "children"),
    Input("btn-detect", "n_clicks"),
    prevent_initial_call=True
)
def run_detection(n_clicks):
    time.sleep(1.5) # Giả lập AI processing time
    return [
        html.Img(src="https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=1000&q=80", style={"width": "100%", "opacity": "0.6"}),
        # Mock Bounding Boxes
        html.Div(style={"position": "absolute", "top": "150px", "left": "100px", "border": "2px solid white", "width": "120px", "height": "120px"}, children=[
            html.Div("CAR // 92%", style={"backgroundColor": "white", "color": "black", "fontSize": "0.7rem", "fontWeight": "bold", "padding": "2px 4px", "position": "absolute", "top": "-18px", "left": "-2px"}),
            html.Div("51H-123.45", style={"backgroundColor": "black", "color": "white", "fontSize": "0.7rem", "fontWeight": "bold", "padding": "2px 4px", "position": "absolute", "bottom": "-18px", "left": "-2px", "border": "1px solid white"})
        ]),
        html.Div(style={"position": "absolute", "top": "100px", "right": "150px", "border": "2px solid var(--danger-color)", "width": "160px", "height": "160px"}, children=[
            html.Div("TRUCK // 88%", style={"backgroundColor": "var(--danger-color)", "color": "white", "fontSize": "0.7rem", "fontWeight": "bold", "padding": "2px 4px", "position": "absolute", "top": "-18px", "left": "-2px"}),
            html.Div("29C-998.12", style={"backgroundColor": "black", "color": "white", "fontSize": "0.7rem", "fontWeight": "bold", "padding": "2px 4px", "position": "absolute", "bottom": "-18px", "left": "-2px", "border": "1px solid white"})
        ])
    ]

