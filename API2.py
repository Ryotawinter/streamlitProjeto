import time
import concurrent.futures
import pandas as pd
import requests
import datetime
from datetime import datetime

import pandas as pd
import requests


# The first function simply gets the puuid, given a summoner name and region
# This is exactly the same as our first example, except we're building the API URL from scratch
def rank(summoner_name, region, api_key):
    api_url = (
            "https://" +
            region +
            ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" +
            summoner_name +
            "?api_key=" +
            api_key
    )
    resp = requests.get(api_url)
    player_info = resp.json()
    id_info = player_info['id']

    api_url = (
            "https://" +
            region +
            ".api.riotgames.com/lol/league/v4/entries/by-summoner/" +
            id_info +
            "?api_key=" +
            api_key
    )
    resp = requests.get(api_url)
    player_info = resp.json()
    rank = player_info[0]
    if rank['queueType']!="RANKED_SOLO_5x5":
        rank = player_info[1]
    df = {'summoner_name': summoner_name.lower(),
          'tier': rank['tier'],
          'rank': rank['rank'],
          'wins': rank['wins'],
          'losses': rank['losses'],
          'leaguePoints': rank['leaguePoints'],
          'queueType': rank['queueType'],
          }
    df=pd.DataFrame([df])
    return df
def get_puuid(summoner_name, region, api_key):
    try:
        api_url = (
                "https://" +
                region +
                ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" +
                summoner_name+
                "?api_key=" +
                api_key
        )

        resp = requests.get(api_url)
        player_info = resp.json()
        puuid = player_info['puuid']
        print(puuid)
    except:
        print(f'Summoner não encontrado:{summoner_name}')
        puuid=0
    return puuid


# The function to get a list of all the match IDs (2nd example above) given a players puuid and mass region
# Updated function where you can set which queue to take data from

def get_match_ids(puuid, mass_region, queue_id, api_key, start_time):
    api_url = (
            "https://" +
            mass_region +
            ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
            puuid +
            "/ids?startTime=" +
            str(start_time) +
            "&endTime=1854414000" +
            "&queue=" +
            str(queue_id) +
            "&count=100" +
            "&api_key=" +
            api_key
    )

    resp = requests.get(api_url)
    match_ids = resp.json()
    return match_ids


# From a given match ID and mass region, get the data about the game
def get_match_data(match_id, mass_region, api_key):
    api_url = (
            "https://" +
            mass_region +
            ".api.riotgames.com/lol/match/v5/matches/" +
            match_id +
            "?api_key=" +
            api_key
    )

    # we need to add this "while" statement so that we continuously loop until it's successful
    while True:
        resp = requests.get(api_url)

        # whenever we see a 429, we sleep for 10 seconds and then restart from the top of the "while" loop
        if resp.status_code == 429:
            print("Rate Limit hit, sleeping for 10 seconds")
            time.sleep(60)
            # continue means start the loop again
            continue

        # if resp.status_code isn't 429, then we carry on to the end of the function and return the data
        match_data = resp.json()
        return match_data


def get_match_data_timeline(match_id, mass_region, api_key):
    api_url = (
            "https://" +
            mass_region +
            ".api.riotgames.com/lol/match/v5/matches/" +
            match_id +
            "/timeline" +
            "?api_key=" +
            api_key
    )
    while True:
        resp = requests.get(api_url)

        # whenever we see a 429, we sleep for 10 seconds and then restart from the top of the "while" loop
        if resp.status_code == 429:
            print("Rate Limit hit, sleeping for 10 seconds")
            time.sleep(60)
            # continue means start the loop again
            continue

        # if resp.status_code isn't 429, then we carry on to the end of the function and return the data
        get_match_data_timeline = resp.json()
        return get_match_data_timeline


def find_player_data(match_data, puuid):
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]
    return player_data



