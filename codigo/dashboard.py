import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc,Input, Output, Dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO

df=pd.read_csv("codigo/Base_DashBoard.csv")

tabcard={"height": "100%"}
config_graph={"displayModeBar": False, "showTips":False}


#temas
url_themes1=dbc.themes.QUARTZ
url_themes2=dbc.themes.CYBORG

#dropdowns

paises = ['Todas'] + df["country_noc"].unique().tolist()
ediçoes=df["edition"].unique()

app=Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([
    dbc.Row([
        # Sidebar
        dbc.Col([
            dbc.Row(html.H1("Olimpíadas")),
            dbc.Row(html.H2("1908-2022")),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H3("Temas")
                ]),
                dbc.Col([
                    ThemeSwitchAIO(aio_id="themes", themes=[url_themes1, url_themes2])
                ])
            ]),
            html.Br(),
            html.H3("Paises"),
            dcc.Dropdown(id="paises", style={"color": "black"}),
            html.Br(),
            html.H3("Edições"),
            dcc.Dropdown(ediçoes, id="edições", value="2022 Winter Olympics", style={"color": "black"})
        ], align="center", md=3, style={"height": "100vh", "overflow-y": "auto"}),

        # Graficos
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Graph(id="medalhaPorPais", className="dbc")
                        )
                    ])
                ],md=8, style={"flex": "1 1 auto"}),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Graph(id="desempenhoPorAtleta", className="dbc")
                        )
                    ])
                ], md=4, style={"flex": "1 1 auto"})

            ], className="g-2 my-auto", style={"flex": "1 1 auto", "margin-top": "7px"}),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Graph(id="quantidadeMEdalhas", className="dbc")
                        )
                    ])
                ], md=6, style={"flex": "1 1 auto"}),  # flex permite que o tamanho se ajuste dinamicamente
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Graph(id="desempenhoPorSexo", className="dbc")
                        )
                    ])
                ], md=6, style={"flex": "1 1 auto"})
            ], className="g-2 my-auto", style={"margin-top": "7px"}),
            dbc.Row([
                dbc.Card([
                    dbc.CardBody(
                        dcc.Graph(id="desempenhoPorEsporte", className="dbc")
                    )
                ])
            ], className="g-2 my-auto", style={"flex": "1 1 auto", "margin-top": "7px"})
        ], align="center", md=9, style={"height": "100vh", "display": "flex", "flex-direction": "column", "overflow-y": "auto"})
    ])
], fluid=True, style={"height": "100vh"})


@app.callback(
Output("paises","options"),
Input("edições", "value")
)
def updateOptionsDrop(edicoes):
    edicoes=df.loc[(df["edition"]==edicoes) & (df["medalPoint"]>0)]
    pais = ['Todas'] + edicoes["country_noc"].unique().tolist()
    return [{"label":i, "value": i} for i in pais]

@app.callback(
Output("paises","value"),
Input("paises", "options")
)
def updateFirstValue(paises):
    return [c["value"] for c in paises][1]

@app.callback(
    [Output("medalhaPorPais", "figure"),
    Output("desempenhoPorAtleta", "figure")],
    [Input("paises", "value"),
    Input("edições", "value"),
    Input(ThemeSwitchAIO.ids.switch("themes"), "value")]
)
def updateFig1(paises, edicao, tema):
    if tema:
        template="quartz"
    else:
        template="cyborg"
    if paises =="Todas":
        dff1=df.dropna()
        paisMaisMedalha=dff1["country_noc"].value_counts().reset_index().head(10)
        figMaisMedalhas=px.bar(paisMaisMedalha, x="country_noc", y="count", title="Desempnho dos melhores paises com base nas medalhas", template=template)
    else:
        dff1=df.loc[df["edition"]==edicao]
        dff1=dff1.dropna()
        paisMaisMedalha=dff1["country_noc"].value_counts().reset_index().head(10)
        figMaisMedalhas=px.bar(paisMaisMedalha, x="country_noc", y="count", title=f"Desempenho de cada pais na {edicao}", template=template)
        
    if paises =="Todas":
        dfSemVazios=df.dropna()
        dff2=dfSemVazios[["athlete", "medalPoint"]]. groupby("athlete").sum().sort_values(by="medalPoint", ascending=False).reset_index().head(10)
        figMelhorAtleta=px.bar(dff2, x="medalPoint", y="athlete", orientation="h", title="Desempenho de cada atleta em todas as Olimíadas", template=template)
    else:
        dfSemVazios=df.dropna()
        dff=dfSemVazios.loc[(dfSemVazios["country_noc"]==paises) & (dfSemVazios["edition"]==edicao) & (dfSemVazios["medalPoint"]>0)]
        dff2=dff[["athlete", "medalPoint"]]. groupby("athlete"). sum().sort_values(by="medalPoint", ascending=False).reset_index().head(10)
        figMelhorAtleta=px.bar(dff2, x="medalPoint", y="athlete", orientation="h", title=f"Desempenho de cada atleta de {paises}", template=template)
    
    return figMaisMedalhas, figMelhorAtleta


