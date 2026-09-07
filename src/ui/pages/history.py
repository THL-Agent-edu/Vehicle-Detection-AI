import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/history', name='Thông tin')

layout = html.Div([
    html.Div(
        style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "marginBottom": "2rem"},
        children=[
            html.Div([
                html.H3("Lịch sử & Kết quả", style={"marginBottom": "0.5rem"}),
                html.P("Review AI detection logs and historical analysis data.", style={"color": "var(--text-secondary)", "margin": 0})
            ]),
            html.Div(style={"display": "flex", "gap": "1rem"}, children=[
                html.Button([html.I(className="ph ph-floppy-disk"), " Lưu thông tin"], className="btn-primary"),
                html.Button([html.I(className="ph ph-download-simple"), " Export CSV"], className="btn-secondary", style={"backgroundColor": "#dbeafe", "borderColor": "transparent", "color": "var(--primary-color)", "fontWeight": "600"})
            ])
        ]
    ),
    
    html.Div(
        className="card",
        style={"padding": "0"},
        children=[
            # Filters
            html.Div(
                style={"padding": "1.5rem", "borderBottom": "1px solid var(--border-color)", "display": "grid", "gridTemplateColumns": "1fr 1fr 1fr 1fr", "gap": "1rem"},
                children=[
                    html.Div([
                        html.Label("Date Range", style={"fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.5rem", "display": "block"}),
                        dcc.Input(type="text", placeholder="2023-10-24 - 2023-10-25", style={"width": "100%", "padding": "0.5rem", "borderRadius": "4px", "border": "1px solid var(--border-color)"})
                    ]),
                    html.Div([
                        html.Label("Plate Search", style={"fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.5rem", "display": "block"}),
                        dcc.Input(id="filter-plate", type="text", placeholder="Enter license plate...", style={"width": "100%", "padding": "0.5rem", "borderRadius": "4px", "border": "1px solid var(--border-color)"})
                    ]),
                    html.Div([
                        html.Label("Vehicle Type", style={"fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.5rem", "display": "block"}),
                        dcc.Dropdown(id="filter-type", options=["All Types", "Car", "Truck", "SUV", "Motorcycle"], value="All Types")
                    ]),
                    html.Div([
                        html.Label("Status List", style={"fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.5rem", "display": "block"}),
                        dcc.Dropdown(id="filter-status", options=["All Statuses", "WHITELIST", "BLACKLIST", "UNKNOWN"], value="All Statuses")
                    ]),
                ]
            ),
            
            # Table
            html.Table(
                className="custom-table",
                children=[
                    html.Thead(
                        html.Tr([
                            html.Th("ID"), html.Th("Timestamp"), html.Th("Thumbnail"), 
                            html.Th("Plate Number"), html.Th("Classification"), html.Th("Status"), 
                            html.Th("AI Confidence"), html.Th("Actions", style={"textAlign": "center"})
                        ])
                    ),
                    html.Tbody(id="history-table-body", children=[
                        html.Tr([
                            html.Td("#VX-9921", style={"fontWeight": "600", "color": "var(--text-secondary)"}),
                            html.Td(html.Div(["10/24 14:32:01", html.Br(), html.Span("CAM-04-NORTH", style={"fontSize": "0.75rem", "color": "var(--text-secondary)"})])),
                            html.Td(html.Div(style={"width": "50px", "height": "30px", "backgroundColor": "#1f2937", "borderRadius": "4px"})),
                            html.Td(html.Span("51G-882.14", style={"border": "1px solid var(--danger-color)", "color": "var(--danger-color)", "padding": "4px 8px", "borderRadius": "4px", "fontWeight": "600"})),
                            html.Td("SUV - Black"),
                            html.Td(html.Span("BLACKLIST", className="status-badge status-blacklist")),
                            html.Td(html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                                html.Div(style={"flex": 1, "height": "6px", "backgroundColor": "#fee2e2", "borderRadius": "3px"}, children=[
                                    html.Div(style={"width": "98%", "height": "100%", "backgroundColor": "var(--danger-color)", "borderRadius": "3px"})
                                ]),
                                html.Span("98%", style={"fontSize": "0.8rem", "fontWeight": "600"})
                            ])),
                            html.Td(html.Div(style={"display": "flex", "gap": "10px", "justifyContent": "center"}, children=[
                                html.I(className="ph ph-pencil-simple", style={"cursor": "pointer"}),
                                html.I(className="ph ph-eye", style={"cursor": "pointer"})
                            ]))
                        ]),
                        html.Tr([
                            html.Td("#VX-9920", style={"fontWeight": "600", "color": "var(--text-secondary)"}),
                            html.Td(html.Div(["10/24 14:31:45", html.Br(), html.Span("CAM-02-EAST", style={"fontSize": "0.75rem", "color": "var(--text-secondary)"})])),
                            html.Td(html.Div(style={"width": "50px", "height": "30px", "backgroundColor": "#9ca3af", "borderRadius": "4px"})),
                            html.Td(html.Span("29C-123.45", style={"border": "1px solid var(--primary-color)", "color": "var(--primary-color)", "padding": "4px 8px", "borderRadius": "4px", "fontWeight": "600"})),
                            html.Td("Commercial Truck"),
                            html.Td(html.Span("WHITELIST", className="status-badge status-whitelist")),
                            html.Td(html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                                html.Div(style={"flex": 1, "height": "6px", "backgroundColor": "#dbeafe", "borderRadius": "3px"}, children=[
                                    html.Div(style={"width": "92%", "height": "100%", "backgroundColor": "var(--primary-color)", "borderRadius": "3px"})
                                ]),
                                html.Span("92%", style={"fontSize": "0.8rem", "fontWeight": "600"})
                            ])),
                            html.Td(html.Div(style={"display": "flex", "gap": "10px", "justifyContent": "center"}, children=[
                                html.I(className="ph ph-pencil-simple", style={"cursor": "pointer"}),
                                html.I(className="ph ph-eye", style={"cursor": "pointer"})
                            ]))
                        ])
                    ])
                ]
            ),
            
            # Pagination
            html.Div(
                style={"padding": "1rem 1.5rem", "borderTop": "1px solid var(--border-color)", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "fontSize": "0.85rem"},
                children=[
                    html.Span("Showing 1-3 of 1,492 entries"),
                    html.Div(style={"display": "flex", "gap": "5px"}, children=[
                        html.Button("<", style={"border": "none", "background": "none", "cursor": "pointer"}),
                        html.Button("1", style={"border": "none", "backgroundColor": "var(--primary-color)", "color": "white", "borderRadius": "4px", "width": "24px", "height": "24px", "cursor": "pointer"}),
                        html.Button("2", style={"border": "none", "background": "none", "cursor": "pointer"}),
                        html.Button("...", style={"border": "none", "background": "none"}),
                        html.Button("49", style={"border": "none", "background": "none", "cursor": "pointer"}),
                        html.Button(">", style={"border": "none", "background": "none", "cursor": "pointer"})
                    ])
                ]
            )
        ]
    )
])

