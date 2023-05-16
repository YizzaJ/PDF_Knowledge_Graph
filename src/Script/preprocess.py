import requests
import csv as csv_1
import json
import os
from bs4 import BeautifulSoup
import json
import re

def process_pdf(file_path):
    inputFile = open(file_path, 'rb')
    response = requests.post("http://localhost:8070/api/processFulltextDocument", 
                                 files={"input": inputFile})
    return response.content

def get_organitation_OA(org):
    response = requests.get("https://api.openalex.org/institutions?search="+org)
    return response.json()

def get_author_OA(author):
    response = requests.get("https://api.openalex.org/authors?search="+author)
    return response.json()  

def get_title_OA(paper):
    response = requests.get("https://api.openalex.org/works?search="+paper)
    return response.json()   

def get_title(soup):
    title = soup.titleStmt
    if title is not None:
        return title.title.text
    else:
        return ""
def wikidata_author(author):
    query = '''
    SELECT ?person ?personLabel ?institution ?institutionLabel ?occupation ?occupationLabel
    WHERE {
      ?person rdfs:label \"'''+author+'''"@en ;
              wdt:P69 ?institution .
      OPTIONAL { ?person wdt:P106 ?occupation . }

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }LIMIT 1
    '''
    response = requests.post("https://query.wikidata.org/sparql?query="+query)

    return BeautifulSoup(response.content,"xml")

def wikidata_paper(paper):
    query = '''
    SELECT ?paper 
    WHERE {
      ?paper rdfs:label \"'''+paper+'''"@en ;

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }LIMIT 1
    '''
    response = requests.post("https://query.wikidata.org/sparql?query="+query)

    return BeautifulSoup(response.content,"xml")

def get_abstract(soup):
    abstract = soup.abstract
    if abstract is not None:
        return str(abstract.text).replace("\n","")
    else:
        return "" 

def get_acknowledgements(soup):
    acknowledgement = soup.find('div', {'type': 'acknowledgement'})
    if acknowledgement is not None:
        return acknowledgement.p.text
    else:
        return ""
    
def extract_ack():
    acknowledgements = []

    with open("./ack.json", 'r') as file:
        data = json.load(file)

        for item in data:
            if 'acknowledgents' in item:
                acknowledgements.append(item['acknowledgents'])
    return acknowledgements

def extract_projects(ack):
    patterns = [
        r'\d{4}\.\d{2}\.\d{4}\.\d{3}',  
        r'\(?[A-Za-z]*\d[A-Za-z\d-]*\)?',
        r'(\(\w*[\d\/.-]+\w*\))|(\w*[\d\/.-]+\w*)'

    ]
    projects = []
    identifiers = []
    for pattern in patterns:
        matches = re.findall(pattern, ack)
        identifiers.extend(matches)

    for id in identifiers:
        if len(id) >= 5:
            projects.append(str(id).replace("(","").replace(")",""))
    return projects

header = ['ID', 'Title', 'most_likely_to_title_WD', 'most_likely_to_title_OA', 
          'publication_date_title', 'author_1', 'educated_at_author_1', 'author_1_ORCID','ocupation_author_1', 
          'works_for_author_1', 'same_as_author_1_WD', 'same_as_author_1_OA', 
          'author_2', 'educated_at_author_2', 'author_2_ORCID','ocupation_author_2', 'works_for_author_2', 
          'same_as_author_2_WD', 'same_as_author_2_OA', 'author_3', 'educated_at_author_3',
          'author_3_ORCID','ocupation_author_3', 'works_for_author_3', 'same_as_author_3_WD', 'same_as_author_3_OA', 
          'author_4', 'educated_at_author_4', 'author_4_ORCID','ocupation_author_4', 'works_for_author_4', 
          'same_as_author_4_WD', 'same_as_author_4_OA', 'author_5', 'educated_at_author_5','author_5_ORCID', 
          'ocupation_author_5', 'works_for_author_5', 'same_as_author_5_WD', 'same_as_author_5_OA',
          'project_1', 'project_2',
          'organitation_name_1', 'location_organitation_1', 
          'same_as_organitation_1_WD', 'same_as_organitation_1_OA', 'organitation_name_2', 'location_organitation_2', 
          'same_as_organitation_2_WD', 'same_as_organitation_2_OA', 'organitation_name_3', 'location_organitation_3', 
          'same_as_organitation_3_WD', 'same_as_organitation_3_OA', 'organitation_name_4', 'location_organitation_4', 
          'same_as_organitation_4_WD', 'same_as_organitation_4_OA', 'organitation_name_5', 'location_organitation_5', 
          'same_as_organitation_5_WD', 'same_as_organitation_5_OA', 'organitation_name_6', 'location_organitation_6', 
          'same_as_organitation_6_WD', 'same_as_organitation_6_OA'
         ]