@app.callback(
    [Output("quantidadeMEdalhas", "figure"),
    Output("desempenhoPorSexo", "figure")],
    [Input("paises", "value"),
    Input("edições", "value"),
    Input(ThemeSwitchAIO.ids.switch("themes"), "value")]
)
def updateFig3Fig4(paises, edicao, tema):
    if tema:
        template="quartz"
    else:
        template="cyborg"

    if paises =="Todas":
        dff1=df.dropna()
        desempenhoDeMedalhas=dff1["medal"].value_counts().reset_index()
        medalhaMaisFrequente=px.pie(desempenhoDeMedalhas, names="medal", values="count", title="Medalhas mais  frequêntes", template=template)
    else:
        dff1=df.loc[(df["edition"]==edicao) & (df["country_noc"]==paises)]
        dff1=dff1.dropna()
        desempenhoDeMedalhas=dff1["medal"].value_counts().reset_index()
        medalhaMaisFrequente=px.pie(desempenhoDeMedalhas, names="medal", values="count", title=f"Medalhas mais frequêntes na {paises} em {edicao}", template=template)
        
    if paises =="Todas":
        dfSemVazios=df.dropna()
        desempenhoSexo=dfSemVazios[["sexo", "medalPoint"]].groupby("sexo").sum().reset_index()
        sexoMelhorDesempenho=px.pie(desempenhoSexo, names="sexo", values="medalPoint",hole=.3 , title="Desempenho de cada sexo em todas as Olimíadas", template=template)
    else:
        dfSemVazios=df.loc[(df["country_noc"]==paises) & (df["edition"]==edicao)]
        dfSemVazios=dfSemVazios.dropna()
        desempenhoSexo=dfSemVazios[["sexo", "medalPoint"]].groupby("sexo").sum().reset_index()
        sexoMelhorDesempenho=px.pie(desempenhoSexo, names="sexo", values="medalPoint",hole=.3 , title=f"Desempenho de cada sexo de {paises} em {edicao}", template=template)
    return medalhaMaisFrequente, sexoMelhorDesempenho

@app.callback(
    Output("desempenhoPorEsporte", "figure"),
    [Input("paises", "value"),
    Input("edições", "value"),
    Input(ThemeSwitchAIO.ids.switch("themes"), "value")]
)
def updateFig5(paises, edicao, tema):
    if tema:
        template="quartz"
    else:
        template="cyborg"


    if paises =="Todas":
        dff1=df.dropna()
        desempenhoPorEsporte=dff1["sport"].value_counts().reset_index()
        esporteDestaque=px.bar(desempenhoPorEsporte, x="sport", y="count", title="Esporte que tem mais medalhas nas Olimpíadas", template=template)
    else:
        dff1=df.loc[(df["edition"]==edicao) & (df["country_noc"]==paises)]
        dff1=dff1.dropna()
        desempenhoPorEsporte=dff1["sport"].value_counts().reset_index()
        esporteDestaque=px.bar(desempenhoPorEsporte, x="sport", y="count", title=f"Esporte destaque de {paises} em {edicao}", template=template)
    return esporteDestaque
        


app.run_server(debug=True)