# Dữ liệu gốc giả lập (Global state for mockup)
mock_data = [
    {"id": "#VX-9921", "time": "10/24 14:32:01", "cam": "CAM-04-NORTH", "plate": "51G-882.14", "type": "SUV - Black", "status": "BLACKLIST", "conf": "98%"},
    {"id": "#VX-9920", "time": "10/24 14:31:45", "cam": "CAM-02-EAST", "plate": "29C-123.45", "type": "Commercial Truck", "status": "WHITELIST", "conf": "92%"},
    {"id": "#VX-9919", "time": "10/24 14:30:10", "cam": "CAM-01-MAIN", "plate": "30F-999.99", "type": "Car - Silver", "status": "UNKNOWN", "conf": "85%"}
]

@callback(
    Output("history-table-body", "children"),
    Input("filter-plate", "value"),
    Input("filter-type", "value"),
    Input("filter-status", "value")
)
def update_table(plate, v_type, status):
    filtered = mock_data
    
    if plate:
        filtered = [row for row in filtered if plate.lower() in row['plate'].lower()]
    if v_type and v_type != "All Types":
        filtered = [row for row in filtered if v_type.lower() in row['type'].lower()]
    if status and status != "All Statuses":
        filtered = [row for row in filtered if row['status'] == status]
        
    rows = []
    for row in filtered:
        # Determine styles based on status
        if row['status'] == 'BLACKLIST':
            status_class = "status-badge status-blacklist"
            plate_color = "var(--danger-color)"
            bar_color = "var(--danger-color)"
            bg_bar = "var(--danger-bg)"
        elif row['status'] == 'WHITELIST':
            status_class = "status-badge status-whitelist"
            plate_color = "var(--primary-color)"
            bar_color = "var(--primary-color)"
            bg_bar = "var(--primary-bg)"
        else:
            status_class = "status-badge"
            plate_color = "var(--text-secondary)"
            bar_color = "var(--text-secondary)"
            bg_bar = "var(--secondary-bg)"
            
        rows.append(html.Tr([
            html.Td(row['id'], style={"fontWeight": "600", "color": "var(--text-secondary)"}),
            html.Td(html.Div([row['time'], html.Br(), html.Span(row['cam'], style={"fontSize": "0.75rem", "color": "var(--text-secondary)"})])),
            html.Td(html.Div(style={"width": "50px", "height": "30px", "backgroundColor": "#1f2937", "borderRadius": "4px"})),
            html.Td(html.Span(row['plate'], style={"border": f"1px solid {plate_color}", "color": plate_color, "padding": "4px 8px", "borderRadius": "4px", "fontWeight": "600"})),
            html.Td(row['type']),
            html.Td(html.Span(row['status'], className=status_class)),
            html.Td(html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                html.Div(style={"flex": 1, "height": "6px", "backgroundColor": bg_bar, "borderRadius": "3px"}, children=[
                    html.Div(style={"width": row['conf'], "height": "100%", "backgroundColor": bar_color, "borderRadius": "3px"})
                ]),
                html.Span(row['conf'], style={"fontSize": "0.8rem", "fontWeight": "600"})
            ])),
            html.Td(html.Div(style={"display": "flex", "gap": "10px", "justifyContent": "center"}, children=[
                html.I(className="ph ph-pencil-simple", style={"cursor": "pointer"}),
                html.I(className="ph ph-eye", style={"cursor": "pointer"})
            ]))
        ]))
    return rows
