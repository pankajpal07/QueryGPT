from langchain_community.utilities import SQLDatabase

def initiate_indexing(mem_client):

    db = SQLDatabase.from_uri(
        "postgresql+psycopg2://postgres:Avp2#Y5R;{K.m(8t:&qugP@178.79.166.161:5432/postgres"
    )
    print("Database Schema", db.table_info)

    system_prompt = f"""
    You are a helpful assistant for indexing data to a knwoledge graph from database schema. You are provided with the database schema and your task is to index the data to a knowledge graph.
    You will be provided with the ddl of the database which is in postgreSQL format and you have to save that in knowledge graph using cypher language. There might be possiblity that
    there are multiple number of schemas available inside a single database, so you have to create routing for those schemas. You will perform the following tasks:
    - Parsing: Parse the DDL and extract the table names, column names, data types, and relationships between tables.
    - Routing: If multiple schemas are present, create routing for each schema.
    - Vectorizing: Create vector data for each table and its columns.
    - Scripting: Create cypher queries to save the data in to the knowledge graph.
    - Saving: Save the data in to the knowledge graph using the cypher queries.
    - Verifying: Verify the data in the knowledge graph using cypher queries.
    - Reporting: Report the status of the indexing process.

    Example:
    User Query: Create the knowledge graph for the following database schema.
        Database: bonga
            Schema: bonga_um
                Table: users
                    Column: id (int)
                    Column: name (string)
                    Column: email (string)
                Table: company
                    Column: id (int)
                    Column: name (string)
                    Column: address (string)
                    Column: admin_user_id (int)
                Relationships:
                    - user.id ← company.admin_user_id
            Schema: bonga_cm
                Table: contact
                    Column: id (int)
                    Column: name (string)
                    Column: email (string)
                Table: list
                    Column: id (int)
                    Column: name (string)
                Table: contact_list
                    Column: id (int)
                    Column: contact_id (int)
                    Column: list_id (int)
                Relationships:
                    - contact.id ← contact_list.contact_id
                    - list.id ← contact_list.list_id
    Output: {'step': 'parsing', 'content': ''}

    Use the schema below to index the data to knowledge graph.
    {db.table_info}
    """

    messages = [
        { 'role': 'system', 'content': system_prompt },
        { 'role': 'user', 'content': "Index the data to knowledge graph." }
    ]

    mem_client.add(
        messages,
        "postgresql_knowledge_graph"
    )

def parse_postgresql_schema():

    f = open("demofile.txt", "r")

    system_prompt = f"""
    You are a helpful assistant for parsing the postgreSQL schema. You are provided with the database schema and your task is to convert it into an LLM-readable format 
    which is described in the example below.

    Rules:
    - You will only parse the schema of the database which is postgresql otherwise don't parse it just gives an error message.
    - You work on start, plan, action, observe, verify, output mode
    - Always perform one step at a time and wait for the input
    - Carefully analyze the provided schema
    - Analyse the output youself first before giving to the user

    Output:
    {
        'step': 'string',
        'content': 'string'
    }

    Example:
    User Query: Create the LLM-readable format for the given database schema
    {f.read()}

    Output: {'step': 'start', 'content': 'User wants to create the LLM-readable format for the given database schema. I will start by parsing the schema and extracting the table names, column names, data types, and relationships between tables.'}
    Output: {'step': 'plan', 'content': 'I will parse the schema and extract the table names, column names, data types, and relationships between tables. I will also create routing for each schema if multiple schemas are present.'}
    Output: {'step': 'action', 'function': 'save_routing', 'input': 'List of all the schemas and their description or functionality based on their names'}

    """
