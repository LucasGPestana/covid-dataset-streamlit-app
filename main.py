import streamlit as st
import streamlit.components.v1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

@st.cache_data
def createStateInfo(data, value_data):

  # Agrupa as datas em um objeto groupby (com esse id), e soma todos as mortes/casos desse dia. O mesmo ocorre para as cidades
  deaths_per_day = data[["date", value_data]].groupby("date").sum()
  deaths_per_cities = data[["name", value_data]].groupby("name").sum()

  # Descobre o valor máximo do Series de value_data ("deaths" ou "cases") e filtra em um DataFrame a instância que corresponde a esse valor máximo, resetando o index (linha)
  # Depois, pega o elemento da primeira linha e da primeira coluna desse novo DataFrame (Referente a data do tipo datetime) e converte para uma string no formato dd/mm/yyyy
  qtd_deaths_max = deaths_per_day.loc[:, value_data].max()
  day_with_more_deaths = deaths_per_day.loc[deaths_per_day.loc[:, value_data] == qtd_deaths_max].reset_index().iloc[0, 0].strftime("%d/%m/%Y")

  # O mesmo que o de cima, só que para valor mínimo
  qtd_deaths_min = deaths_per_day.loc[:, value_data].min()
  day_with_less_deaths = deaths_per_day.loc[deaths_per_day.loc[:, value_data] == qtd_deaths_min].reset_index().iloc[0, 0].strftime("%d/%m/%Y")

  # O mesmo que os dois acima, só que para o valor máximo da cidade
  qtd_deaths_max_city = deaths_per_cities.loc[:, value_data].max()
  city_with_more_deaths = deaths_per_cities.loc[deaths_per_cities.loc[:, value_data] == qtd_deaths_max_city].reset_index().iloc[0, 0]

  return [(day_with_more_deaths, qtd_deaths_max), (day_with_less_deaths, qtd_deaths_min), (city_with_more_deaths, qtd_deaths_max_city)]

@st.cache_data
def createGraphMonths(data, value_data):

  # Value_data pode ser deaths ou cases

  meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  meses_ano = dict()

  # Adiciona dentro do dicionário as abreviações dos meses (pegos da lista meses por meio do número inteiro do mês disponibilizado pelo atributo month de datetime) e o ano como valores, cujas chaves são suas representações númericas
  for date in data["date"]:
    meses_ano[f"{date.month}-{date.year}"] = f"{meses[date.month - 1]}. {date.year}"

  # Adiciona um Objeto Series month dentro do DataFrame filtrado, com os valores do dicionário meses_ano
  data["month"] = data["date"].apply(lambda x: meses_ano[f"{x.month}-{x.year}"])

  # Agrupa a soma de todas as mortes ou casos que um mês (de um ano) teve
  value_per_month = data.groupby("month")[value_data].sum()

  # Adiciona as porcentagens de mortes ou casos do total em uma lista
  porcentagens = [(value/value_per_month.sum()) * 100 for _, value in value_per_month.items()]

  # Gráfico de barras (Porcentagem x Mês e Ano)
  graph_value_per_month = px.bar(
    x=porcentagens,
    y=list(meses_ano.values()),
    orientation='h',
    labels={'x': "Porcentagem(%)", 'y': "Mês e Ano"}
  )

  return graph_value_per_month

@st.cache_data
def createGraphYears(data, value_data):

  # value_data pode representar deaths ou cases

  # Cria um Series year (ano) dentro do DataFrame filtrado
  data["year"] = data["date"].apply(lambda x: str(x.year))

  # Agrupa a soma de todos as mortes ou casos que houve em cada ano (id do GroupBy), em uma dada cidade
  value_per_year = data.groupby("year")[value_data].sum()

  # Gráfico em barra (Qtd. mortes/casos x Ano)
  graph_value_per_year = px.bar(data_frame=value_per_year, y=value_data)

  return graph_value_per_year