def gather_all_data(puuid, match_id, mass_region, api_key, role, tempo1, tempo2):
    try:
        data = {'Nick': [],
                'Data': [],
                'champion': [],
                'championenemy': [],
                'kills': [],
                'deaths': [],
                'assists': [],
                'win': [],
                'position': [],
                'tempo_total':[],
                'cs': [],
                'cspm': [],
                'killParticipation': [],
                'soloKills': [],
                'teamDamagePercentage': [],
                'visionScoreAdvantageLaneOpponent': [],
                'visionScorePerMinute': [],
                'detectorWardsPlaced': [],
                'wardTakedownsBefore20M': [],
                'wardTakedowns': [],
                'firstBloodKill': [],
                'firstBloodAssist': [],
                'kda': [],
                'turretPlatesTaken': [],
                'dragonKills': [],
                'wardsKilled': [],
                'wardsPlaced': [],
                'maxCsAdvantageOnLaneOpponent':[],
                'laningPhaseGoldExpAdvantage': [],
                f'cs@{tempo1}': [],
                f'csdiff@{tempo1}': [],
                f'jgdiff@{tempo1}': [],
                f'golddiff@{tempo1}': [],
                f'xpdiff@{tempo1}': [],
                f'danodiff@{tempo1}': [],
                f'csdiff@{tempo2}': [],
                f'jgdiff@{tempo2}': [],
                f'golddiff@{tempo2}': [],
                f'xpdiff@{tempo2}': [],
                f'danodiff@{tempo2}': [],
                f'danodiff@3':[],
                f'Dpm':[],
                f'gameId': [],
                f'gold15rend':[],
                f'goldpm':[],
                f'danoporgold':[],
                f'cspmjg':[],
                'xgeral':[],
                'ygeral':[],
                'fbvitima':[],
                'wardtime':[],
                'Side':[]
                }

        def boolean_to_int(boolean_value):
            if boolean_value:
                return 1
            else:
                return 0
        match_data = get_match_data(match_id, mass_region, api_key)
        player_data = find_player_data(match_data, puuid)
        id_player = player_data['participantId']
        position = player_data['individualPosition']
        gameId=match_data['info']['gameId']

        # tempo game
        minutos = match_data['info']['gameDuration'] // 60
        segundos_restantes = match_data['info']['gameDuration'] % 60
        tempo_total = f"{minutos}:{segundos_restantes}"
        if int(minutos) > 15:
            dia = match_data['info']['gameEndTimestamp']
            dia = str(dia)[:10]
            dia = datetime.utcfromtimestamp(int(dia))
            dia = dia.strftime("%Y-%m-%d %H:%M:%S")
            dia = dia.split(' ')
            dia = dia[0]

            if position == role:

                # adversario
                participants = match_data['metadata']['participants']
                for p in participants:
                    if p != puuid:
                        player_indexa = participants.index(p)
                        a = match_data['info']['participants'][player_indexa]
                        if a['individualPosition'] == position:
                            adversario = a
                    else:
                        continue

                # timeline
                match_data_time = get_match_data_timeline(match_id, mass_region, api_key)
                player_data_timeline = match_data_time['info']['frames']
                timeline3 = player_data_timeline[int(3)]['participantFrames'][str(id_player)]
                timeline6 = player_data_timeline[int(tempo1)]['participantFrames'][str(id_player)]
                timeline15 = player_data_timeline[int(tempo2)]['participantFrames'][str(id_player)]

                xgeral = []
                ygeral = []
                wardtime = []
                fbvitima = []

                def process_data(i,xgeral,ygeral,wardtime,fbvitima,player_data_timeline):
                    try:
                        x = player_data_timeline[i]['participantFrames'][str(id_player)]['position']['x']
                        y = player_data_timeline[i]['participantFrames'][str(id_player)]['position']['y']
                        eventos=player_data_timeline[i]['events']
                        for event in eventos:
                            if event.get('type') == 'WARD_PLACED':
                                idevento = event['creatorId']
                                if str(idevento) == str(id_player):
                                    wardtime.append(event.get('timestamp'))
                            if event.get('killType') == 'KILL_FIRST_BLOOD':
                                killer_id = event.get('killerId')
                                if str(killer_id)==str(id_player):
                                    fbvitima.append(1)
                                else:
                                    fbvitima.append(0)

                        xgeral.append(int(x))
                        ygeral.append(int(y))
                    except Exception as e:
                        print(f"Erro na função process_data({i}): {str(e)}")

                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [executor.submit(process_data, i,xgeral,ygeral,wardtime,fbvitima,player_data_timeline) for i in range(15)]

                    # Aguarde a conclusão de todas as tarefas
                    concurrent.futures.wait(futures)

                # timeline adversario
                id_player_a = adversario['participantId']
                match_data_time_a = get_match_data_timeline(match_id, mass_region, api_key)
                player_data_timeline_a = match_data_time_a['info']['frames']
                timeline_a3 = player_data_timeline_a[int(3)]['participantFrames'][str(id_player_a)]
                timeline_a6 = player_data_timeline_a[int(tempo1)]['participantFrames'][str(id_player_a)]
                timeline_a15 = player_data_timeline_a[int(tempo2)]['participantFrames'][str(id_player_a)]

                # assign the variables we're interested in
                champion = player_data['championName']
                championenemy = adversario['championName']
                k = player_data['kills']
                d = player_data['deaths']
                a = player_data['assists']
                win = player_data['win']
                side=player_data['teamId']
                if int(side)==100:
                    side='blue'
                else:
                    side = 'red'
                cs = player_data['totalMinionsKilled']
                cspm = round(player_data['totalMinionsKilled'] / minutos, 2)
                cspmjg = round(player_data['neutralMinionsKilled'] / minutos, 2)


                killParticipation = player_data['challenges']['killParticipation']
                soloKills = player_data['challenges']['soloKills']
                teamDamagePercentage = player_data['challenges']['teamDamagePercentage']
                visionScoreAdvantageLaneOpponent = player_data['challenges']['visionScoreAdvantageLaneOpponent']
                visionScorePerMinute = player_data['challenges']['visionScorePerMinute']
                detectorWardsPlaced = player_data['detectorWardsPlaced']
                wardTakedownsBefore20M = player_data['challenges']['wardTakedownsBefore20M']
                wardTakedowns = player_data['challenges']['wardTakedowns']
                firstBloodKill = player_data['firstBloodKill']
                firstBloodAssist = player_data['firstBloodAssist']
                kda = player_data['challenges']['kda']
                turretPlatesTaken = player_data['challenges']['turretPlatesTaken']
                dragonKills = player_data['dragonKills']
                wardsKilled = player_data['wardsKilled']
                wardsPlaced = player_data['wardsPlaced']
                maxCsAdvantageOnLaneOpponent=player_data['challenges']['maxCsAdvantageOnLaneOpponent']
                laningPhaseGoldExpAdvantage=player_data['challenges']['laningPhaseGoldExpAdvantage']
                danototal=player_data['totalDamageDealtToChampions']
                dpm=danototal/minutos
                goldtotal=player_data['goldEarned']
                goldpm=goldtotal/minutos
                danoporgold=goldtotal/danototal

                ##timeline 6 min
                cs_time6 = timeline6['minionsKilled']
                cs_time_a6 = timeline_a6['minionsKilled']
                cs_diff6 = cs_time6 - cs_time_a6

                jg6 = timeline6['jungleMinionsKilled']
                jga6 = timeline_a6['jungleMinionsKilled']
                jg_diff6 = jg6 - jga6

                gold6 = timeline6["totalGold"]
                golda6 = timeline_a6["totalGold"]
                golda6diff = gold6 - golda6

                xp6 = timeline6["xp"]
                xpa6 = timeline_a6["xp"]
                xp6diff = xp6 - xpa6

                danototal = timeline6['damageStats']['totalDamageDoneToChampions']
                danorecebido = timeline_a6['damageStats']['totalDamageDoneToChampions']
                danodiff6 = danototal - danorecebido

                danototal = timeline3['damageStats']['totalDamageDoneToChampions']
                danorecebido = timeline_a3['damageStats']['totalDamageDoneToChampions']
                danodiff3 = danototal - danorecebido


                ### 15 min
                cs_time15 = timeline15['minionsKilled']
                cs_time_a15 = timeline_a15['minionsKilled']
                cs_diff15 = cs_time15 - cs_time_a15

                jg15 = timeline15['jungleMinionsKilled']
                jga15 = timeline_a15['jungleMinionsKilled']
                jg_diff15 = jg15 - jga15

                gold15 = timeline15["totalGold"]
                gold15rend=(timeline15["totalGold"]-timeline15["currentGold"])/(timeline15["totalGold"]+timeline15["currentGold"])
                golda15 = timeline_a15["totalGold"]
                golda15diff = gold15 - golda15

                xp15 = timeline15["xp"]
                xpa15 = timeline_a15["xp"]
                xp15diff = xp15 - xpa15

                danototal = timeline15['damageStats']['totalDamageDoneToChampions']
                danorecebido = timeline_a15['damageStats']['totalDamageDoneToChampions']
                danodiff15 = danototal - danorecebido

                # add them to our dataset
                data['Nick'].append(summoner_name.lower())
                data['Data'].append(dia)
                data['champion'].append(champion)
                data['championenemy'].append(championenemy)
                data['kills'].append(k)
                data['deaths'].append(d)
                data['assists'].append(a)
                data['win'].append(boolean_to_int(win))
                data['position'].append(position)
                data['cs'].append(cs)
                data['cspm'].append(cspm)
                data['tempo_total'].append(tempo_total)
                data[f'cs@{tempo1}'].append(cs_time6)
                data[f'csdiff@{tempo1}'].append(cs_diff6)
                data[f'jgdiff@{tempo1}'].append(jg_diff6)
                data[f'golddiff@{tempo1}'].append(golda6diff)
                data[f'xpdiff@{tempo1}'].append(xp6diff)
                data[f'csdiff@{tempo2}'].append(cs_diff15)
                data[f'jgdiff@{tempo2}'].append(jg_diff15)
                data[f'golddiff@{tempo2}'].append(golda15diff)
                data[f'xpdiff@{tempo2}'].append(xp15diff)
                data[f'danodiff@{tempo1}'].append(danodiff6)
                data[f'danodiff@{tempo2}'].append(danodiff15)
                data['killParticipation'].append(killParticipation)
                data['soloKills'].append(soloKills)
                data['teamDamagePercentage'].append(teamDamagePercentage)
                data['visionScoreAdvantageLaneOpponent'].append(visionScoreAdvantageLaneOpponent)
                data['visionScorePerMinute'].append(visionScorePerMinute)
                data['detectorWardsPlaced'].append(detectorWardsPlaced)
                data['wardTakedownsBefore20M'].append(wardTakedownsBefore20M)
                data['wardTakedowns'].append(wardTakedowns)
                data['firstBloodKill'].append(boolean_to_int(firstBloodKill))
                data['firstBloodAssist'].append(boolean_to_int(firstBloodAssist))
                data['kda'].append(kda)
                data['turretPlatesTaken'].append(turretPlatesTaken)
                data['dragonKills'].append(dragonKills)
                data['wardsKilled'].append(wardsKilled)
                data['wardsPlaced'].append(wardsPlaced)
                data['laningPhaseGoldExpAdvantage'].append(laningPhaseGoldExpAdvantage)
                data['maxCsAdvantageOnLaneOpponent'].append(maxCsAdvantageOnLaneOpponent)
                data['danodiff@3'].append(danodiff3)
                data['Dpm'].append(dpm)
                data['gameId'].append(gameId),
                data['gold15rend'].append(gold15rend),
                data['goldpm'].append(goldpm),
                data['danoporgold'].append(danoporgold)
                data['cspmjg'].append(cspmjg),
                data['ygeral'].append(ygeral),
                data['xgeral'].append(xgeral)
                data['fbvitima'].append(int(fbvitima[0])),
                data['wardtime'].append(wardtime),
                data['Side'].append(side)


        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

