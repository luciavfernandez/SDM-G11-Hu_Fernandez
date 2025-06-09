# SDM-G11-Hu_Fernandez
In this repository, you will find all the corresponding files to the different instructions related to the Assignment 2: Knowledge Graphs

1## Installation

Take into consideration the following installations:
1.GraphDB as explained in the corresponding Assignment paper
2. An active repository made within the system, in this case the repository is called "KnowledgeGraphAssignment2"
3. Having the proper configuration in the repository. Also, it is preferable to have admin default username (otherwise, please change the corresponding python files).

2## Implementation
For this solution, we will be using the Terminal, open it in the directory of the project. The first step is to create a virtual environment, we did with python3, but one can choose to do it with conda or other environment managers, we chose this to avoid any possible versioning conflicts and keep a clean environment for our application. So we expect python to be installed and available in the terminal with either python3 or python commands. Now, you should go to the Directory where your files are located. You will need to install two libraries in the new environment as well, the respective code follows:

 ```
   python3 -m venv myenv
   source myenv/bin/activate
   pip install requests
   pip install rdflib SPARQLWrapper
   pip install pandas 
```

Finally, run the following commands to see the available files from the project and run each of python files in the given order, replace the square brackets with the proper name of the files.

 ```
   ls
   python [file_name].py
 ```

3## Source Codes


In this section we aim to explain the correct implementation and explaination per file, keep in mind that the Official documentation is found in the document __G11-Hu-Fernandez.pdf__.

1. Requesting Data - For this task, we need to request the paper data from the dblp.org API call. For that, run the python file defined as __request.py__. Additionally you can change the number of papers in the variable defined hits = 5 (In this case we are using only 5). This file creates the unstructured data file defined as __dblp.json__
2. For the current example, we are using the file __dblp_5.json__ that brings only 5 papers from the API.
3. TBOX Definition - Import the turtle file __G11-B1-Hu-Fernandez.ttl__ in the Repository (Import -> Upload RDF files). This is the TBOX schema. On the other hand, you need to run in the terminal the file __G11-B1-Hu-Fernandez.py__, where you can see the schema implementation for the graph.
4. ABOX Definition - For the ABOX (ingesting + statistics), run the code __G11-B2_2-Hu-Fernandez.py__. The output after running the code is the statistics in the terminal and also a turtle file defined as __G11-B2_2_ABOX-Hu-Fernandez .ttl__. The latter file is useful to see the resulting ABOX file.
5. Queries - For the two queries stated in the PDF file, we decided to add a simple text file called __G11-B2_3-Hu-Fernandez.txt__, the objective of the file is to have in handy and in another file the corresponding two queries analized for the assignment.

After running the files, you can easily turn your environment off:

 ```
   deactive
 ```


C'est fini !