@st.cache_data
def createMap(data, text, scale):

  # A escala serve para trabalhar com tamanhos semelhantes, mesmo com uma alta diferença de valores entre mortes e casos

  # Coordenadas de cada estado (Para a adição do marcadores)
  coordinates = {
      'AC': (-8.77, -70.55),
      'AL': (-9.71, -35.73),
      'AM': (-3.47, -62.21),
      'AP': (1.41, -51.77),
      'BA': (-12.96, -38.51),
      'CE': (-3.71, -38.54),
      'DF': (-15.78, -47.93),
      'ES': (-19.19, -40.34),
      'GO': (-16.64, -49.31),
      'MA': (-2.55, -44.30),
      'MG': (-18.10, -44.38),
      'MS': (-20.51, -54.54),
      'MT': (-12.64, -55.42),
      'PA': (-5.53, -52.29),
      'PB': (-7.06, -35.55),
      'PE': (-8.28, -35.07),
      'PI': (-8.28, -43.68),
      'PR': (-24.89, -51.55),
      'RJ': (-22.84, -43.15),
      'RN': (-5.79, -36.51),
      'RO': (-11.22, -62.80),
      'RR': (1.99, -61.33),
      'RS': (-30.01, -51.22),
      'SC': (-27.33, -49.44),
      'SE': (-10.95, -37.07),
      'SP': (-23.55, -46.64),
      'TO': (-10.25, -48.25)
    }
  
  # Cria um gráfico template
  fig = go.Figure()

  # Percorre cada instância de DataFrameGroupBy
  for state, value in data.items():

    # Adiciona um novo gráfico (objeto Scattergeo) dentro do objeto Figure
    fig.add_trace(go.Scattergeo(
        name=state,
        locationmode="ISO-3",
        lat=[coordinates[state][0]],
        lon=[coordinates[state][1]],
        text=[f"{state}: {value} {text}"],
        mode="markers",
        marker={
          "size": value * scale,
          "opacity": 0.7,
          "reversescale": True,
          "autocolorscale": True,
          "symbol": "circle",
          "line": {
            "width": 1,
            "color": "rgb(102, 102, 102)"
          }
        }))
  
  # Atualiza o layout do gráfico template (Agora com o gráfico Scattergeo incluso)
  fig.update_layout(
      title=f"{text.capitalize()} de COVID-19 em Cada Estado",
      geo={
        "scope": "south america",
        "showland": True,
        "center": {
          "lon": -55,
          "lat": -12
        },
        "projection_scale": 4
      })
  
  return fig


@st.cache_data
def loadData(path, columns):

  # columns serve para que apenas algumas colunas sejam lidas do dataset e, assim, reduza a RAM utilizada

  try:

    data = pd.read_csv(filepath_or_buffer=path, sep=",", usecols=columns)
    return data
  
  except Exception as exc:

    st.error(f"Ocorreu um erro inesperado: {exc}")

