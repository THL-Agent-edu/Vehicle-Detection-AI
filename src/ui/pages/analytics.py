import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

dash.register_page(__name__, path='/analytics', name='Báo cáo')

# Create a mock bar chart matching the screenshot
fig = go.Figure(data=[
    go.Bar(
        x=["00h", "04h", "08h", "12h", "16h", "20h", "24h"],
        y=[100, 200, 800, 500, 600, 950, 300],
        marker_color='#3b82f6',
        width=0.6
    )
])
fig.update_layout(
    margin=dict(l=0, r=0, t=20, b=0),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(gridcolor='#f3f4f6', tickcolor='rgba(0,0,0,0)', tickfont=dict(color='#9ca3af')),
    xaxis=dict(tickcolor='rgba(0,0,0,0)', tickfont=dict(color='#9ca3af')),
    height=280
)

# Create Donut Chart
donut_fig = go.Figure(data=[go.Pie(
    labels=['Xe máy', 'Ô tô con', 'Xe tải/Khách'], 
    values=[55, 30, 15], 
    hole=.7,
    marker=dict(colors=['#3b82f6', '#9ca3af', '#ef4444']),
    textinfo='none'
)])
donut_fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False,
    height=160,
    width=160,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    annotations=[dict(text='100%', x=0.5, y=0.5, font_size=24, showarrow=False, font=dict(color='#9ca3af'))]
)

