# Graph Data Loader and Query System

You need to run demo_alex_dolia.ipynb

This project provides tools to load graph-structured data into a **Neo4j** database, process it for use with a **language model (LLM)**, and execute complex graph queries efficiently. The system is designed to handle data related to entities like **Papers**, **Authors**, **Journals**, and **Wikipages**, enabling advanced knowledge extraction and query generation.

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







# Optimizing LLMs for Graph Query Generation

## Objective
This project aims to enhance the performance of a Language Model (LLM) in generating precise, efficient, and contextually accurate graph queries (e.g., Cypher, SPARQL) for graph data related to **papers, authors, and journals**. By leveraging fine-tuning techniques such as **LoRA (Low-Rank Adaptation)** and **DPO (Direct Preference Optimization)**, we improve the model's understanding of graph schemas, relationships, and user intent to generate optimized and syntactically correct queries.

---

## Approach

### 1. Fine-Tuning with LoRA
**LoRA** introduces parameter-efficient adaptations to transformer models for domain-specific tasks while retaining the capabilities of the pre-trained model.

#### Steps:
1. **Pretrained Model Selection**
   - Use a base LLM like GPT-Neo, LLaMA, or GPT-3.5 optimized for natural language understanding.

2. **Dataset Preparation**
   - **Input:** Natural language questions and schema descriptions for papers, authors, and journals.  
   - **Output:** Corresponding graph queries.
   - **Example:**
     ```json
     {
       "input": "List all journals where 'John Doe' has published papers.",
       "schema": "Graph contains nodes: Paper, Author, Journal. Relationships: is_author_of, was_published_in.",
       "output": "MATCH (a:Author {name: 'John Doe'})-[:is_author_of]->(p:Paper)-[:was_published_in]->(j:Journal) RETURN DISTINCT j.name"
     }
     ```

3. **Model Adaptation**
   - Add LoRA layers to transformer components (e.g., `q_proj`, `v_proj`) to reduce fine-tuning parameter counts and computational cost.

4. **Training Process**
   - Tokenize inputs with a schema-aware tokenizer highlighting terms like `Paper`, `Author`, and `Journal`.
   - Train the LoRA-enhanced model to minimize query generation errors.

5. **Evaluation**
   - Use unseen datasets for validation.
   - Evaluate using BLEU, ROUGE, and execution success rates on Neo4j or SPARQL endpoints.

---

### 2. Fine-Tuning with DPO
**Direct Preference Optimization (DPO)** fine-tunes models by aligning their outputs with user preferences based on feedback.

#### Steps:
1. **Feedback Dataset Creation**
   - Collect feedback on generated queries:
     - **Positive feedback:** Accurate and efficient queries.
     - **Negative feedback:** Incorrect or suboptimal queries.
   - **Example:**
     ```json
     {
       "question": "Find all papers authored by 'Alice Smith' in 'Journal of AI'.",
       "schema": "Graph contains nodes: Paper, Author, Journal. Relationships: is_author_of, was_published_in.",
       "generated_queries": [
         {
           "query": "MATCH (a:Author {name: 'Alice Smith'})-[:is_author_of]->(p:Paper)-[:was_published_in]->(j:Journal {name: 'Journal of AI'}) RETURN p.title",
           "feedback": 1
         },
         {
           "query": "MATCH (j:Journal {name: 'Journal of AI'})-[:was_published_in]->(p:Paper)<-[:is_author_of]-(a:Author {name: 'Alice Smith'}) RETURN p.title",
           "feedback": 1
         },
         {
           "query": "MATCH (p:Paper {title: 'Alice Smith'})-[:was_published_in]->(j:Journal {name: 'Journal of AI'}) RETURN p.title",
           "feedback": 0
         }
       ]
     }
     ```

2. **Model Fine-Tuning**
   - Train the model to prioritize high-feedback queries by adjusting the log-probabilities during training.
   - Use reinforcement learning techniques (e.g., REINFORCE algorithm) for optimization.

3. **Evaluation**
   - Test query generation on diverse datasets.
   - Measure user satisfaction and query execution success rates.

---

## Datasets

### Sources for Training Data:
1. **Graph Query Examples**
   - Public datasets (e.g., Neo4j’s movie dataset) adapted for papers, authors, and journals.
   - Custom datasets derived from real-world publication graphs.

2. **Schema Documentation**
   - Input schema definitions for associating schema terms (e.g., `is_author_of`, `was_published_in`) with graph queries.

3. **Synthetic Data Generation**
   - Use pre-trained LLMs to generate diverse graph questions and their corresponding queries.

---

## Challenges and Mitigation

### Dataset Quality
- **Challenge:** Limited labeled data for specific graph schemas.
- **Mitigation:** Use synthetic data augmentation and transfer learning.

### Schema Generalization
- **Challenge:** Difficulty adapting to unseen schemas.
- **Mitigation:** Train on a variety of schema descriptions and develop schema embeddings.

### Performance Trade-offs
- **Challenge:** Fine-tuning may degrade general-purpose capabilities.
- **Mitigation:** Use parameter-efficient methods like LoRA to retain the base model’s versatility.

---

## Success Metrics

### 1. Query Accuracy
- BLEU or ROUGE scores comparing generated queries to ground-truth data.

### 2. Execution Success
- Rate of successful query executions on live graph databases.

### 3. User Satisfaction
- Feedback from surveys assessing the model’s ability to meet user intent.

### 4. Efficiency
- Evaluation of model latency and token usage during query generation.

---

## Conclusion
Fine-tuning an LLM using **LoRA** and **DPO** offers an efficient, scalable approach to optimize graph query responses for datasets involving **papers, authors, and journals**. LoRA ensures computational efficiency, while DPO aligns outputs with user preferences. These techniques enable the development of advanced, schema-aware agentic systems capable of delivering accurate, user-aligned graph queries.

