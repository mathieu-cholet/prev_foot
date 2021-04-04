import pandas as pd
from bs4 import BeautifulSoup
import requests
from time import sleep
import pandas as pd
import datetime

def func_day(d):
    return d.split()[0]
def func_month(d):
    return d.split()[1]
def func_year(d):
    return d.split()[2]

dict_months = {
    "Janvier": "01",
    "Février": "02",
    "Mars": "03",
    "Avril": "04",
    "Mai": "05",
    "Juin": "06",
    "Juillet": "07",
    "Août": "08",
    "Septembre": "09",
    "Octobre": "10",
    "Novembre": "11",
    "Décembre": "12"
}

def dataframe_last_matchs(championnat):
    
    if championnat=="Série A":
        lien="https://fbref.com/fr/comps/11/calendrier/Scores-et-tableaux-Serie-A"
    elif championnat=="Bundesliga":
        lien="https://fbref.com/fr/comps/20/calendrier/Scores-et-tableaux-Bundesliga"
    elif championnat=="Première league":
        lien="https://fbref.com/fr/comps/9/calendrier/Scores-et-tableaux-Premier-League"
    elif championnat=="Liga":
        lien="https://fbref.com/fr/comps/12/calendrier/Scores-et-tableaux-La-Liga"
    elif championnat=="Ligue 1":
        lien="https://fbref.com/fr/comps/13/calendrier/Scores-et-tableaux-Ligue-1"
        
    r2=requests.get(lien)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    
    today=datetime.date.today()
    df_matchs_csv=pd.read_csv("intermed/df_matchs.csv",sep=";")
    df_matchs=pd.DataFrame(columns=["date","host_team","away_team","score","host_list_player","away_list_player"])
    for rapport in range(len(soup2.find_all("tbody")[0].find_all("td",{"data-stat":"score"}))) :
        records=[]    
        
        if soup2.find_all("tbody")[0].find_all("td",{"data-stat":"match_report"})[rapport].text == "Rapport de match " and soup2.find_all("tbody")[0].find_all("td",{"data-stat":"date"})[rapport].find("a").text>df_matchs_csv["date"].max()  and soup2.find_all("tbody")[0].find_all("td",{"data-stat":"date"})[rapport].find("a").text < today.isoformat()  :
       
            date=soup2.find_all("tbody")[0].find_all("td",{"data-stat":"date"})[rapport].find("a").text
            host_team=soup2.find_all("tbody")[0].find_all("td",{"data-stat":"squad_a"})[rapport].find("a").text
            away_team= soup2.find_all("tbody")[0].find_all("td",{"data-stat":"squad_b"})[rapport].find("a").text
            score=soup2.find_all("tbody")[0].find_all("td",{"data-stat":"score"})[rapport].find("a").text

            match="https://fbref.com"+soup2.find_all("tbody")[0].find_all("td",{"data-stat":"match_report"})[rapport].find("a")["href"]
            r3=requests.get(match)
            soup3 = BeautifulSoup(r3.text, 'html.parser')
            try:         
                    host_players=soup3.find_all("tbody")[5].find_all("th",{"scope":"row","data-stat":"player"})
                    host_list_player=[]
                    for i in range(len(host_players)):
                        host_player=host_players[i].find("a").text
                        host_list_player.append(host_player)

                    away_players=soup3.find_all("tbody")[7].find_all("th",{"scope":"row","data-stat":"player"})                
                    away_list_player=[]
                    for i in range(len(away_players)):
                        away_player=away_players[i].find("a").text
                        away_list_player.append(away_player)
            except : 
                try : 
                    host_players=soup3.find_all("tbody")[0].find_all("th",{"scope":"row","data-stat":"player"})
                    host_list_player=[]
                    for i in range(len(host_players)):
                        host_player=host_players[i].find("a").text
                        host_list_player.append(host_player)

                    away_players=soup3.find_all("tbody")[2].find_all("th",{"scope":"row","data-stat":"player"})                
                    away_list_player=[]
                    for i in range(len(away_players)):
                        away_player=away_players[i].find("a").text
                        away_list_player.append(away_player)
                except:
                    host_list_player=""
                    away_list_player=""
                    print("problème sur la liste des joueurs : {}".format(match))
        else :
            records.append("")
            continue
        records.append((date,host_team,away_team,score,host_list_player,away_list_player)) 
        df_match = pd.DataFrame(records, columns=["date","host_team","away_team","score","host_list_player","away_list_player"])
        df_matchs = df_matchs.append(df_match)
    return df_matchs


