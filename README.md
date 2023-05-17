# PDF_Knowledge_Graph

## Description

This project refers to a PDF analyzer that by extracting their Abstracs and Acknowledgements, constructs a knowledge graph. This allows the user to have the files categorized regarding common themes and alsogenerate queries against them, being able to extract information such as the authors, organizations acknowledged, and the type of paper they represent. Additionally, the information extracted from the PDFs will be enriched using online sources such as [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) and the [OpenAlex API](https://openalex.org/).

### Parts of the project

This complex projects is divided into different parts regarding of the function they do. They were separated to allow the user to fix mistakes and so they can use their prefered models.

#### Preprocessing

This part refers to the data extraction from the PDF files and also their processing. We are using [Grobid](https://github.com/kermitt2/grobid) for the data extraction, and a python script to generate a *.json*  (*extracted.json*) file with the **Title, Abstract and Acknowledgements** parts from each of the files.

#### Topic Modeling, Clustering and Name Entity Recognition

This part of the project uses the output of the last one to classify each file according a topic and a cluster. Additionally, it extracts entities present on the **acknowledgements** section to enrich the final knowledge graph.
To tackle the task of clustering the files we are computing a distance matrix based on tf-idf vectors for the preprocessed paper abstracts. Given the distance matrix k-means or agglomerative clustering can be performed and evaluated with the silhouette score.
Moreover, we are using the LDA approach to compute topics as well based on the tf-idf vectors. The topic quality is evaluated using coherence.
In order to extract entities from the **acknowledgements** section of all papers we are using the [huggingface api](https://huggingface.co/Jean-Baptiste/roberta-large-ner-english?text=My+name+is+wolfgang+and+I+live+in+berlin) with a pretrained roberta ner model.

#### Generating the CSV

This process gathers all the information provided by the first to parts to generate a *.csv* (*data_with_links.csv*) that will be the input for the final formation of the knowledge graph. This file contains information such as the title, authors, organizations, date of publication, topic, cluster, ect.., and the enriched information extracted from other sources such as education of authors, type of paper, countries of the organizations, among others.

#### Web interface

With this, the user is going to be able to do queries to the knowledge graph. The information is represented with a table, so the user can get the complete information regarding their query.

## Requirements

To run this program you will need:

* System with Windows or Linux operating systems.
* Install [Docker](https://docs.docker.com/engine/install/).

## Installation Instructions

1. Clone this git project:

   `git clone https://github.com/YizzaJ/PDF_Knowledge_Graph.git`

## Execution Instructions

1. Run a docker server.
2. . Enter the *src/* directory since the rest of the instructions will be executed from there:
   `cd src`
3. Insert all the *.pdf* files inside the **PDFs** directory.
4. If you are using Windows run the `preprocessing.bat` file. If you are using Linux run `preprocessing.sh`.
   This will create two files inside the  output directory, `extracted.json` and `data-with-links.json`.
5. The data-with-links.json file should be used as one of the input files used in the CSV file generation step.

Using AI to create additional information

- The following steps are used to include additional information to enrich the knowledge graph.

6. Make sure that you have run the previous steps and there is an [extracted.json](data/extracted.json) file in the *data folder*
7. To perform clustering and topic modelling run `python ai_tasks/ai_tasks.py`
8. To perform NER run the [NER notebook](src/ai_tasks/NER.ipynb) manually

Adding the additional extracted data to the data source of the Knowledge Graph 

9. Place the files `abstract_ai_data.json`, `topic_id_list.json` and `acknowledgement_triple.json`, generated in the previous step, in the `src/output` folder.
10. If you are using Windows run the `generate_csv.bat` file. If you are using Linux run `generate_csv.sh`.
    This will create a CSV file inside the CSV directory named `data-with-links.csv.`

Knowledge Graph generation and Visualization step

11. If you are using Windows run the `generate_kg.bat` file. If you are using Linux run `generate_kg.sh`.
    This will create a container called `flask` that runs a web server to visualize the information contained in the Knowledge Graph. The expected output will be:

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
## Contact

For any issue contact any of the authors:

* Christian Dörpelkus (c.dorpelkus@alumnos.upm.es)
* Miguel Yanez (m.yanez@alumnos.upm.es).
* Jesus Hernandez (jesus.hernandezp@alumnos.upm.es).