rows = [] 
files_json = []
for filename in os.listdir('./PDFs/'):
    print('Proccesing: ' + filename)
    csv = {key: '' for key in header} 
    index = len(rows)  
    grobit_file = process_pdf("./PDFs/" + filename)
    soup = BeautifulSoup(grobit_file, "xml")
    csv['ID'] = index
    csv['Title'] = soup.find('title').text.replace("'","") if soup.find('title').text else ''
    if wikidata_paper(csv['Title']).find('binding', {'name': 'paper'}):
        csv['most_likely_to_title_WD'] = wikidata_paper(csv['Title']).find('binding', {'name': 'paper'}).uri.text
    else: 
        csv['most_likely_to_title_WD'] = ''
    csv['publication_date_title'] = soup.find('date')['when'] if soup.find('date').has_attr('when') else ''
    i = 0
    for author in soup.find_all('author'):
        name = author.find('forename')
        surname = author.find('surname')
        if name is not None and len(name.text) > 2 and name.text not in csv.values():
            i += 1
            surname = surname.text if surname else ''
            name = name.text if name else ''
            csv['author_' + str(i)] = name.replace("'","") + ' ' + surname.replace("'","")
            res = wikidata_author(name + ' ' + surname).find('binding', {'name': 'institutionLabel'})
            if res != None: 
                csv['educated_at_author_'+str(i)] = res.literal.text.replace("'","")
            else:
                csv['educated_at_author_'+str(i)] = ''
            res = wikidata_author(name + ' ' + surname).find('binding', {'name': 'person'})
            if res != None and res.uri:
                csv['same_as_author_'+str(i)+'_WD'] = res.uri.text
            else:
                csv['same_as_author_'+str(i)+'_WD'] = ''
            res = wikidata_author(name + ' ' + surname).find('binding', {'name': 'occupationLabel'})
            if res != None and res.literal:
                csv['ocupation_author_'+str(i)] = res.literal.text.replace("'","")
            else:
                csv['ocupation_author_'+str(i)] = ''
    i = 0
    for project in extract_projects(get_acknowledgements(soup)):
        csv['project_'+str(i)] = project
        i += 1
    filtered_data = {key: csv[key] for key in header if key in csv}
    rows.append(filtered_data)
    file_json = {
                "ID": index,
                "title":  get_title(soup),
                "abstract": get_abstract(soup),
                "acknowledgents": get_acknowledgements(soup)
            }
    files_json.append(file_json)
OA_authors = {}
index = 1
print('Adding OpenAlex information about the authors')
for i in range(len(rows)):
    OA_authors[i] = {}
    for f in range(5):
        if len(rows[i]['author_' + str(index)]) > 0 and get_author_OA(rows[i]['author_' + str(index)])['meta']['count'] > 0:
            rows[i]['same_as_author_'+str(index)+'_OA'] = get_author_OA(rows[i]['author_' + str(index)])['results'][0]['id']
            rows[i]['author_'+ str(index) +'_ORCID'] = get_author_OA(rows[i]['author_' + str(index)])['results'][0]['orcid']\
                if get_author_OA(rows[i]['author_' + str(index)])['results'][0]['orcid'] is not None else ''
            rows[i]['works_for_author_'+str(index)] = get_author_OA(rows[i]['author_' + str(index)])['results'][0]['last_known_institution']['id']\
                if get_author_OA(rows[i]['author_' + str(index)])['results'][0]['last_known_institution'] is not None else ''
        index += 1
    index = 1
print('Finished')
print('Adding OpenAlex ID\'s related to Titles')
for i in range(len(rows)):
    rows[i]['most_likely_to_title_OA'] = get_title_OA(rows[i]['Title'])['results'][0]['id'] \
              if get_title_OA(rows[i]['Title'])['meta']['count'] > 0 else ''
    rows[i]['type_of_paper'] = get_title_OA(rows[i]['Title'])['results'][0]['type'] \
              if get_title_OA(rows[i]['Title'])['meta']['count'] > 0 else ''
print('Finished\n File named \'extracted.json\' has been generated in output folder. \n Please, fix any mistakes and procced to the IA integration part. ')
        
with open('./output/data-with-links.json', 'w', encoding='utf-8') as jsonfile:
    jsonfile.write(json.dumps(rows, indent=4))

with open('./output/extracted.json', 'w') as file:
        file.write(json.dumps(files_json, indent=4))