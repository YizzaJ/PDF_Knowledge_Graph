[![DOI](https://zenodo.org/badge/637133691.svg)](https://zenodo.org/badge/latestdoi/637133691)
[![Documentation Status](https://readthedocs.org/projects/pdf-knowledge-graph/badge/?version=latest)](https://pdf-knowledge-graph.readthedocs.io/en/latest/?badge=latest)

# PDF_Knowledge_Graph

## Description

This project refers to a PDF analyzer that by extracting their Abstracs and Acknowledgements, constructs a knowledge graph. This allows the user to have the files categorized regarding common themes and alsogenerate queries against them, being able to extract information such as the authors, organizations acknowledged, and the type of paper they represent. Additionally, the information extracted from the PDFs will be enriched using online sources such as [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) and the [OpenAlex API](https://openalex.org/).

## Requirements

To run this program you will need:

* System with Windows or Linux operating systems.
* Install [Docker](https://docs.docker.com/engine/install/).

## Installation Instructions

1. Clone this git project:

   `git clone https://github.com/YizzaJ/PDF_Knowledge_Graph.git`

## Execution Instructions

1. Run a docker server.
2. . Enter the [src/](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src "src") directory since the rest of the instructions will be executed from there:
   `cd src`
3. Insert all the *.pdf* files inside the [src/PDFs](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src/PDFs) directory.
4. If you are using Windows run the `preprocessing.bat` file. If you are using Linux run `preprocessing.sh`.
   This will create **two** files inside the  output directory, `extracted.json` and `data-with-links.json`.
5. The `data-with-links.json` file should be used as one of the input files used in the CSV file generation step.

**Topic Modelling, Clustering and NER**

- The following steps are used to include additional information to enrich the knowledge graph.

6. Make sure that you have run the previous steps and to copy the [extracted.json](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/output/extracted.json) file to the [data](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/data "data") directory.
7. To perform clustering and topic modelling run `python ai_tasks/ai_tasks.py`
8. To perform NER run the [NER notebook](src/ai_tasks/NER.ipynb) manually

**Generating the CSV**

* This uses the information generated from the previous steps to form a *.csv* with all the information.

9. Place the `abstract_ai_data.json`, `topic_id_list.json` and `acknowledgement_triple.json` files, generated in the previous step, in the [src/output](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src/output) directory. The `extracted.json` and `data-with-links.json` should be already on that folder.
10. If you are using Windows run the [generate_csv.bat](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/generate_csv.bat) file. If you are using Linux run [generate_csv.sh](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/generate_csv.sh).
    This will create a *.csv* file inside the [src/CSV](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src/CSV) directory named `data-with-links.csv.`

**Knowledge Graph generation and Visualization step**

11. If you are using Windows run the [generate_kg.bat](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/generate_kg.bat) file. If you are using Linux run [generate_kg.sh](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/generate_kg.sh).
    This will create a container called `flask` that runs a web server to visualize the information contained in the Knowledge Graph. The expected output should be:

```
   Serving Flask app 'main'
   Debug mode: off
   WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
   Running on all addresses (0.0.0.0)
   Running on http://127.0.0.1:8080
   Running on http://172.17.0.2:8080
   Press CTRL+C to quit
```

12. Finally, you will be able to view the results in your web browser at the following URL:

```bash
  http://localhost:8080
```

## Example

Ins this part, we provide some sample outputs of our containers using some sample .pdf files.

* The .pdf files we use can be located at the [src/PDFs](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src/PDFs) directory.
* On the [src/output](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src/output) directory you can find:
  * [extracted.json](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/output/extracted.json): output of the **first container** that provides a list of title, abstrac and acknowledgements from each of the processed papers.
  * [data-with-links.json](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/output/data-with-links.json): output of the **first container** that provides the enriched from the **external sources** information about each paper.
  * [abstract_ai_data.json](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/output/abstract_ai_data.json): output of the **topic modelling and clustering part**, this contains the topics, the clusters, and to which one of the each paper belongs to. Also you could find the probabilities of each paper for belonging to each of the topics.
  * [topic_id_list.json](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/output/topic_id_list.json): output of the **topic modelling and clustering part** that contains a list of the words for each topic.
  * [acknowledgement_triple.json](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/output/acknowledgement_triple.json): output of the **topic modelling and clustering part** that contains the triples of that pairs the entities extracted on the acknowledgements with each paper. Also contains the type of entity.
* On the [src/CSV](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src/CSV) directory you will have [data-with-links.csv](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/CSV/data-with-links.csv) that is the result of the generate CSV steps and from adding any missing information.
* On the [src/rdf](https://github.com/YizzaJ/PDF_Knowledge_Graph/tree/main/src/rdf) directory you can find the [KG.nt](https://github.com/YizzaJ/PDF_Knowledge_Graph/blob/main/src/rdf/KG.nt) that was generated.
  **

## Contact

For any issue contact any of the authors:

* Christian Dörpelkus (c.dorpelkus@alumnos.upm.es)
* Miguel Yanez (m.yanez@alumnos.upm.es).
* Jesus Hernandez (jesus.hernandezp@alumnos.upm.es).
