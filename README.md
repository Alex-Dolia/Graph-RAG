# Graph Data Loader and Query System

You need to run demo_alex_dolia.ipynb

This project provides tools to load graph-structured data into a **Neo4j** database, process it for use with a **language model (LLM)**, and execute complex graph queries efficiently. The system is designed to handle data related to entities like **Papers**, **Authors**, **Journals**, and **Wikipages**, enabling advanced knowledge extraction and query generation.


### Questions to Answer

1. **Which authors have collaborated with Alice Smith on any papers?**  
2. **What are the most influential papers in “Symbolic Artificial Intelligence”?**  
3. **What is the expertise of “Henry Davis”?**  
4. **What is the focus of the *Journal of Artificial Intelligence Research* and how does it differentiate from other journals?**  


### Answering Approaches (see [demo_alex_dolia.ipynb](https://github.com/Alex-Dolia/Graph-RAG/blob/main/demo_alex_dolia.ipynb))

1. **[Neo4j queries](https://github.com/Alex-Dolia/Graph-RAG/blob/main/utils/utilsv2.py) that are run in Python or directly in Neo4J**
2. **[Neo4j queries + Prompt Completion with LLM](https://github.com/Alex-Dolia/Graph-RAG/blob/main/utils/utilsv2.py)**
3. **Examples of [Neo4j queries, FewShotPromptTemplate and GraphCypherQAChain](https://github.com/Alex-Dolia/Graph-RAG/blob/main/utils/graph_rag.py)**

---
## Features of `GraphRAG`

### 1. Dynamic Graph Connectivity
- Establishes a seamless connection to a Neo4j database using the `Neo4jGraph` class.
- Automatically refreshes and retrieves the schema to ensure up-to-date metadata.

### 2. Graph Data Transformation
- Automatically formats nodes with taglines for better readability and context.
- Updates relationships between entities such as authorship, citations, and mentions.

### 3. Data Loading into Neo4j
- Provides a modular, class-based system for loading nodes and edges into a Neo4j database.
- Handles entity-specific attributes like `tagline` for Papers, Journals, and Wikipages.

### 4. Predefined Examples for Cypher Queries
- Provides a robust set of examples mapping common user questions to Cypher queries.
- Examples include counting citations, identifying collaborators, and extracting expertise.

### 5. Custom Query Prompt Template
- Utilizes `FewShotPromptTemplate` to build a prompt for translating natural language questions into Cypher queries.
- Includes predefined examples and schema details for enhanced accuracy.
- Supports flexible input variables like `question` and `schema`.

### 6. Language Model Integration
- Integrates with OpenAI's `ChatGPT` (via `ChatOpenAI`) for Cypher query generation and results summarization.
- Configurable parameters, including temperature for output tuning.

### 7. Neo4j Graph Question-Answering Chain
- Employs `GraphCypherQAChain` to process user queries.
- Combines the power of Neo4j for data retrieval and LLM for natural language outputs.
- Supports advanced options, such as verbose logging and bypassing certain query restrictions.

### 8. Invoke Method for Query Execution
- The `invoke` method simplifies the process of sending questions to the system.
- Converts user queries into Cypher commands, executes them on the database, and returns results.

## Example Use Cases
- Count the number of citations and mentions for papers.
- Identify authors collaborating on specific publications.
- Determine the expertise of an individual based on authored documents.
- Differentiate the focus areas of journals, like the "Journal of Artificial Intelligence Research."

## Benefits
- **Seamless Integration**: Combines Neo4j's graph capabilities with OpenAI's advanced LLMs for an enhanced question-answering experience.
- **Scalability**: Modular design ensures flexibility for extending examples and adapting the chain to new use cases.
- **Context-Aware Responses**: Uses graph schema information and Cypher examples to produce precise and contextually relevant answers.

---

## Setup Instructions

### 1. Prerequisites

- **Neo4j Database**:
  - Install and set up Neo4j: [Neo4j Installation Guide](https://neo4j.com/docs/operations-manual/current/installation/)
  - Start your Neo4j instance and ensure you have connection credentials.

- **Python Environment**:
  - Python 3.8 or higher.
  - Install required libraries using `pip`.

### 2. Install Dependencies

```bash
pip install neo4j langchain openai textwrap


## 3. Environment Variables

Ensure the following environment variables are set up, or replace them in the code directly with your Neo4j credentials and OpenAI API key.

| Variable          | Description                                      |
|-------------------|--------------------------------------------------|
| `NEO4J_URI`       | Neo4j URI (e.g., `bolt://localhost:7687`)         |
| `NEO4J_USERNAME`  | Neo4j username (default: `neo4j`)                |
| `NEO4J_PASSWORD`  | Neo4j password                                   |
| `DATABASE`        | Neo4j database name (default: `neo4j`)           |
| `OPENAI_API_KEY`  | OpenAI API key for LLM integration               |

You can either set these variables in your environment or modify the code to include the credentials directly.


## Usage Instructions

### 1. Updating the JSON Data
The `update_json` function formats input graph data by:
- Adding taglines for better descriptions.
- Updating relationship edges based on entity types.

```python
from your_module import update_json

data = {
    "nodes": [...],
    "edges": [...]
}
updated_data = update_json(data)
```

### 2. Loading Data into Neo4j

The `GraphLoader` class handles the loading of data into Neo4j. It processes nodes and relationships based on the entity types.

```python
from your_module import GraphLoader

# Initialize the loader
loader = GraphLoader(uri="bolt://localhost:7687", username="neo4j", password="password", database="neo4j")

# Load data
loader.load_data(updated_data)

# Close the connection

loader.close()
```
This will merge nodes and relationships into the Neo4j database based on the provided data.

### 3. Executing Queries

Use the `GraphSDK` class to execute Cypher queries on the Neo4j database. This class allows for flexible query execution and returns results as formatted strings.

```python
from your_module import GraphSDK

# Initialize the SDK
sdk = GraphSDK(uri="bolt://localhost:7687", username="neo4j", password="password", database="neo4j")

# Execute a query
query = "MATCH (p:Paper) RETURN p.tagline LIMIT 5"
result = sdk.execute_query(query, {})
print(result)

# Close the connection
sdk.close()
```

This code will execute the query on the Neo4j instance and print the result.
