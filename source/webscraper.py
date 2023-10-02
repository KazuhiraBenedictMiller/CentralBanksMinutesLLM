from bs4 import BeautifulSoup
import requests

import os
import sys
sys.path.append("../source/")
sys.path.append("../")

import paths

def FetchDataForYear(Links):
    
    for x in Links:
        
        RBA_Base_Link = "https://www.rba.gov.au/"

        Response = requests.get(RBA_Base_Link + x["Link"])
        Soup = BeautifulSoup(Response.text,"html.parser")

        Div = Soup.find("div", {"id": "content"})

        T = []

        for y in Div:
            T.append(y.text)

        Text = [text.replace("\n", "").replace("\t", "").replace("\xa0", " ").replace(",", ", ").replace("  ", " ") for text in T]
        Text = [t for t in Text if t != ""] 

        File_Path = paths.TRANSFORMED_DATA_DIR / f'{x["Title"]}.txt'

        if not File_Path.exists():
            with open (File_Path, "w") as f:
                f.write('\n'.join(Text))
    

def ETL_Pipeline(StartYear, EndYear):
    
    RBA_Base_Link = "https://www.rba.gov.au/"
    Monetary_Policy_Link = "monetary-policy/rba-board-minutes/"
    
    while StartYear <= EndYear:
        
        Complete_Link = RBA_Base_Link + Monetary_Policy_Link + str(StartYear) + "/"
    
        Response = requests.get(Complete_Link)
        Soup = BeautifulSoup(Response.text,"html.parser")

        UL = Soup.find("ul", {"class": "list-articles"})
        As = UL.find_all("a")
        Minutes_Links = [{"Link" : x["href"], "Title" : x.text.replace(" ", "_")} for x in As]

        FetchDataForYear(Minutes_Links)
    
        StartYear += 1