import streamlit as st
import time
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.io as pio

if 'initial_df' not in st.session_state:
    st.session_state.initial_df = None
button_clicked = False

st.set_page_config(
    page_title="Scout",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def carregar_dados(summoner_name,start_time,end_time):
    #2023-10-05
    resultado=pd.read_pickle('Datageral.pkl')
    df=resultado.loc[(resultado['Nick']==summoner_name) & (resultado['Data']>=start_time) & (resultado['Data']<=end_time)]
    pdlgeral=pd.read_csv('pdlgeral.csv')
    pdlgeral = pdlgeral.loc[(pdlgeral['summoner_name'] == summoner_name)]

    return df, pdlgeral
# Function to store the DataFrame in session state
def store_dataframe(df):
    st.session_state.initial_df = df

# Function to retrieve the DataFrame from session state
def retrieve_dataframe():
    return st.session_state.initial_df

def heatmappsotion(df_total, side):
    resultado = df_total.loc[df_total['Side'] == side]
    resultado.loc[:, 'xgeral'] = resultado['xgeral'].apply(lambda lista: lista[:15])
    resultado.loc[:, 'ygeral'] = resultado['ygeral'].apply(lambda lista: lista[:15])

    x_geral = resultado['xgeral']
    y_geral = resultado['ygeral']

    x_geral = x_geral.explode().astype(float)
    y_geral = y_geral.explode().astype(float)
    data = pd.DataFrame({'xgeral': x_geral, 'ygeral': y_geral})

    # Crie uma figura do Matplotlib
    fig, ax = plt.subplots(facecolor='#0c1414')

    # Plote o mapa de densidade de kernel (KDE) na figura
    sns.kdeplot(data=data, x='xgeral', y='ygeral', cmap="RdPu", fill=True, thresh=0.3, levels=6, alpha=0.4,warn_singular=False, ax=ax)

    # Plote os pontos de dispersão no mesmo eixo
    ax.scatter(x_geral, y_geral, c='darkred', s=5)

    # Carregue e sobreponha a imagem de fundo
    background_image = plt.imread('map.png')
    rx0, ry0, rx1, ry1 = 0, 0, 14820, 14881
    ax.imshow(background_image, aspect='auto', extent=[rx0, rx1, ry0, ry1], zorder=-1)

    ax.set_axis_off()
    ax.set_frame_on(False)

    # Defina os limites do gráfico
    ax.set_xlim(rx0, rx1)
    ax.set_ylim(ry0, ry1)


    # Retorna a figura
    return fig

def tempofirstward(df):
    df['wardtime'] = df['wardtime'].apply(lambda x: x if (x is not None and len(x) > 0) else None)
    df = df.dropna(subset=['wardtime'])
    media_primeiro_elemento  = df['wardtime'].apply(lambda x: x[0])
    media_primeiro_elemento=media_primeiro_elemento.mean()
    minuto=(media_primeiro_elemento/1000)//60
    segundo=(media_primeiro_elemento/1000)%60
    tempofirstward=f'{int(minuto)}:{int(segundo)}'
    return tempofirstward

def plot_stat_diff(df, tempo, stat_name,separacao):
    if separacao=='Dias':
        if tempo == 8:
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
        summoner_name = st.selectbox("Nick:", ['Picknn','Namiru','Maxmüs','Krastyel1','xoska', 'Titeito', 'Qats', 'lolo', 'Aithusa', 'Zayco'])
        summoner_name = summoner_name.lower()
        data_atual = datetime.now()


        data_inicial=datetime(2023,10,21)
        year_range = st.slider(label="Selecione uma Data:", min_value=data_inicial, max_value=data_atual, value=[data_inicial,data_atual])
        data_inicial = str(data_inicial).split(' ')
        data_inicial = data_inicial[0]
        data_atual=str(data_atual).split(' ')
        data_atual = data_atual[0]
        tempo1=8
        tempo2=15

        partidas = st.selectbox("Partidas:", [":", "15", "10", "5", "1"])
        separacao = st.selectbox("Separação dos dados:", ["Dias", "Partidas"])
        divisao = st.selectbox("Champs com maior:", ["Win Rate", "Numero de Jogos"])

        if st.button("Buscar Partidas",type="primary"):
                button_clicked = True
                geral = carregar_dados(summoner_name,data_inicial,data_atual)
                df_total=geral[0]
                pdl=geral[1]
                st.subheader(f'Total de partidas: {len(df_total)}')

                df = df_total
                if partidas == ":":
                    df = df_total
                else:
                    df = df_total[:int(partidas)]
                store_dataframe(df)



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

# Retrieve the DataFrame from session state
df = retrieve_dataframe()



try:
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
                                st.markdown(f'''Cs diff aos 8: :green[+{cs_med}]''')
                            else:
                                st.markdown(f'''Cs diff aos 8: :red[{cs_med}]''')

                    with col2:
                        xp_med = round(df[f'xpdiff@{tempo1}'].mean(), 1)
                        if xp_med > 0:
                            st.markdown(f'''XP diff aos 8: :green[+{xp_med}]''')
                        else:
                            st.markdown(f'''XP diff aos 8: :red[{xp_med}]''')

                    with col3:
                        gold_med = round(df[f'golddiff@{tempo1}'].mean(), 1)
                        if gold_med > 0:
                            st.markdown(f'''Gold diff aos 8: :green[+{gold_med}]''')
                        else:
                            st.markdown(f'''Gold diff aos 8: :red[{gold_med}]''')

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
                        plot_stat_diff(df, 8, 'jgdiff',separacao)
                    else:
                        st.subheader("CS diff médio ")
                        plot_stat_diff(df, 8, 'csdiff',separacao)
                    st.subheader("Gold diff médio")
                    plot_stat_diff(df, 8, 'golddiff',separacao)
                with col2:
                    st.subheader("Xp diff médio")
                    plot_stat_diff(df, 8, 'xpdiff',separacao)
                    st.subheader("Dano diff médio")
                    plot_stat_diff(df, 8, 'danodiff',separacao)

    with tab2:
        col1, col2 ,col3, col4= st.columns(4)
        if 'df' in locals():
            with st.container():
                if str(df.iloc[0,:]['position'])=='MIDDLE':
                    Cspmcomp=9.00
                    DPMcomp=950.23
                    tempofirstwardcomp=str('2:26')
                    VisionScorepmcomp=1.3
                    pinkcomp=0.11
                    wardsplacedcomp=0.5
                    wardskiledcomp=0.4
                    percentdanocomp='28%'
                    Goldpmcomp=497.37
                    dragonskillcomp = ''
                elif str(df.iloc[0,:]['position'])=='BOTTOM':
                    Cspmcomp = 8.51
                    DPMcomp = 880.0
                    tempofirstwardcomp = str('2:52')
                    VisionScorepmcomp = 1.2
                    pinkcomp = 0.11
                    wardsplacedcomp = 0.5
                    wardskiledcomp = 0.3
                    percentdanocomp = '27%'
                    Goldpmcomp = 520.95
                    dragonskillcomp = ''
                elif str(df.iloc[0,:]['position'])=='JUNGLE':
                    Cspmcomp = 6.03
                    DPMcomp = 739.6
                    tempofirstwardcomp = str('2:56')
                    VisionScorepmcomp = 1.32
                    pinkcomp = 0.25
                    wardsplacedcomp = 0.5
                    wardskiledcomp = 0.30
                    percentdanocomp = '23%'
                    Goldpmcomp = 469.76
                    dragonskillcomp=2.3
                elif str(df.iloc[0,:]['position'])=='TOP':
                    Cspmcomp = 7.45
                    DPMcomp = 766.71
                    tempofirstwardcomp = str('3:01')
                    VisionScorepmcomp = 0.86
                    pinkcomp = 0.14
                    wardsplacedcomp = 0.44
                    wardskiledcomp = 0.10
                    percentdanocomp = '24%'
                    Goldpmcomp = 449.07
                    dragonskillcomp=''

                elif str(df.iloc[0,:]['position'])=='UTILITY':
                    Cspmcomp = ''
                    DPMcomp = ''
                    tempofirstwardcomp = str('2:40')
                    VisionScorepmcomp = 3.01
                    pinkcomp = 0.3
                    wardsplacedcomp = 1.38
                    wardskiledcomp = 0.5
                    percentdanocomp = ''
                    Goldpmcomp = 310.85
                    dragonskillcomp = ''

                # Calcula a média de cada métrica
                df[['minutos', 'segundos']] = df['tempo_total'].str.split(':', expand=True).astype(int)
                df['wardspm']=df['wardsPlaced']/df['minutos']
                df['wardsdestruidaspm'] = df['wardsKilled'] / df['minutos']
                df['detectorwardsdestruidaspm']=df['detectorWardsPlaced']/ df['minutos']
                mean_teamDamagePercentage = df['teamDamagePercentage'].mean()
                mean_visionScoreAdvantageLaneOpponent = round(df['visionScoreAdvantageLaneOpponent'].mean(), 2)
                mean_visionScorePerMinute = round(df['visionScorePerMinute'].mean(), 2)
                mean_detectorWardsPlacedpm = round(df['detectorwardsdestruidaspm'].mean(), 2)
                mean_detectorWardsPlaced = round(df['detectorWardsPlaced'].mean(), 2)

                mean_wardTakedownsBefore20M = round(df['wardTakedownsBefore20M'].mean(), 1)
                mean_wardTakedowns = round(df['wardTakedowns'].mean(), 1)

                mean_firstBloodKill =df['firstBloodKill'].sum()
                mean_firstBloodAssist = df['firstBloodAssist'].sum()
                totaljogos=int(len(df['firstBloodKill']))
                mean_fbpart=int(mean_firstBloodKill+mean_firstBloodAssist)/totaljogos
                mean_kda = round(df['kda'].mean(), 1)
                mean_turretPlatesTaken = round(df['turretPlatesTaken'].mean(), 1)
                mean_dragonKills = round(df['dragonKills'].mean(), 1)
                mean_wardsKilled = round(df['wardsdestruidaspm'].mean(), 2)
                mean_wardsPlacedpm = round(df['wardspm'].mean(), 2)
                mean_wardsPlaced=round(df['wardsPlaced'].mean(), 2)
                dpm=round(df['Dpm'].mean(),2)
                gold15rend=round(df['gold15rend'].mean(),2)
                goldpm=round(df['goldpm'].mean(),2)
                danoporgold=round(df['danoporgold'].mean(),2)
                victimfb=round(df['fbvitima'].mean(),2)

                # Exibe os resultados


                with col1:
                    st.subheader('Visão')
                    st.write(f'VisionScorepm: {mean_visionScorePerMinute}({VisionScorepmcomp})')
                    st.write(f'VisionScore diff: {mean_visionScoreAdvantageLaneOpponent}')
                    st.write(f'Sentinela Detectora colocada por minuto: {mean_detectorWardsPlacedpm}({pinkcomp}) - Pinks colocados {mean_detectorWardsPlaced}')
                    st.write(f'Ward destruidas antes dos 20m: {mean_wardTakedownsBefore20M}')
                    st.write(f'Wards Destruidas por minuto: {mean_wardsKilled}({wardskiledcomp })')
                    st.write(f'Wards colocadas por minuto: {mean_wardsPlacedpm}({wardsplacedcomp}) - Wards colocados {mean_wardsPlaced} ')
                    st.write(f'O tempo médio da primeira ward: {tempofirstward(df)}({tempofirstwardcomp })')

                with col2:
                    st.subheader('Objetivos')
                    st.write(f'Média de dragonKills: {mean_dragonKills}({dragonskillcomp })')
                    st.write(f'Média de Plates: {mean_turretPlatesTaken}')
                    st.write(f'Gold efetivo aos 15: {gold15rend}')
                    st.write(f'Goldpm: {goldpm}({Goldpmcomp})')


                with col3:
                    st.subheader('Combate')
                    role = (df.iloc[0, :])
                    if role['position'] == 'JUNGLE':
                        st.write(f'Cspm: {round(df["cspmjg"].mean(),2)}({Cspmcomp})')
                    else:
                        st.write(f'Cspm: {round(df["cspm"].mean(), 2)}({Cspmcomp})')
                    st.write(f'Porcentagem de Dano do time: {round(mean_teamDamagePercentage*100,1)}%({percentdanocomp })')
                    st.write(f'Participação em FB: {round((mean_fbpart)*100,1)}%')
                    st.write(f'Vitima de FB: {round((victimfb) * 100, 1)}%')
                    st.write(f'KDA: {mean_kda}')
                    st.write(f'DPM:{dpm}({DPMcomp})')
                    st.write(f'Dano por gold: {danoporgold}')

                    with col4:

                        st.subheader('Champions Win rate')

                        win_loss_counts = df.groupby('champion')['win'].value_counts().unstack(fill_value=0)

                        # Calcular a win rate para cada campeão
                        if divisao == "Win Rate":
                            win_rate = (win_loss_counts[1] / (win_loss_counts[0] + win_loss_counts[1])) * 100
                        else:
                            win_rate = ((win_loss_counts[1] + win_loss_counts[0])) * 100

                        # Classificar os campeões pela win rate em ordem decrescente
                        sorted_win_rate = win_rate.sort_values(ascending=False)

                        # Selecionar os 3 melhores campeões com win rate mais alta
                        top_3_champions = sorted_win_rate.head(3)

                        # Imprimir os 3 melhores campeões com suas win rates, vitórias e derrotas
                        i = 0
                        for champion in top_3_champions.items():
                            champion = champion[0]
                            gold = df.loc[df['champion'] == champion]
                            average_gold_diff6 = gold['golddiff@8'].mean()
                            average_gold_diff15 = gold['golddiff@15'].mean()
                            wins = win_loss_counts.loc[champion, 1]
                            losses = win_loss_counts.loc[champion, 0]
                            win_rate1 = (wins / (wins + losses)) * 100
                            if win_rate1 > 50:
                                color = 'green'
                            else:
                                color = 'red'
                            if average_gold_diff6 > 0:
                                color1 = 'green'
                                mais = '+'
                            else:
                                color1 = 'red'
                                mais = ''
                            st.markdown(
                                f"Campeão: {champion} - Win Rate: :{color}[{win_rate1:.2f}%] - Vitórias: {wins} -Derrotas: {losses} - Gold diff @8: :{color1}[{mais}{average_gold_diff6:.2f}]")
                            i += 1
                        pool = df['champion'].unique().tolist()
                        st.subheader('Pool')
                        for i in pool:
                            st.write(i)
            with st.container():
                col1, col2, col3 = st.columns(3)
                if partidas != '1':
                    if 'df' in locals():
                        with col2:
                            st.subheader('Heatmap de Posição até os 15')
                            side=st.selectbox("Side:", ["Blue", "Red"])
                            side=side.lower()
                            plot=heatmappsotion(df,side)
                            st.pyplot(plot,use_container_width=True)
except Exception as e:
    st.subheader('Esperando Dados...')
    print(f"Erro na função process_data(): {str(e)}")