tempo1 = 5
tempo2 = 15
# Takes 2 minutes to run
#st.set_page_config()

import asyncio
import concurrent.futures
import pandas as pd
from datetime import datetime


def carregar_dados(summoner_name,role,start_time,tempo1,tempo2,api_keys):
    region = "BR1"
    mass_region = "AMERICAS"
    queue_id = 420
    api_key_iter = iter(api_keys)
    api_key=api_keys[0]
    api_key1 = api_keys[1]
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    start_time = int(start_time.timestamp())
    puuid1 = get_puuid(summoner_name, region, api_key1)
    print('AAAA')
    puuid = get_puuid(summoner_name, region, api_key)
    print('AAAA')
    match_ids = get_match_ids(puuid, mass_region, queue_id, api_key, start_time)
    max_threads = 20
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        futures = []
        for match_id in match_ids:
            try:
                api_key = next(api_key_iter)
            except StopIteration:
                # Se todas as chaves foram usadas, reinicie o iterador
                api_key_iter = iter(api_keys)
                api_key = next(api_key_iter)
            if api_key==api_keys[1]:
                puuid2=puuid1
            else:
                puuid2 = puuid
            future = executor.submit(gather_all_data,puuid, match_id, mass_region, api_key, role, tempo1, tempo2)
            futures.append(future)

        resultado = pd.DataFrame()
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                resultado = pd.concat([resultado, result], ignore_index=True)
            except Exception as e:
                print(f"---")
    return resultado