def links_by_championnat(championnat):
    if championnat=="Série A":
        championnat="?league=31&order=desc"
    elif championnat=="Bundesliga":
        championnat="?league=19&order=desc"
    elif championnat=="Première league":
        championnat="?league=13&order=desc"
    elif championnat=="Liga":
        championnat="?league=53&order=desc"
    elif championnat=="Ligue 1":
        championnat="?league=16&order=desc"
    r = requests.get('https://www.fifaindex.com/fr/teams/')
    soup = BeautifulSoup(r.text, 'html.parser')
    fifas=soup.find("li",{"class":"breadcrumb-item dropdown"}).find_all("a")[1:]
    lien_fifa=[]
    for i in range(len(fifas)):
        lien_fifa.append("https://www.fifaindex.com"+fifas[i]["href"])
    lien_fifa.pop(3)  #delete then fifa18wc (world  cup) 
    link_team_championanat=[]
    links_date =[]
    date_str=[]
    for i in range(len(lien_fifa)):  
        r = requests.get(lien_fifa[i])
        soup = BeautifulSoup(r.text, 'html.parser')    
        dates=soup.find_all("li",{"class":"breadcrumb-item dropdown"})[1].find_all("a")[1:]

        for j in range(len(dates)):
            links_date.append("https://www.fifaindex.com"+dates[j]["href"]+championnat)
            date_str.append(dates[j].text)
    df=pd.DataFrame(list(zip(date_str, links_date)), date_str,columns=['dates',"links_date"])
    df['test']=df['dates'].map(func_day)+'-'+df['dates'].map(func_month).map(dict_months)+'-'+df['dates'].map(func_year)
    df['test'] = pd.to_datetime(df['test'],format="%d-%m-%Y" )
    df["month"]=df["test"].dt.month
    df["year"]=df["test"].dt.year
    df.sort_values(by=["year","month"], ascending=False)
    df.drop_duplicates(subset = ["year","month"], keep = 'first', inplace=True)
    df_matchs=pd.read_csv("intermed/df_matchs.csv",sep=";")

    df=df[(df["test"]>df_matchs["date"].max())]
    links_date=df.links_date.values.tolist()       
    
    for i in range(len(links_date)):  
        r = requests.get(links_date[i])
        soup = BeautifulSoup(r.text, 'html.parser')
        Teams=soup.find("div",{"class":"responsive-table table-rounded"}).find_all("a",{"class":"link-team"})
        for j in range(len(Teams)):
            if j%2:
                link_team_championanat.append("https://www.fifaindex.com"+Teams[j]["href"])
        sleep(1)
    return link_team_championanat


def last_update_team(link_team_championanat): 
    df_teams_championnat= pd.DataFrame(columns=['team','date','attaque','milieu','defense','budget_transfert'])
    for link in range(len(link_team_championanat)):
        r = requests.get(link_team_championanat[link])
        soup = BeautifulSoup(r.text, 'html.parser')
        records = []
        team=soup.find_all("div",{"class":"col-sm-6 col-md-7"})[0].find("h1").text
        date=soup.find_all("li",{"class":"breadcrumb-item dropdown"})[1].find_all("a")[0].text
        attaque=soup.find_all("li",{"class": "list-group-item"})[1].find("span").text
        milieu=soup.find_all("li",{"class": "list-group-item"})[2].find("span").text
        defense=soup.find_all("li",{"class": "list-group-item"})[3].find("span").text
        try : 
            budget_transfert=soup.find_all("li",{"class": "list-group-item"})[4].find("span",{"class":"data-currency data-currency-euro float-right"}).text
        except :
            budget_transfert=''
        records.append((team,date, attaque, milieu,defense,budget_transfert))
        df_team = pd.DataFrame(records, columns=['team','date','attaque','milieu','defense','budget_transfert'])
        df_teams_championnat=df_teams_championnat.append(df_team)
        sleep(1)
    return df_teams_championnat

