from bs4 import BeautifulSoup
import requests

from fpdf import FPDF

import os
import sys
sys.path.append("../source/")
sys.path.append("../")

import paths

def CleanTextData(Text):
    
    #Function used to Clean and Preprocess Text Data
    
    #Characters to Replace
    
    ToReplace = {"\n": " ",
                 "\t": " ",
                 "\xa0": " ",
                 ",": ", ",
                 "  ": " ",
                 "   ": " ",
                 "    ": " ",
                 "     ": " ",
                 "  ": " "  #<- This is Doubled in the Dictionary for a Reason
                }
        
    #Iterating through Dictionary and Cleaning Each Character in Text
        
    for k,v in ToReplace.items():
        Text = [text.replace(k, v) for text in Text]
        
    #Our List contains now a Given Number of Strings, Cleaned by Previous Special Characters
    #First, we Remove Empty and Strings that Contain only one Space
    #Second, we Re-Encode in Latin-1 Encoding in order to be Used by FPDF
    #Third, we Remove Characters not in the Latin-1 Unicode (if not Encoded by Latin-1 they're left with a "?" instead)
        
    Text = [t for t in Text if t != "" and t != " "] 
    Text = [e.encode("latin-1", "replace").decode("latin-1") for e in Text]
    Text = [c.replace("?", "") for c in Text]
        
    return Text
    
def PrintPDF(File_Path, Title, CleanedText):
    
    #Function Only used to Dump the PDF to Disk
    
    #If File doesn't Exist, it then sets the pdf properties and it dumps to Disk
    
    if not File_Path.exists():
        PDF = FPDF()
        PDF.add_page()
        PDF.set_font("Arial", size = 10)
        PDF.set_margins(left = 10, top = 10, right = 10)
            
        for text in CleanedText:
            PDF.multi_cell(w = 0, h = 9, txt = text, align = "L")

        PDF.output(File_Path)
    
    else:
        print(f'{Title} Already Processed and in the Vector Store. Check in the Storage Directory.')

def FetchDataForYear(Links):
    
    #For a Given List of Links, we Iterate through each one of them and Scrape the Content, Clean it and Dump it to Disk
    
    for x in Links:
        if x.endswith("html"):
            RBA_Base_Link = "https://www.rba.gov.au/"

            Response = requests.get(RBA_Base_Link + x["Link"])
            Soup = BeautifulSoup(Response.text, "html.parser")

            Div = Soup.find("div", {"id": "content"})

            Text = []

            #for y in Div.find_all("p") -> To get only Paragraphs and not Titles 
            for y in Div:
                Text.append(y.text)

            CleanedText = CleanTextData(Text)

            PrintPDF(paths.STORAGE_DATA_DIR / f'{x["Title"]}.pdf', f'{x["Title"]}.pdf',CleanedText)
            
def ScrapeData(StartYear, EndYear):
    
    #For a Given Range of Years from StartYear to EndYear, we get all the Links for the Minutes, then Scrape the Content, Clean the Data and Dump it to Disk
    
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