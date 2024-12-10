from neo4j import GraphDatabase
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
import textwrap

def update_json(data):
    # Initialize the updated edges list
    updated_edges = data["edges"].copy()

    # Iterate over all nodes
    nodes = []
    for node in data["nodes"]:
        if   node["type"] == "Paper" or node["type"] == "Wikipage":
             sep1 = " " if node["title"   ].strip().endswith(".") else "."
             sep2 = " " if node["abstract"].strip().endswith(".") else "."
        if   node["type"] == "Paper":
             tagline = " Paper Title: "    + node["title"].strip() + sep1 + " Abstract: " + node["abstract"] + sep2
        elif node["type"] == "Journal":
             tagline = " Journal name: "   + node["name"]
        elif node["type"] == "Wikipage":
             tagline = " Wikipage Title: " + node["title"].strip() + sep1 + " Abstract: " + node["abstract"] + sep2
             wiki_id = node["id"]
             key_people = node.get("key_people", [])
             for person_id in key_people:
                 updated_edges.append({
                     "source": person_id,
                     "target": wiki_id,
                     "type": "is_author_of"
                 })
        else:
           tagline = "NONE"

        node["tagline"] = tagline
        nodes.append(node)    
        
    data["edges"] = updated_edges
    data["nodes"] = nodes
    return data

# Step 1: Load data into Neo4j
class GraphLoader:
    def __init__(self, uri, username, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self):
        self.driver.close()

    def load_data(self, data):
        with self.driver.session(database=self.database) as session:
            # Load nodes
            for node in data["nodes"]:
                if node["type"] == "Person":
                   session.run(
                                """
                                MERGE (n:Person {id: $id, type: $type, name: $name, tagline: $tagline})
                                SET n:Entity
                                """,
                                id=node["id"], type=node["type"], name=node.get("name", node.get("title")), tagline=node["tagline"]
                    ) 
                elif node["type"] == "Paper":
                    session.run(
                                """
                                MERGE (n:Paper {id: $id, type: $type, name: $name, tagline: $tagline})
                                SET n:Document
                                SET n:Entity
                                """,
                                id=node["id"], type=node["type"], name=node.get("name", node.get("title")), tagline=node["tagline"]
                    )
                elif node["type"] == "Journal":
                    session.run(
                                """
                                MERGE (n:Journal {id: $id, type: $type, name: $name, tagline: $tagline})
                                SET n:Document
                                SET n:Entity
                                """,
                                id=node["id"], type=node["type"], name=node.get("name", node.get("title")), tagline=node["tagline"]
                    )    
                elif node["type"] == "Wikipage":
                    session.run(
                                """
                                MERGE (n:Wikipage {id: $id, type: $type, name: $name, tagline: $tagline})
                                SET n:Document
                                SET n:Entity 
                                """,
                                id=node["id"], type=node["type"], name=node.get("name", node.get("title")), tagline=node["tagline"]
                    )       
            # Load edges
            for edge in data["edges"]:
                if edge["type"] == 'is_author_of':
                   session.run(
                       """
                       MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                       MERGE (a)-[r:is_author_of]->(b)
                       """,
                       source=edge["source"], target=edge["target"]
                       )
                elif edge["type"] == 'was_published_in':
                   session.run(
                       """
                       MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                       MERGE (a)-[r:was_published_in]->(b)
                       """,
                       source=edge["source"], target=edge["target"]
                       )
                elif edge["type"] == 'mention_concept':
                   session.run(
                       """
                       MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                       MERGE (a)-[r:mention_concept]->(b)
                       """,
                       source=edge["source"], target=edge["target"]
                       )
                elif edge["type"] == 'mention_paper':
                   session.run(
                       """
                       MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                       MERGE (a)-[r:mention_paper]->(b)
                       """,
                       source=edge["source"], target=edge["target"]
                       )                   
                elif edge["type"] == 'cited':
                   session.run(
                       """
                       MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                       MERGE (a)-[r:cited]->(b)
                       """,
                       source=edge["source"], target=edge["target"]
                       )                   
class GraphSDK:
    def __init__(self, uri, username, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self):
        self.driver.close()
  
    def execute_query(self, query: str, parameters: dict) -> str:
        """
        Execute a given Cypher query and return the result directly formatted as required.

        Args:
           query (str): The Cypher query to execute.
           parameters (dict): A dictionary of parameters to use in the query.

        Returns:
           str: The query result, already formatted as a string.
        """
        with self.driver.session(database=self.database) as session:
             result = session.run(query, **parameters)
             return result.single()[0]  # Assumes the query is structured to return the desired string.

    def generate_wrapped_text(self,
                              template: str,  
                              taglines: str, 
                              temperature: float = 0, 
                              max_tokens: int = 100,
                              model_name: str = 'gpt-3.5-turbo-instruct') -> str:
        """
        Generate and format text using an LLM based on the provided template and taglines.

        Args:
            template (str): The template to be used for expertise extraction.
            taglines (str): The input text to process.
            temperature (float): The temperature for the LLM (controls randomness). Default is 0.
            max_tokens (int): The maximum number of tokens for the LLM. Default is 100.
            model_name (str): The name of the model to use. Default is 'gpt-3.5-turbo-instruct'.

        Returns:
            str: The processed and wrapped output text.
        """
        # Initialize the LLM with specified parameters
        llm = OpenAI(model_name=model_name, temperature=temperature, max_tokens=max_tokens)

        # Set up the prompt template and chain
        expertise_prompt = PromptTemplate(input_variables=["text_input"], template=template)
        expertise_extraction_chain = LLMChain(llm=llm, prompt=expertise_prompt)
    
        # Run the chain with the input text
        expertise = expertise_extraction_chain.run(taglines)
    
        # Format the output text
        wrapped_text = textwrap.fill(expertise, width=100, break_long_words=False, replace_whitespace=False)
        return wrapped_text