import time
inicio=time.time()

TOP = ['Merkatos','Master 200KM','Hakari',"mirai547", "dontneedmemories", "Yozan", "tzic"]
JUNGLE = ["Nero The Fik",'FA letter','WR PLAYER', "GAM Levi", "Lêvi", "sarolu",'Vinicete','n tenho mental']
MIDDLE = ['azek',"TKZ O KOALA", "O KOALA", "O KOALA 2", "HKS Dazai", "Rei do Ocidente"]
BOTTOM = ["HKS shima og", "AWE Fujita", "eihei", "Rabelokinho", "XiaoZhuanZhu", "Tessin1", "Tessin o matador"]
UTILITY = ["houndin",'Indila4', "grixfyy",'Kita1',"Suunken", "OFF Suunken"]

lista=[TOP,JUNGLE,MIDDLE,BOTTOM,UTILITY]
number=0
api_keys = ['RGAPI-448ce467-3b1b-4cac-96c5-9613331437fc', 'RGAPI-df6cb55a-a3f6-49ea-ad1d-3ec3e40ac3dc']
start_time='2023-09-20 00:00:00'
data = pd.DataFrame()
pdlgeral=pd.DataFrame()



for i in lista:
    role1=['TOP','JUNGLE','MIDDLE','BOTTOM','UTILITY']
    for j in i:
        role=role1[number]
        summoner_name=str(j)
        print(role)
        print(summoner_name)
        df=carregar_dados(summoner_name,role,start_time,5,15,api_keys)
        #pdl=rank(summoner_name,'BR1',api_keys[0])
        #pdlgeral= pd.concat([pdlgeral, pdl], ignore_index=True)
        print(df)
        data = pd.concat([data, df], ignore_index=True)
        time.sleep(60)
    number += 1

print(data)
fim=time.time()
print(f'Resultado {fim-inicio}s')
import os

pasta_destino = r'C:\Users\igorb\PycharmProjects\pythonProject1\streamlitProjeto'
# Nome do arquivo CSV que você deseja salvar
nome_arquivo = 'Datageral.pkl'
nome_arquivo1 = 'pdlgeral.csv'

# Crie o caminho completo para o arquivo CSV
caminho = os.path.join(pasta_destino, nome_arquivo)
caminho_1 = os.path.join(pasta_destino, nome_arquivo1)


data.to_pickle(nome_arquivo)
#pdlgeral.to_csv(caminho_1, index=False)




