from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

class GraphRAG(object):
    """docstring for ClassName"""
    def __init__(self, NEO4J_URI, 
                       NEO4J_USERNAME,
                       NEO4J_PASSWORD,
                       NEO4J_DATABASE,
                       examples = None,
                       verbose=False):

        graph = Neo4jGraph(
                url      = NEO4J_URI,
                username = NEO4J_USERNAME,
                password = NEO4J_PASSWORD,
                database = NEO4J_DATABASE,
        )
        # Refresh and print the schema
        graph.refresh_schema()

        if examples is None:
           examples = [
           { "question": "Provide the number of citations and mentionings for all papers",
             "query": """MATCH (doc)<-[r]-(citation)
             WHERE type(r) IN ['cited', 'mention_paper', 'mention_concept']
             WITH doc, COUNT(r) AS CitationCount
             ORDER BY CitationCount DESC
             RETURN doc.id, doc.tagline, CitationCount
             """
           },
           { "question": "What paper has the most of citations and paper mentionings?",
             "query": """MATCH ()-[r]->(p:Paper)
             WHERE type(r) IN ['cited', 'mention_paper', 'mention_concept']
             WITH p, COUNT(r) AS CitationCount
             ORDER BY CitationCount DESC
             RETURN p.id, p.name, CitationCount
             LIMIT 1
             """
           },
           { "question": "What is the most influential papers in 'Symbolic Artificial Intelligence'?",
             "query": """MATCH ()-[r]->(p:Paper)<-[m]-(: Entity: {{name: 'Symbolic Artificial Intelligence'}}) 
             WHERE (type(r) IN ['cited', 'mention_paper', 'mention_concept']) AND
                   (type(m) IN ['cited', 'mention_paper', 'mention_concept'])
             WITH p, COUNT(r) AS CitationCount
             ORDER BY CitationCount DESC
             RETURN p.id, p.name, CitationCount
             LIMIT 1
             """
           },                
           {
             "question": "Which authors have collaborated with Alice Smith on any papers?",
             "query": """MATCH (author1:Person {{name: 'Alice Smith'}})-[:is_author_of]->(doc:Document)
             WHERE doc.type IN ["Paper", "Wikipage"]
             MATCH (doc)<-[:is_author_of]-(author2:Person {{type: "Person"}})
             WHERE author1 <> author2
             WITH COLLECT(DISTINCT author2.name) AS collaborators
             RETURN 'The collaborators of ' + 'Alice Smith' + ' are: ' + REDUCE(s = '', name IN collaborators | s + CASE s WHEN '' THEN '' ELSE ', ' END + name)
             """,
           },
           {
             "question": "How many authors are there?",
             "query": "MATCH (a:Person)-[:is_author_of]->(:Paper) RETURN count(DISTINCT a)",
           },
           {
             "question": "Which author published the paper Combining Symbolic and Subsymbolic Methods?",
             "query": "MATCH (p:Paper {{name: 'Combining Symbolic and Subsymbolic Methods'}})<-[:is_author_of]-(a) RETURN a.name",
           },
           {
             "question": "How many papers has Alice Smith published?",
             "query": "MATCH (a:Person {{name: 'Alice Smith'}})-[:is_author_of]->(p:Paper) RETURN count(p)",
           },
           {
             "question": "What is the expertise of Henry Davis?",
             "query": """
             MATCH (person:Person {{name: 'Henry Davis'}})-[:is_author_of]->(doc:Document)
             WITH COLLECT(doc.tagline) AS taglines
             RETURN COALESCE(REDUCE(s = '', tagline IN taglines | s + ' ' + tagline), 'No taglines available') AS result
             """,  
           },
           {
             "question": "What is the focus of the 'Journal of Artificial Intelligence Research' and how does it differentiate from other journals?",
             "query": """
             MATCH (p:Paper)-[:was_published_in]->(j:Journal)
             WITH 
             j.name AS journal_name,
             COLLECT(p.tagline) AS paper_taglines
             RETURN 
             apoc.text.join(COLLECT(
             CASE 
               WHEN journal_name = 'Journal of Artificial Intelligence Research' THEN 
                'Papers and Abstracts from "' + 'Journal of Artificial Intelligence Research' + '":\n' + 
                apoc.text.join(paper_taglines, ' \n') + '\n'
               ELSE 
                'Other Journal: ' + journal_name + '\nPapers and Abstracts:\n' + 
                apoc.text.join(paper_taglines, ' \n') + '\n'
             END
             ), '\n') AS result
             """,
           },
           ]
        
        example_prompt = PromptTemplate.from_template(
              "User input: {question}\nCypher query: {query}"
        )
        prompt = FewShotPromptTemplate(
                 examples=examples,
                 example_prompt=example_prompt,
                 prefix="You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.\n\nHere is the schema information\n{schema}.\n\nBelow are a number of examples of questions and their corresponding Cypher queries.",
                 suffix="User input: {question}\nCypher query: ",
                 input_variables=["question", "schema"],
        )

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.chain = GraphCypherQAChain.from_llm(
                         graph=graph,
                         llm=llm,
                         cypher_prompt=prompt,
                         verbose=verbose,
                         allow_dangerous_requests=True,
        )
        
    def invoke(self, msg):
        return self.chain.invoke(msg)