def last_update_player(links_players):
    links_player=[]
    for i in range(len(links_players)):  
        r = requests.get(links_players[i])
        soup = BeautifulSoup(r.text, 'html.parser')
        players=soup.find("div",{"class":"responsive-table table-rounded"}).find_all("tr")[1:]
        for j in range(len(players)):
            links_player.append("https://www.fifaindex.com"+players[j].find_all("a")[0]["href"])
        sleep(1)
    
    df_players=pd.DataFrame(columns=['player','club','date','taille','poid','meilleur_pied','age','valeur','salaire','controles',
                         'dribbles','marquage','tacle_glisse','tacle_debout','engagement','reactivite','placement',
                         'intercept','vista','discipline','passe_centre','passe_courte','passe_longue','phy_acceleration',
                         'phy_endurance','phy_force',' phy_equilibre','phy_vitesse','phy_agilite','phy_detente','tir_tete',
                         'tir_frappe','tir_finition','tir_loin','tir_effet','tir_precision','tir_penalty','tir_volee',
                         'gardien_placement','gardien_plongeon','gardien_main','gardien_pied','gardien_reflexe'])


    for i in range(len(links_player)):
        r = requests.get(links_player[i])
        soup = BeautifulSoup(r.text, 'html.parser')
        records = []
        team=soup.find_all("div",{"class":"col-12 col-sm-6 col-lg-6 team"})
        info=soup.find_all("div",{"class":"col-sm-6"})
        cards=soup.find_all("div",{"class":"col-12 col-md-4 item"})

        
        try:
            try:
                try :
                    player=info[1].contents[1].find_all("h5",{"class":"card-header"})[0].contents[0]
                except :
                    player=""
                try:
                    c=team[1].find("div",{"class":"card-body"}).find('button').text
                    club=team[1].find("h5").find_all("a")[-1].text
                except:
                    c=team[0].find("div",{"class":"card-body"}).find('button').text
                    club=team[0].find("h5").find_all("a")[-1].text
                date=soup.find_all("li",{"class":"breadcrumb-item dropdown"})[1].find_all("a")[0].text
                taille=info[1].find_all("span",{"class":"data-units data-units-metric"})[0].text
                poid=info[1].find_all("span",{"class":"data-units data-units-metric"})[1].text
                meilleur_pied=info[1].find_all("p")[2].find("span").text
                age=info[1].find_all("p")[4].find("span").text
                try : 
                    valeur=info[1].find_all("p",{"class":"data-currency data-currency-euro"})[0].find("span").text
                    salaire=info[1].find_all("p",{"class":"data-currency data-currency-euro"})[1].find("span").text
                except :
                    valeur=""
                    salaire=""

                controles=cards[0].contents[1].find_all("p")[0].contents[1].text
                dribbles= cards[0].contents[1].find_all("p")[1].contents[1].text

                marquage=cards[1].contents[1].find_all("p")[0].contents[1].text
                tacle_glisse=cards[1].contents[1].find_all("p")[1].contents[1].text
                tacle_debout=cards[1].contents[1].find_all("p")[2].contents[1].text

                engagement = cards[2].contents[1].find_all("p")[0].contents[1].text
                reactivite = cards[2].contents[1].find_all("p")[1].contents[1].text
                placement = cards[2].contents[1].find_all("p")[2].contents[1].text
                intercept = cards[2].contents[1].find_all("p")[3].contents[1].text
                vista = cards[2].contents[1].find_all("p")[4].contents[1].text
                try :
                    discipline = cards[2].contents[1].find_all("p")[5].contents[1].text
                except :
                    discipline=""
                passe_centre=cards[3].contents[1].find_all("p")[0].contents[1].text
                passe_courte=cards[3].contents[1].find_all("p")[1].contents[1].text
                passe_longue=cards[3].contents[1].find_all("p")[2].contents[1].text

                phy_acceleration=cards[4].contents[1].find_all("p")[0].contents[1].text
                phy_endurance=cards[4].contents[1].find_all("p")[1].contents[1].text
                phy_force=cards[4].contents[1].find_all("p")[2].contents[1].text
                phy_equilibre=cards[4].contents[1].find_all("p")[3].contents[1].text
                phy_vitesse=cards[4].contents[1].find_all("p")[4].contents[1].text
                phy_agilite=cards[4].contents[1].find_all("p")[5].contents[1].text
                phy_detente=cards[4].contents[1].find_all("p")[6].contents[1].text

                tir_tete=cards[5].contents[1].find_all("p")[0].contents[1].text
                tir_frappe=cards[5].contents[1].find_all("p")[1].contents[1].text
                tir_finition=cards[5].contents[1].find_all("p")[2].contents[1].text
                tir_loin=cards[5].contents[1].find_all("p")[3].contents[1].text
                tir_effet=cards[5].contents[1].find_all("p")[4].contents[1].text
                tir_precision=cards[5].contents[1].find_all("p")[5].contents[1].text
                tir_penalty=cards[5].contents[1].find_all("p")[6].contents[1].text
                tir_volee=cards[5].contents[1].find_all("p")[7].contents[1].text

                gardien_placement=cards[6].contents[1].find_all("p")[0].contents[1].text
                gardien_plongeon=cards[6].contents[1].find_all("p")[1].contents[1].text
                gardien_main=cards[6].contents[1].find_all("p")[2].contents[1].text
                gardien_pied=cards[6].contents[1].find_all("p")[3].contents[1].text
                gardien_reflexe=cards[6].contents[1].find_all("p")[4].contents[1].text
            except :
                    try:
                        try :
                            player=info[1].contents[1].find_all("h5",{"class":"card-header"})[0].contents[0]
                        except :
                            player=""
                        try:
                            c=team[1].find("div",{"class":"card-body"}).find('button').text
                            club=team[1].find("h5").find_all("a")[-1].text
                        except:
                            c=team[0].find("div",{"class":"card-body"}).find('button').text
                            club=team[0].find("h5").find_all("a")[-1].text
                        date=soup.find_all("li",{"class":"breadcrumb-item dropdown"})[1].find_all("a")[0].text
                        taille=info[1].find_all("span",{"class":"data-units data-units-metric"})[0].text
                        poid=info[1].find_all("span",{"class":"data-units data-units-metric"})[1].text
                        meilleur_pied=info[1].find_all("p")[2].find("span").text
                        age=info[1].find_all("p")[4].find("span").text
                        try : 
                            valeur=info[1].find_all("p",{"class":"data-currency data-currency-euro"})[0].find("span").text
                            salaire=info[1].find_all("p",{"class":"data-currency data-currency-euro"})[1].find("span").text
                        except :
                            valeur=""
                            salaire=""

                        controles=cards[0].contents[1].find_all("p")[0].contents[-1].text
                        dribbles= cards[0].contents[1].find_all("p")[1].contents[-1].text

                        marquage=cards[1].contents[1].find_all("p")[0].contents[-1].text
                        tacle_glisse=cards[1].contents[1].find_all("p")[1].contents[-1].text
                        tacle_debout=""

                        engagement = cards[2].contents[1].find_all("p")[0].contents[-1].text
                        reactivite = cards[2].contents[1].find_all("p")[2].contents[-1].text
                        placement = ""
                        intercept = ""
                        vista =""
                        try :
                            discipline = cards[2].contents[1].find_all("p")[1].contents[-1].text
                        except :
                            discipline=""
                        passe_centre=cards[3].contents[1].find_all("p")[0].contents[-1].text
                        passe_courte=cards[3].contents[1].find_all("p")[1].contents[-1].text
                        passe_longue=cards[3].contents[1].find_all("p")[2].contents[-1].text

                        phy_acceleration=cards[4].contents[1].find_all("p")[0].contents[-1].text
                        phy_endurance=cards[4].contents[1].find_all("p")[1].contents[-1].text
                        phy_force=cards[4].contents[1].find_all("p")[2].contents[-1].text
                        phy_equilibre=""
                        phy_vitesse=cards[4].contents[1].find_all("p")[3].contents[-1].text
                        phy_agilite=""
                        phy_detente=""

                        tir_tete=cards[5].contents[1].find_all("p")[0].contents[-1].text
                        tir_frappe=cards[5].contents[1].find_all("p")[1].contents[-1].text
                        tir_finition=cards[5].contents[1].find_all("p")[2].contents[-1].text
                        tir_loin=cards[5].contents[1].find_all("p")[3].contents[-1].text
                        tir_effet=""
                        tir_precision=cards[5].contents[1].find_all("p")[4].contents[-1].text
                        tir_penalty=""
                        tir_volee=""

                        gardien_placement=cards[6].contents[1].find_all("p")[2].contents[-1].text
                        gardien_plongeon=cards[6].contents[1].find_all("p")[3].contents[-1].text
                        gardien_main=cards[6].contents[1].find_all("p")[1].contents[-1].text
                        gardien_pied=""
                        gardien_reflexe=cards[6].contents[1].find_all("p")[0].contents[-1].text
                    except : 
                        try :
                            player=info[1].contents[1].find_all("h5",{"class":"card-header"})[0].contents[0]
                        except :
                            player=""
                        try:
                            c=team[1].find("div",{"class":"card mb-5"}).find('button').text
                            club=team[1].find("h5").find_all("a")[-1].text
                        except:
                            c=team[0].find("div",{"class":"card mb-5"}).find('button').text
                            club=team[0].find("h5").find_all("a")[-1].text
                        date=soup.find_all("li",{"class":"breadcrumb-item dropdown"})[1].find_all("a")[0].text
                        taille=info[1].find_all("span",{"class":"data-units data-units-metric"})[0].text
                        poid=info[1].find_all("span",{"class":"data-units data-units-metric"})[1].text
                        meilleur_pied=info[1].find_all("p")[2].find("span").text
                        age=info[1].find_all("p")[4].find("span").text
                        try : 
                            valeur=info[1].find_all("p",{"class":"data-currency data-currency-euro"})[0].find("span").text
                            salaire=info[1].find_all("p",{"class":"data-currency data-currency-euro"})[1].find("span").text
                        except :
                            valeur=""
                            salaire=""

                        controles=cards[0].contents[1].find_all("p")[0].contents[-1].text
                        dribbles= cards[0].contents[1].find_all("p")[1].contents[-1].text

                        marquage=cards[1].contents[1].find_all("p")[0].contents[-1].text
                        tacle_glisse=cards[1].contents[1].find_all("p")[1].contents[-1].text
                        tacle_debout=""

                        engagement = cards[2].contents[1].find_all("p")[0].contents[-1].text
                        reactivite = cards[2].contents[1].find_all("p")[1].contents[-1].text
                        placement = ""
                        intercept = ""
                        vista =""

                        discipline = cards[2].contents[1].find_all("p")[2].contents[-1].text

                        passe_centre=cards[3].contents[1].find_all("p")[0].contents[-1].text
                        passe_courte=cards[3].contents[1].find_all("p")[1].contents[-1].text
                        passe_longue=cards[3].contents[1].find_all("p")[2].contents[-1].text

                        phy_acceleration=cards[4].contents[1].find_all("p")[0].contents[-1].text
                        phy_endurance=cards[4].contents[1].find_all("p")[2].contents[-1].text
                        phy_force=cards[4].contents[1].find_all("p")[3].contents[-1].text
                        phy_equilibre=cards[4].contents[1].find_all("p")[4].contents[-1].text
                        phy_vitesse=cards[4].contents[1].find_all("p")[1].contents[-1].text
                        phy_agilite=""
                        phy_detente=""

                        tir_tete=cards[5].contents[1].find_all("p")[0].contents[-1].text
                        tir_frappe=cards[5].contents[1].find_all("p")[2].contents[-1].text
                        tir_finition=""
                        try: 
                            tir_loin=cards[5].contents[1].find_all("p")[3].contents[-1].text
                        except : 
                            tir_loin=""
                        tir_effet=""
                        tir_precision=cards[5].contents[1].find_all("p")[1].contents[-1].text
                        tir_penalty=""
                        tir_volee=""

                        gardien_placement=cards[6].contents[1].find_all("p")[3].contents[-1].text
                        gardien_plongeon=""
                        gardien_main=cards[6].contents[1].find_all("p")[2].contents[-1].text
                        gardien_pied=""
                        gardien_reflexe=cards[6].contents[1].find_all("p")[0].contents[-1].text    
            records.append((player,club,date,taille,poid,meilleur_pied,age,valeur,
                                      salaire,controles,dribbles,marquage,tacle_glisse,tacle_debout,engagement,
                                      reactivite,placement,intercept,vista,discipline,passe_centre,passe_courte,
                                      passe_longue,phy_acceleration,phy_endurance,phy_force,phy_equilibre,phy_vitesse,
                                      phy_agilite,phy_detente,tir_tete,tir_frappe,tir_finition,tir_loin,tir_effet,
                                      tir_precision,tir_penalty,tir_volee,gardien_placement,gardien_plongeon,gardien_main,
                                      gardien_pied,gardien_reflexe))
            df_player = pd.DataFrame(records, columns=['player','club','date','taille','poid','meilleur_pied','age','valeur',
                                      'salaire','controles','dribbles','marquage','tacle_glisse','tacle_debout','engagement',
                                      'reactivite','placement','intercept','vista','discipline','passe_centre','passe_courte',
                                      'passe_longue','phy_acceleration','phy_endurance','phy_force','phy_equilibre','phy_vitesse',
                                      'phy_agilite','phy_detente','tir_tete','tir_frappe','tir_finition','tir_loin','tir_effet',
                                      'tir_precision','tir_penalty','tir_volee','gardien_placement','gardien_plongeon','gardien_main',
                                      'gardien_pied','gardien_reflexe'])

            df_players=df_players.append(df_player)
            sleep(1)
        except:
            print(links_players[i])
    return df_players

if __name__ == "__main__":
    df_match = dataframe_last_matchs("Série A")
    links_date = last_update("Série A")
    df_team = last_update_team(links_date)
    df_player = last_update_player(links_date)


