import json
import csv as csv_1
import requests
from bs4 import BeautifulSoup
csv = []
header = ['ID', 'Title', 'type_of_paper','most_likely_to_title_WD', 'most_likely_to_title_OA', 
          'publication_date_title', 'author_1', 'educated_at_author_1', 'author_1_ORCID','ocupation_author_1', 
          'works_for_author_1', 'same_as_author_1_WD', 'same_as_author_1_OA', 
          'author_2', 'educated_at_author_2', 'author_2_ORCID','ocupation_author_2', 'works_for_author_2', 
          'same_as_author_2_WD', 'same_as_author_2_OA', 'author_3', 'educated_at_author_3',
          'author_3_ORCID','ocupation_author_3', 'works_for_author_3', 'same_as_author_3_WD', 'same_as_author_3_OA', 
          'author_4', 'educated_at_author_4', 'author_4_ORCID','ocupation_author_4', 'works_for_author_4', 
          'same_as_author_4_WD', 'same_as_author_4_OA', 'author_5', 'educated_at_author_5','author_5_ORCID', 
          'ocupation_author_5', 'works_for_author_5', 'same_as_author_5_WD', 'same_as_author_5_OA',
          'project_1', 'project_2', 'works_for_author_6',
          'organitation_name_1', 'location_organitation_1', 'organitation_website_1', 'organitation_website_2',
          'organitation_website_3', 'organitation_website_4','organitation_website_5', 'organitation_website_6',
          'same_as_organitation_1_WD', 'same_as_organitation_1_OA', 'organitation_name_2', 'location_organitation_2', 
          'same_as_organitation_2_WD', 'same_as_organitation_2_OA', 'organitation_name_3', 'location_organitation_3', 
          'same_as_organitation_3_WD', 'same_as_organitation_3_OA', 'organitation_name_4', 'location_organitation_4', 
          'same_as_organitation_4_WD', 'same_as_organitation_4_OA', 'organitation_name_5', 'location_organitation_5', 
          'same_as_organitation_5_WD', 'same_as_organitation_5_OA', 'organitation_name_6', 'location_organitation_6', 
          'same_as_organitation_6_WD', 'same_as_organitation_6_OA','acknowledge_person_1', 'acknowledge_person_2', 
          'acknowledge_person_3', 'acknowledge_person_4', 'acknowledge_person_5','belongs_to_topic', 'topic_words_2', 
          'topic_words_1','topic_words_0', 'topic_words_7', 'topic_words_4', 'topic_words_5', 'topic_words_6', 'topic_words_8',
          'topic_probability', 'topic_words_3', 'topic_words_9', 'topic_words_10', 'belongs_to_cluster'
         ]
def find_topic_words(jsonfile):
    topic = jsonfile
    json_unique = {}
    json_unique['topics'] = {}
    for i in range(30):
        if topic['topic_id'][str(i)] is not None and topic['topic'][str(i)] is not None:
            tuples = (str(topic['topic_id'][str(i)]).replace(".0",""), topic['topic'][str(i)]) 
        if tuples not in json_unique.values():
            json_unique['topics'].update([tuples])
    return json_unique

def get_organitation_OA(org):
    response = requests.get("https://api.openalex.org/institutions?search="+org)
    return response.json()
print('Processing...')
with open('./output/data-with-links.json', 'r') as csvfile:
        csvAux = json.load(csvfile)
        for obj in csvAux:
            csv.append(obj)

def wikidata_org(org):
    query = '''
    SELECT ?org
    WHERE {
      ?org rdfs:label \"'''+org+'''"@en ;

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }LIMIT 1
    '''
    response = requests.post("https://query.wikidata.org/sparql?query="+query)

    return BeautifulSoup(response.content,"xml")

with open('./output/acknowledgement_triple.json', 'r') as jsonfile:
    ackjson = json.load(jsonfile)
    person = 1
    org = 1
    prev_id = ackjson[0]['paper_id']
    for ack in ackjson:
        if ack['entity_type'] == 'ORG' and prev_id == ack['paper_id']:
            csv[ack['paper_id']]['organitation_name_' + str(org)] = ack['entity_name'].strip().replace("'","")
            res = wikidata_org(ack['entity_name'].strip()).find('binding', {'name': 'org'})
            if res != None:
                csv[ack['paper_id']]['same_as_organitation_' + str(org) + '_WD'] = res.uri.text
            else:
                csv[ack['paper_id']]['same_as_organitation_' + str(org) + '_WD'] = ''
            OA_res = get_organitation_OA(str(ack['entity_name']).replace('&','and'))['results']
            if OA_res:
                csv[ack['paper_id']]['same_as_organitation_'+str(org)+'_OA'] = OA_res[0]['id']
                csv[ack['paper_id']]['location_organitation_'+str(org)] = OA_res[0]['country_code']
                csv[ack['paper_id']]['organitation_website_'+str(org)] = OA_res[0]['homepage_url']
            if org < 6:
                org += 1
        if ack['entity_type'] == 'PER' and prev_id == ack['paper_id']:
            csv[ack['paper_id']]['acknowledge_person_' + str(person)] = ack['entity_name'].strip()
            if person < 5:
                person += 1 
        if prev_id != ack['paper_id']:
            person = 1 
            org = 1
        prev_id = ack['paper_id']
with open('./output/abstract_ai_data.json', 'r') as topicjson:
    clusterTopic = json.load(topicjson)
    for i in range(30):
        csv[i]['belongs_to_topic'] = str(clusterTopic['topic_id'][str(i)]).replace(".0","")
        csv[i]['belongs_to_cluster'] = str(clusterTopic['cluster'][str(i)]).replace(".0","")
        csv[i]['topic_probability'] = clusterTopic['topic_prob'][str(i)]
    topic_words = find_topic_words(clusterTopic)
    for i in topic_words['topics'].keys():
        csv[0]['topic_words_' + str(i)] = topic_words['topics'][str(i)]
json_data = json.loads(json.dumps(csv, indent=4))
with open('./CSV/data-with-links.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv_1.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    for row in json_data:
        writer.writerow(row)
print('Finished!\nThe CSV file has been generated in the CSV folder\n Please, fix any mistakes and procced to the execution part')