layout = html.Div([
    html.Div(
        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "2rem"},
        children=[
            html.H3("Phân tích & Thống kê", style={"margin": 0}),
            html.Div(style={"display": "flex", "gap": "1rem"}, children=[
                html.Button("Tạo báo cáo thống kê", className="btn-primary"),
                html.Button("Xuất PDF/CSV", className="btn-secondary"),
                html.Button([html.I(className="ph ph-printer"), " In báo cáo"], className="btn-secondary", style={"backgroundColor": "#374151", "color": "white", "borderColor": "#374151"})
            ])
        ]
    ),
    
    html.Div(
        style={"display": "grid", "gridTemplateColumns": "3fr 1fr", "gap": "1.5rem"},
        children=[
            # Left Column
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "1.5rem"},
                children=[
                    # Top Row of Left Column
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "1.5rem"},
                        children=[
                            html.Div(className="card", children=[
                                html.P("Total Vehicle Volume", style={"color": "var(--text-secondary)", "fontSize": "0.85rem", "margin": "0 0 10px 0"}),
                                html.H2("142,893", style={"margin": "0 0 5px 0"}),
                                html.Span("↗ +12.4% vs yesterday", style={"color": "var(--success-color)", "fontSize": "0.8rem", "fontWeight": "500"})
                            ]),
                            html.Div(className="card", style={"borderColor": "var(--danger-color)"}, children=[
                                html.P("Blacklist Alerts (24h)", style={"color": "var(--danger-color)", "fontSize": "0.85rem", "margin": "0 0 10px 0"}),
                                html.H2("47", style={"margin": "0 0 5px 0", "color": "var(--danger-color)"}),
                                html.Span("! Requires immediate review", style={"color": "var(--text-secondary)", "fontSize": "0.8rem", "fontWeight": "500"})
                            ]),
                            html.Div(className="card", children=[
                                html.P("Core Metrics", style={"color": "var(--text-secondary)", "fontSize": "0.85rem", "margin": "0 0 10px 0"}),
                                html.Div(style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}, children=[
                                    html.Span("V-AI Processing Load", style={"fontSize": "0.8rem", "fontWeight": "500"}),
                                    html.Span("68%", style={"fontSize": "0.8rem", "fontWeight": "600", "color": "var(--success-color)"})
                                ]),
                                html.Div(style={"height": "4px", "backgroundColor": "var(--secondary-bg)", "borderRadius": "2px", "marginBottom": "15px"}, children=[
                                    html.Div(style={"width": "68%", "height": "100%", "backgroundColor": "var(--success-color)", "borderRadius": "2px"})
                                ]),
                                html.Div(style={"display": "flex", "justifyContent": "space-between"}, children=[
                                    html.Span("Network Latency", style={"fontSize": "0.8rem", "fontWeight": "500"}),
                                    html.Span("24ms", style={"fontSize": "0.8rem", "fontWeight": "600"})
                                ])
                            ])
                        ]
                    ),
                    
                    # Chart Card
                    html.Div(className="card", children=[
                        html.H4("Lưu lượng phương tiện theo giờ", style={"margin": "0 0 1rem 0", "fontSize": "1.1rem"}),
                        dcc.Graph(figure=fig, config={'displayModeBar': False})
                    ])
                ]
            ),
            
            # Right Column
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "1.5rem"},
                children=[
                    # Classification Card
                    html.Div(className="card", children=[
                        html.H4("Phân loại phương tiện", style={"margin": "0 0 1.5rem 0", "fontSize": "1.1rem"}),
                        html.Div(style={"display": "flex", "alignItems": "center", "gap": "20px"}, children=[
                            dcc.Graph(figure=donut_fig, config={'displayModeBar': False}),
                            html.Div(style={"flex": 1, "display": "flex", "flexDirection": "column", "gap": "10px"}, children=[
                                html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, children=[
                                    html.Div([html.Span(style={"width": "8px", "height": "8px", "backgroundColor": "#3b82f6", "display": "inline-block", "marginRight": "8px", "borderRadius": "2px"}), "Xe máy"]),
                                    html.Span("55%", style={"fontWeight": "600"})
                                ]),
                                html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, children=[
                                    html.Div([html.Span(style={"width": "8px", "height": "8px", "backgroundColor": "#9ca3af", "display": "inline-block", "marginRight": "8px", "borderRadius": "2px"}), "Ô tô con"]),
                                    html.Span("30%", style={"fontWeight": "600"})
                                ]),
                                html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, children=[
                                    html.Div([html.Span(style={"width": "8px", "height": "8px", "backgroundColor": "#ef4444", "display": "inline-block", "marginRight": "8px", "borderRadius": "2px"}), "Xe tải/Khách"]),
                                    html.Span("15%", style={"fontWeight": "600"})
                                ])
                            ])
                        ])
                    ]),
                    
                    # Reliability Card
                    html.Div(className="card", children=[
                        html.H4("Độ tin cậy trung bình", style={"margin": "0 0 1.5rem 0", "fontSize": "1.1rem"}),
                        html.Div(style={"display": "flex", "flexDirection": "column", "gap": "15px"}, children=[
                            html.Div([
                                html.Div(style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}, children=[
                                    html.Span("Nhận diện Biển số", style={"fontSize": "0.9rem"}),
                                    html.Span("98.5%", style={"fontSize": "0.9rem", "fontWeight": "600", "color": "var(--success-color)"})
                                ]),
                                html.Div(style={"height": "4px", "backgroundColor": "#f3f4f6", "borderRadius": "2px"}, children=[
                                    html.Div(style={"width": "98.5%", "height": "100%", "backgroundColor": "var(--success-color)", "borderRadius": "2px"})
                                ])
                            ]),
                            html.Div([
                                html.Div(style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}, children=[
                                    html.Span("Phân loại Dòng xe", style={"fontSize": "0.9rem"}),
                                    html.Span("95.2%", style={"fontSize": "0.9rem", "fontWeight": "600", "color": "var(--success-color)"})
                                ]),
                                html.Div(style={"height": "4px", "backgroundColor": "#f3f4f6", "borderRadius": "2px"}, children=[
                                    html.Div(style={"width": "95.2%", "height": "100%", "backgroundColor": "var(--success-color)", "borderRadius": "2px"})
                                ])
                            ]),
                            html.Div([
                                html.Div(style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}, children=[
                                    html.Span("Phát hiện Màu sắc", style={"fontSize": "0.9rem"}),
                                    html.Span("88.7%", style={"fontSize": "0.9rem", "fontWeight": "600", "color": "var(--primary-color)"})
                                ]),
                                html.Div(style={"height": "4px", "backgroundColor": "#f3f4f6", "borderRadius": "2px"}, children=[
                                    html.Div(style={"width": "88.7%", "height": "100%", "backgroundColor": "var(--primary-color)", "borderRadius": "2px"})
                                ])
                            ])
                        ])
                    ])
                ]
            )
        ]
    )
])