def main():

  # Configurações da página Streamlit (page_icon recebe um objeto Image)
  st.set_page_config(page_title="Dashboard", page_icon=Image.open("images/icon.png"))

  with st.container():
    st.markdown("<h1 style='text-align: center'>Dashboard Sobre a COVID-19 no Brasil</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: justify'>Dados públicos relativo a COVID-19 nos estados e cidades brasileiras, entre 2020 e 2021. Caso queira verificar a fonte da base de dados, <a href='https://www.kaggle.com/datasets/unanimad/corona-virus-brazil?select=brazil_covid19_cities.csv'>Clique Aqui</a>.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: justify'>Do lado esquerdo, você pode verificar os dados relativo a um estado em específico. Assim que selecionar algum, será disponibilizado mais um campo para escolher a cidade desse estado que, uma vez escolhida, permite acessar os dados dela sobre a COVID-19.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: justify'>Abaixo, você pode observar o panorama geral do Brasil nesse contexto. Você pode voltar a essa página selecionando 'Nenhum' em estado, no lado esquerdo.</p>", unsafe_allow_html=True)

  data = loadData("files/brazil_covid19_cities.csv", ["name", "date", "state", "deaths", "cases"])

  # Configurações do Sidebar

  # Cor de fundo
  st.markdown("""
              <style>
                [data-testid=stSidebar] {
                      background-color: rgb(13, 33, 79);
                }
              </style>
              """, unsafe_allow_html=True)
  
  # Cabeçalho e imagem
  st.sidebar.header("Sistema Nexus")
  st.sidebar.image("images/rounded-logo.png", width=150)

  # Tratamento dos dados

  # Converte as strings em objetos datetime
  data["date"] = pd.to_datetime(data["date"])

  # Converte o tipo dos casos, antes real, para inteiro
  data["cases"] = pd.to_numeric(data["cases"], downcast="integer")


  # Criação de uma caixa de seleção com todos os estados
  # Quando a opção "Nenhum" é acionada, um contexto mais geral é mostrado (O mesmo serve para o selectbox de cidade)
  opcoes_estado = ["Nenhum"]
  opcoes_estado.extend(list(data["state"].unique()))
  estado_escolhido = st.sidebar.selectbox(label="Estado", options=opcoes_estado)


  if estado_escolhido == "Nenhum":

    st.warning("Ajuste o zoom do mapa manualmente, conforme necesssário, usando os botões do canto superior do mapa!")

    with st.spinner("Carregando dados..."):
      cases_per_state = data.groupby("state")["cases"].sum()

      fig = createMap(cases_per_state, "casos", 0.0000001)
      st.plotly_chart(fig)

    st.write("---")

    with st.spinner("Carregando dados..."):
      deaths_per_state = data.groupby("state")["deaths"].sum()

      fig2 = createMap(deaths_per_state, "mortes", 0.000005)
      st.plotly_chart(fig2)

  else:

    # Filtra todas as instâncias do DataFrame que tem o estado escolhido como valor da coluna "state"
    data_filtered = data[data["state"] == estado_escolhido]

    with st.spinner("Carregando dados..."):
      
      # Gráfico de Área (Qtd. Mortes x Data), com legenda das cidades do estado
      deaths_per_cities = px.area(data_frame=data_filtered, 
                                  x="date", 
                                  y="deaths", 
                                  color="name", 
                                  title=f"Quantidade de mortes por cidade em {estado_escolhido}")
      st.plotly_chart(deaths_per_cities)

      max_info_2, min_info_2, max_city_info_2 = createStateInfo(data_filtered, "deaths")

      # Informações sobre as mortes no estado
      st.write(f"## Dados de Mortes de {estado_escolhido}")
      st.write(f"Dia com maior número de mortes: {max_info_2[0]}")
      st.write(f"Quantidade de mortes do maior dia: {max_info_2[1]}")

      st.write("---")

      st.write(f"Dia com menor número de mortes: {min_info_2[0]}")
      st.write(f"Quantidade de mortes do menor dia: {min_info_2[1]}")

      st.write("---")

      st.write(f"Cidade com maior número de mortes: {max_city_info_2[0]}")
      st.write(f"Quantidade de mortes da cidade: {max_city_info_2[1]}")
    
    with st.spinner("Carregando dados..."):
      
      # Gráfico de Área (Qtd. Casos x Data), com legenda das cidades do estado
      cases_per_cities = px.area(data_frame=data_filtered, 
                                 x="date", 
                                 y="cases", 
                                 color="name", 
                                 title=f"Quantidade de casos por cidade em {estado_escolhido}")
      st.plotly_chart(cases_per_cities)

      max_info, min_info, max_city_info = createStateInfo(data_filtered, "cases")

      # Informações sobre os casos no estado
      st.write(f"## Dados de Casos de {estado_escolhido}")
      st.write(f"Dia com maior número de casos: {max_info[0]}")
      st.write(f"Quantidade de casos do maior dia: {max_info[1]}")

      st.write("---")

      st.write(f"Dia com menor número de casos: {min_info[0]}")
      st.write(f"Quantidade de casos do menor dia: {min_info[1]}")

      st.write("---")

      st.write(f"Cidade com maior número de casos: {max_city_info[0]}")
      st.write(f"Quantidade de casos da cidade: {max_city_info[1]}")

    # Selectbox que aparece apenas quando o estado escolhido não for "Nenhum"
    opcoes_cidade = ["Nenhum"]
    opcoes_cidade.extend(list(data_filtered["name"].unique()))
    cidade_escolhida = st.sidebar.selectbox(label="Cidade", options=opcoes_cidade)

    if cidade_escolhida == "Nenhum":

      # Continua mostrando apenas as informações do estado
      pass

    else:

      # Faz a rolagem da página aos gráficos correspondentes a cidade
      with open("src/main.js", "r") as file:
        streamlit.components.v1.html(html=f"<script>{file.read()}</script>")

      # Adiciona às informações do estado informações sobre a cidade escolhida
      st.write("---")

      # Filtra todas as instâncias do DataFrame filtrado de estados que possuem a cidade escolhida como valor da coluna name (nome da cidade)
      data_filtered_city = data_filtered[data_filtered["name"] == cidade_escolhida]

      # Renderização do gráfico Qtd. Mortes x Ano
      with st.spinner("Carregando dados..."):
        st.write(f"## Quantidade de Mortes de {cidade_escolhida} por Ano")
        graph = createGraphYears(data_filtered_city, "deaths")
        st.plotly_chart(graph)

      st.write("---")

      # Renderização do gráfico Qtd. Casos x Ano
      with st.spinner("Carregando dados..."):
        st.write(f"## Quantidade de Casos de {cidade_escolhida} por Ano")
        graph2 = createGraphYears(data_filtered_city, "cases")
        st.plotly_chart(graph2)
      
      st.write("---")

      # Renderização do gráfico Porcentagem Mortes x Mês e Ano
      with st.spinner("Carregando dados..."):
        st.write(f"## Porcentagem de Mortes de {cidade_escolhida} por Mês")
        graph3 = createGraphMonths(data_filtered_city, "deaths")
        st.plotly_chart(graph3)

      st.write("---")

      # Renderização do gráfico Porcentagem Casos x Mês e Ano
      with st.spinner("Carregando dados..."):
        st.write(f"## Porcentagem de Casos de {cidade_escolhida} por Mês")
        graph4 = createGraphMonths(data_filtered_city, "cases")
        st.plotly_chart(graph4)
  
  hide_st_style = """
                  <style>
                  #MainMenu {visibility: hidden;}
                  footer {visibility: hidden;}
                  header {visibility: hidden;}
                  </style>
                  """

  # Oculta o header e footer do Streamlit
  st.markdown(body=hide_st_style, unsafe_allow_html=True)

if __name__ == "__main__":
  main()
