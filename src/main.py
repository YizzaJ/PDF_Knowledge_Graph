import os

from flask import Flask, render_template, request, json, redirect, url_for, session, jsonify
from flask.wrappers import Response
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
from pathlib import Path
import csv



class MyResponse(Response):
    default_mimetype = 'application/json'

# CONFIGURACION DE LA APP
app = Flask(__name__)
app.secret_key = 'clave secreta'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["CACHE_TYPE"] = "null"

with open('./rdf/KG.nt', 'r') as kg_file:
    kg_lines = kg_file.readlines()

updated_kg_lines = []
i = 0
for line in kg_lines:
    if line.startswith("\"<http://group3.papers.es/resource/Topic/" + str(i) + ">\"@"):
        updated_line = line.replace(">\"@", ">").replace("\"<", "<")
        updated_kg_lines.append(updated_line)
        i += 1
    else:
        updated_kg_lines.append(line)

with open('./rdf/KG.nt', 'w') as kg_file:
    kg_file.writelines(updated_kg_lines)

    

# RDFLIB

g = Graph()
g.namespace_manager.bind('rr', Namespace("http://www.w3.org/ns/r2rml#"), override=False)
g.namespace_manager.bind('rml', Namespace("http://semweb.mmlab.be/ns/rml#"), override=False)
g.namespace_manager.bind('ql', Namespace("http://semweb.mmlab.be/ns/ql#"), override=False)
g.namespace_manager.bind('transit', Namespace("http://vocab.org/transit/terms/"), override=False)
g.namespace_manager.bind('xsd', Namespace("http://www.w3.org/2001/XMLSchema#"), override=False)
g.namespace_manager.bind('wgs84_pos', Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#"), override=False)
g.namespace_manager.bind('', Namespace("http://group3.com/"), override=False)
g.namespace_manager.bind('rml', Namespace("http://semweb.mmlab.be/ns/rml#"), override=False)
g.namespace_manager.bind('owl', Namespace("http://www.w3.org/2002/07/owl#"), override=False)

ns = Namespace("http://group3.papers.es/ontology/")
ns2 = Namespace("http://group3.papers.es/resource/")
owl = Namespace("http://www.w3.org/2002/07/owl#")
g.parse("./rdf/KG.nt", format="nt")

data = []
with open('./CSV/data-with-links.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)# Leer la primera fila del archivo CSV
csvfile.close()
with open('./static/data-with-links.json', 'w', encoding='utf-8') as jsonfile:
    jsonfile.write(json.dumps(data, indent=4))


# MAIN Y METODOS PARA MOSTRAR PAGINAS
@app.route("/")
def main():
    return render_template("search.html")


@app.route("/results", methods=['POST', 'GET'])
def results():
    return render_template("results.html")

@app.route("/busqueda", methods=['POST', 'GET'])
def busqueda():
    try:
        _requestAutor = request.args.get('authorSelect')
        _requestOrganization = request.args.get('organizationSelect')
        _requestPaper = request.args.get('paperSelect')
        _requestTopic = request.args.get('topicSelect')
        _autor = str(_requestAutor)
        _org = str(_requestOrganization)
        _paper = str(_requestPaper)
        _topic = str(_requestTopic)
        _jsonList= []

        # SPARQL query
        query = "select distinct ?Object " \
                " where{ " 
        if _autor != '':
            query  += "?Object <http://group3.papers.es/ontology/hasAuthor> <http://group3.papers.es/resource/Person/"+ _autor.replace(" ","%20") + ">."
        if _org != '':
            query  += "?Object <http://group3.papers.es/ontology/acknowledges> <http://group3.papers.es/resource/Organitation/"+ _org.replace(" ","%20") + ">."
        if _paper != '':
            query  += "?Object <http://group3.papers.es/ontology/hasTitle> \""+ _paper + "\"."
        if _topic != '':
            query  += "?Object <http://group3.papers.es/ontology/belongsToTopic> <http://group3.papers.es/resource/Topic/"+ _topic + ">."
        query += '\n}'
        q3 = prepareQuery(query)
        for r in g.query(q3):
            tojson = {'id': str(r[0]).replace("http://group3.papers.es/resource/paper/","")}
            query2 = "select distinct ?Property " \
                     "where { ?m ?Property ?Object .}"
            q4 = prepareQuery(query2)
            for r2 in g.query(q4, initBindings={"m": r[0]}):
                # print(r[0], r2[0])
                query3 = "select distinct ?Object " \
                         "where { ?m ?p ?Object .}"
                q5 = prepareQuery(query3)
                author = 1
                org = 1
                per = 1
                for r3 in g.query(q5, initBindings={"m": r[0], "p": r2[0]}):
                    propiedad = str(r2[0])
                    print(propiedad)
                    objeto = str(r3[0])
                    #print(objeto)
                    if propiedad == "http://group3.papers.es/ontology/hasTitle":
                        tojson['title'] = objeto
                    if propiedad == "http://group3.papers.es/ontology/belongsToTopic":
                        queryTopic = "select distinct ?o where {" \
                            "<"+objeto +">"+" <http://group3.papers.es/ontology/words>  ?o .}"
                        q7 = prepareQuery(queryTopic)
                        for rt in g.query(q7):
                            tojson['topic_words'] = str(rt[0])
                        tojson['topic'] = objeto.replace("http://group3.papers.es/resource/Topic/","" )
                    if propiedad == "http://group3.papers.es/ontology/publicationDate":
                        tojson['date'] = objeto
                    if propiedad == "http://group3.papers.es/ontology/belongsToCluster":
                        tojson['cluster'] = objeto.replace("http://group3.papers.es/resource/Cluster/","" )
                    if propiedad == "http://group3.papers.es/ontology/similarTo":
                        tojson['OA'] = objeto
                    if propiedad == "http://www.w3.org/2002/07/owl#sameAs":
                        tojson[propiedad.replace("http://www.w3.org/2002/07/owl#sameAs", "WD")] = objeto
                    if propiedad == "http://group3.papers.es/ontology/hasType":
                        tojson["type_of_paper"] = objeto
                    if propiedad == "http://group3.papers.es/ontology/hasAuthor":
                        tojson['author_' + str(author)] = objeto.replace("http://group3.papers.es/resource/Person/","").replace("%20"," ")
                        queryAutor = "select distinct ?o where {" \
                            "<"+objeto+"> ?p  ?o ."\
                            "?m <http://www.w3.org/2002/07/owl#sameAs> ?o .}"
                        q6 = prepareQuery(queryAutor)
                        i = 1
                        for r4 in g.query(q6):
                            tojson["same_as_author_" + str(author) + '_' + str(i)] = str(r4[0])
                            i += 1
                    if propiedad == "http://group3.papers.es/ontology/acknowledges" and objeto.startswith("http://group3.papers.es/resource/Organitation/"):
                        tojson['organization_' + str(org)] = objeto.replace("http://group3.papers.es/resource/Organitation/","").replace("%20"," ")
                        queryAutor = "select distinct ?o where {" \
                            "<"+objeto+"> ?p  ?o ."\
                            "?m <http://www.w3.org/2002/07/owl#sameAs> ?o .}"
                        q6 = prepareQuery(queryAutor)
                        index = 1
                        for r4 in g.query(q6):
                            tojson["same_as_organization_" + str(org) + "_" + str(index)] = str(r4[0])
                            index += 1
                    if propiedad == "http://group3.papers.es/ontology/acknowledges" and objeto.startswith("http://group3.papers.es/resource/Person/"):
                        tojson['person_' + str(per)] = objeto.replace("http://group3.papers.es/resource/Person/","").replace("%20"," ")

                    per += 1
                    org += 1
                    author += 1
            # break
            _jsonList.append(tojson)
        # END SPARQL query
        with open("./static/query.json", "w", encoding='utf-8') as file:
            json.dump(_jsonList, file, indent = 4)
        if(len(_jsonList)==0):
            return render_template("error.html",error="El recurso al que intentas acceder no esta disponible")
        return render_template("results.html",street="Lo que sea",enlace="https://www.wikidata.org/entity/Q2807", solo = True)
    except Exception as e:
        return json.dumps({'error': e})


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(port=5000)
