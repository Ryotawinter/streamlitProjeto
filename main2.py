import streamlit as st
import time
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.io as pio


st.set_page_config(
    page_title="Projeto Medina",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def carregar_dados(summoner_name,start_time,end_time):
    #2023-10-05
    resultado=pd.read_csv('Datageral.csv')
    df=resultado.loc[(resultado['Nick']==summoner_name) & (resultado['Data']>=start_time) & (resultado['Data']<=end_time)]
    pdlgeral=pd.read_csv('pdlgeral.csv')
    pdlgeral = pdlgeral.loc[(pdlgeral['summoner_name'] == summoner_name)]

    return df, pdlgeral

def plot_stat_diff(df, tempo, stat_name,separacao):
    if separacao=='Dias':
        if tempo == 5:
            stat_mean = df.groupby('Data')[f'{stat_name}@{tempo}'].mean()
            stat_mean1 = df.groupby('Data')[f'{stat_name}@15'].mean()
            result_df = pd.merge(stat_mean, stat_mean1, on='Data', how='inner')
            st.bar_chart(result_df,color=['#48D1CC','#90EE90'])

    else:
            result_df = df[[f'{stat_name}@{tempo}',f'{stat_name}@15']]

            st.bar_chart(result_df, color=['#48D1CC', '#90EE90'])



with st.sidebar:
    with st.container():
        st.title('Estatisticas Soloq')
        # Coletando parâmetros do usuário
        summoner_name = st.text_input("Nome do Summoner")
        summoner_name=summoner_name.lower()
        data_atual = datetime.now()
        #data_atual=str(data_atual).split(' ')
        #data_atual=data_atual[0]
        #data_inicial='2023-09-01'
        data_inicial=datetime(2023,9,1)
        year_range = st.slider(label="Selecione uma Data:", min_value=data_inicial, max_value=data_atual, value=[data_inicial,data_atual])
        data_inicial = str(data_inicial).split(' ')
        data_inicial = data_inicial[0]
        data_atual=str(data_atual).split(' ')
        data_atual = data_atual[0]
        tempo1=5
        tempo2=15

        partidas = st.selectbox("Partidas:", [":", "15", "10", "5", "1"])
        separacao = st.selectbox("Separação dos dados:", ["Dias", "Partidas"])
        divisao = st.selectbox("Champs com maior:", ["Win Rate", "Numero de Jogos"])

        if st.button("Buscar Partidas"):
                geral = carregar_dados(summoner_name,data_inicial,data_atual)
                df_total=geral[0]
                pdl=geral[1]
                st.subheader(f'Total de partidas: {len(df_total)}')
                df = df_total
                if partidas == ":":
                    df = df_total
                else:
                    df = df_total[:int(partidas)]
    with st.container():
        if 'df' in locals():
            winrate = ((pdl["wins"]) / (pdl["wins"] + pdl["losses"])) * 100
            a = pdl[["wins", 'losses']]
            cores = {'wins': '#48D1CC', 'losses': '#90EE90'}
            pio.templates.default = "plotly"
            fig_kind = px.pie(a, names=a.columns, values=a.values[0], color=['#48D1CC', '#90EE90'],
                              title=f'Soloq - Win Rate em {a.values[0].sum()} partidas')
            st.plotly_chart(fig_kind, use_container_width=True)
            st.write(f'Tier: {pdl["tier"].iloc[0]} {pdl["rank"].iloc[0]} - PDL: {pdl["leaguePoints"].iloc[0]}')


tab1, tab2 = st.tabs(["Early Game", "Total"])

with tab1:
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        if 'df' in locals():
            role=(df.iloc[0,:])
            if role['position'] == 'JUNGLE':
                with col1:
                    cs_med = round(df['jgdiff@15'].mean(), 1)
                    if cs_med > 0:
                        st.markdown(f'''Cs diff aos 15: :green[+{cs_med}]''')
                    else:
                        st.markdown(f'''Cs diff aos 15: :red[{cs_med}]''')
            else:
                with col1:
                    cs_med = round(df['csdiff@15'].mean(), 1)
                    if cs_med > 0:
                        st.markdown(f'''Cs diff aos 15: :green[+{cs_med}]''')
                    else:
                        st.markdown(f'''Cs diff aos 15: :red[{cs_med}]''')

            with col2:
                xp_med = round(df['xpdiff@15'].mean(), 1)
                if xp_med > 0:
                    st.markdown(f'''XP diff aos 15: :green[+{xp_med}]''')
                else:
                    st.markdown(f'''XP diff aos 15: :red[{xp_med}]''')

            with col3:
                gold_med = round(df['golddiff@15'].mean(), 1)
                if gold_med > 0:
                    st.markdown(f'''Gold diff aos 15: :green[+{gold_med}]''')
                else:
                    st.markdown(f'''Gold diff aos 15: :red[{gold_med}]''')

            with col4:
                danodiff_med = round(df[f'danodiff@{tempo2}'].mean(), 1)
                if danodiff_med > 0:
                    st.markdown(f'''Dano diff aos {tempo2}: :green[+{danodiff_med}]''')
                else:
                    st.markdown(f'''Dano diff aos {tempo2}: :red[{danodiff_med}]''')
            with col5:
                maxCsdiff = round(df['maxCsAdvantageOnLaneOpponent'].mean(), 1)
                st.markdown(f'''Maior vantagem de cs: :green[{maxCsdiff}]''')


        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            if 'df' in locals():
                role = (df.iloc[0, :])
                if role['position'] == 'JUNGLE':
                    with col1:
                        cs_med = round(df[f'jgdiff@{tempo1}'].mean(), 1)
                        if cs_med > 0:
                            st.markdown(f'''Cs diff aos 5: :green[+{cs_med}]''')
                        else:
                            st.markdown(f'''Cs diff aos 5: :red[{cs_med}]''')
                else:
                    with col1:
                        cs_med = round(df[f'csdiff@{tempo1}'].mean(), 1)
                        if cs_med > 0:
                            st.markdown(f'''Cs diff aos 5: :green[+{cs_med}]''')
                        else:
                            st.markdown(f'''Cs diff aos 5: :red[{cs_med}]''')

                with col2:
                    xp_med = round(df[f'xpdiff@{tempo1}'].mean(), 1)
                    if xp_med > 0:
                        st.markdown(f'''XP diff aos 5: :green[+{xp_med}]''')
                    else:
                        st.markdown(f'''XP diff aos 5: :red[{xp_med}]''')

                with col3:
                    gold_med = round(df[f'golddiff@{tempo1}'].mean(), 1)
                    if gold_med > 0:
                        st.markdown(f'''Gold diff aos 5: :green[+{gold_med}]''')
                    else:
                        st.markdown(f'''Gold diff aos 5: :red[{gold_med}]''')

                with col4:
                    danodiff_med = round(df[f'danodiff@{tempo1}'].mean(), 1)
                    if danodiff_med > 0:
                        st.markdown(f'''Dano diff aos {tempo1}: :green[+{danodiff_med}]''')
                    else:
                        st.markdown(f'''Dano diff aos {tempo1}: :red[{danodiff_med}]''')
                with col5:
                    danodiff_med3 = round(df[f'danodiff@3'].mean(), 1)
                    if danodiff_med3 > 0:
                        st.markdown(f'''Dano diff aos 3: :green[+{danodiff_med3}]''')
                    else:
                        st.markdown(f'''Dano diff aos 3: :red[{danodiff_med3}]''')
        st.write('---')


    with st.container():
        col1, col2 = st.columns(2)
        if 'df' in locals():
            with col1:
                role = (df.iloc[0, :])
                if role['position'] == 'JUNGLE':
                    st.subheader("CS jg diff médio ")
                    plot_stat_diff(df, 5, 'jgdiff',separacao)
                else:
                    st.subheader("CS diff médio ")
                    plot_stat_diff(df, 5, 'csdiff',separacao)
                st.subheader("Gold diff médio")
                plot_stat_diff(df, 5, 'golddiff',separacao)
            with col2:
                st.subheader("Xp diff médio")
                plot_stat_diff(df, 5, 'xpdiff',separacao)
                st.subheader("Dano diff médio")
                plot_stat_diff(df, 5, 'danodiff',separacao)

with tab2:
    col1, col2 ,col3= st.columns(3)
    if 'df' in locals():
        with st.container():
            # Calcula a média de cada métrica
            mean_teamDamagePercentage = df['teamDamagePercentage'].mean()
            mean_visionScoreAdvantageLaneOpponent = round(df['visionScoreAdvantageLaneOpponent'].mean(), 1)
            mean_visionScorePerMinute = round(df['visionScorePerMinute'].mean(), 1)
            mean_detectorWardsPlaced = round(df['detectorWardsPlaced'].mean(), 1)
            mean_wardTakedownsBefore20M = round(df['wardTakedownsBefore20M'].mean(), 1)
            mean_wardTakedowns = round(df['wardTakedowns'].mean(), 1)

            mean_firstBloodKill =df['firstBloodKill'].sum()
            mean_firstBloodAssist = df['firstBloodAssist'].sum()
            totaljogos=int(len(df['firstBloodKill']))
            mean_fbpart=int(mean_firstBloodKill+mean_firstBloodAssist)/totaljogos
            mean_kda = round(df['kda'].mean(), 1)
            mean_turretPlatesTaken = round(df['turretPlatesTaken'].mean(), 1)
            mean_dragonKills = round(df['dragonKills'].mean(), 1)
            mean_wardsKilled = round(df['wardsKilled'].mean(), 1)
            mean_wardsPlaced = round(df['wardsPlaced'].mean(), 1)
            dpm=round(df['Dpm'].mean(),2)
            gold15rend=round(df['gold15rend'].mean(),2)
            goldpm=round(df['goldpm'].mean(),2)
            danoporgold=round(df['danoporgold'].mean(),2)

            # Exibe os resultados


            with col1:
                st.subheader('Visão')
                st.write(f'VisionScorepm: {mean_visionScorePerMinute}')
                st.write(f'VisionScore diff: {mean_visionScoreAdvantageLaneOpponent}')
                st.write(f'Sentinela Detectora colocada: {mean_detectorWardsPlaced}')
                st.write(f'Ward destruidas antes dos 20m: {mean_wardTakedownsBefore20M}')
                st.write(f'Wards Destruidas: {mean_wardsKilled}')
                st.write(f'Wards colocadas: {mean_wardsPlaced}')
            with col2:
                st.subheader('Objetivos')
                st.write(f'Média de dragonKills: {mean_dragonKills}')
                st.write(f'Média de turretPlatesTaken: {mean_turretPlatesTaken}')
                st.write(f'Gold efetivo aos 15: {gold15rend}')
                st.write(f'Goldpm: {goldpm}')


            with col3:
                st.subheader('Combate')
                role = (df.iloc[0, :])
                if role['position'] == 'JUNGLE':
                    st.write(f'Cspm: {round(df["cspmjg"].mean(),2)}')
                else:
                    st.write(f'Cspm: {round(df["cspm"].mean(), 2)}')
                st.write(f'Porcentagem de Dano do time: {round(mean_teamDamagePercentage*100,1)}%')
                st.write(f'Participação em FB: {round((mean_fbpart)*100,1)}%')
                st.write(f'KDA: {mean_kda}')
                st.write(f'DPM:{dpm}')
                st.write(f'Dano por gold: {danoporgold}')
        with st.container():
            if partidas != 1:
                if 'df' in locals():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.subheader('Soloq')

                    with col2:

                        st.subheader('Champions Win rate')

                        win_loss_counts = df.groupby('champion')['win'].value_counts().unstack(fill_value=0)

                        # Calcular a win rate para cada campeão
                        if divisao=="Win Rate":
                            win_rate = (win_loss_counts[1] / (win_loss_counts[0] + win_loss_counts[1])) * 100
                        else :
                            win_rate = ((win_loss_counts[1] + win_loss_counts[0])) * 100

                        # Classificar os campeões pela win rate em ordem decrescente
                        sorted_win_rate = win_rate.sort_values(ascending=False)

                        # Selecionar os 3 melhores campeões com win rate mais alta
                        top_3_champions = sorted_win_rate.head(3)

                        # Imprimir os 3 melhores campeões com suas win rates, vitórias e derrotas
                        i=0
                        for champion in top_3_champions.items():
                            champion=champion[0]
                            gold=df.loc[df['champion']==champion]
                            average_gold_diff6 = gold['golddiff@5'].mean()
                            average_gold_diff15 = gold['golddiff@15'].mean()
                            wins = win_loss_counts.loc[champion, 1]
                            losses = win_loss_counts.loc[champion, 0]
                            win_rate1 = (wins / (wins + losses)) * 100
                            if win_rate1>50:
                                color='green'
                            else:
                                color='red'
                            if average_gold_diff6>0:
                                color1='green'
                                mais='+'
                            else:
                                color1='red'
                                mais=''
                            st.markdown(f"Campeão: {champion} - Win Rate: :{color}[{win_rate1:.2f}%] - Vitórias: {wins} -Derrotas: {losses} - Gold diff @5: :{color1}[{mais}{average_gold_diff6:.2f}]")
                            i+=1



