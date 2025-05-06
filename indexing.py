import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import CharacterTextSplitter
import psycopg2
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
import json
from neo4j import GraphDatabase
from chat import chat_with_json_response, chat

def initiate_indexing(chat_client, mem_client):
    # chuking_schema_and_save_to_vector_db()
    # generate_readable_format(chat_client, mem_client)
    # save_to_knowledge_graph(mem_client, chat_client)
    save_memory(mem_client, chat_client)

def generate_readable_format(chat_client, mem_client):
    f = open("example1.sql", "r")

    system_prompt = f"""
    You are a helpful assistant who is expert in analysing the database schema. You are provided with the database schema and your task is to convert it into an readable format
    which is described in the example below.

    Rules:
     - You will only parse the schema of the database which is postgresql otherwise don't parse it just gives an error message.
     - Carefully analyze the provided schema
     - Analyse the output youself first before giving to the user
    
    Output:
    {{
        'schemas': [
            {{
                'name': 'string',
                'tables': [
                    {{
                        'name': 'string',
                        'cols': [
                            {{
                                'col': 'string',
                                'data_type': 'string'
                            }}
                        ]
                    }}
                ],
                'relationships': [
                    {{
                        'from_table': 'string',
                        'to_table': 'string',
                        'from_column': 'string',
                        'to_column': 'string'
                    }}
                ]
            }}
        ]
    }}

    Example:
    User Query: Create the readable format for the given database schema
    {f.read()}
    Output: {{'schemas': [{{'name': 'bonga_cm', 'tables': [{{'name': 'user', 'cols': [{{'col': 'id', 'data_type': 'int'}}, {{'col': 'name', 'data_type': 'string'}}, {{'col': 'email', 'data_type': 'string'}}, {{'col': 'admin_user_id', 'data_type': 'int'}}]}}, {{'name': 'company', 'columns': [{{'col': 'id', 'data_type': 'int'}}, {{'col': 'name', 'data_type': 'string'}}, {{'col': 'admin_user_id', 'data_type': 'int'}}]}}], 'relationships': [{{'from_table': 'user', 'to_table': 'company', 'from_column': 'id', 'to_column': 'admin_user_id'}}]}}]}}
    """

    f = open("schema.sql", "r")
    messages = [
        { 'role': 'system', 'content': system_prompt },
        { 'role': 'user', 'content': f'Create the readable format for the given database schema: {f.read()}' }
    ]

    response = chat_client.chat.completions.create(
        model=os.getenv('MODEL'),
        response_format={"type": "json_object"},
        messages=messages,
        max_tokens=32768,
    )

    f = open('output.json', 'w')
    f.write(response.choices[0].message.content)
    f.close()

def chuking_schema_and_save_to_vector_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        cursor = conn.cursor()

        # Step 1: Get non-system schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema');
        """)
        schemas = cursor.fetchall()

        for schema in schemas:
            schema_name = schema[0]
            print(f"\n📂 Schema: {schema_name}")
            # create collection with schema name
            
            documentContent = ''
            # Step 2: Get tables in this schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE';
            """, (schema_name,))
            tables = cursor.fetchall()

            documents = []
            for table in tables:
                table_name = table[0]
                documentContent += f"Table: {table_name}"

                # Step 3: Get columns in this table
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s;
                """, (schema_name, table_name))
                columns = cursor.fetchall()

                columnsText = []
                for column in columns:
                    col_name, col_type = column
                    columnsText.append(col_name + ': ' + col_type)
                
                # Step 4: Get all foreign keys for this table
                cursor.execute("""
                    SELECT 
                        kcu.column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM 
                        information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema = %s
                        AND tc.table_name = %s;
                """, (schema_name, table_name))

                relations = []

                fks = cursor.fetchall()
                for fk in fks:
                    local_col, ref_schema, ref_table, ref_col = fk
                    relations.append(local_col + '→' + ref_schema + '.' + ref_table + '(' + ref_col + ')')
                document = Document(
                    page_content=documentContent,
                    metadata={
                        "schema": schema_name,
                        "table": table_name,
                        "columns": columnsText,
                        "relations": relations
                    }
                )
                documents.append(document)
                documentContent = ''

            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GEMINI_API_KEY"))

            text_splitter = CharacterTextSplitter(
                separator=",",
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                is_separator_regex=False,
            )

            # loader = TextLoader(documents)
            # loaded_docs = loader.load()
            # print(json.dumps(documents))
            split_documents = text_splitter.split_documents(documents)

            QdrantVectorStore.from_documents(
                documents=split_documents,
                # connection=connection'
                api_key=os.getenv('QDRANT_API_KEY'),
                host=os.getenv('QDRANT_HOST'),
                port=6333,
                collection_name=schema_name,
                embedding=embeddings
            )
            # vector_store.add_documents(split_documents)
        cursor.close()
        conn.close()
        print("✅ Injection in Vector Store done successfully")
    except Exception as e:
        print("❌ Error:", e)

def fetch_all_documents_one_by_one(collection_name, host='localhost', port=6333, batch_size=50):
    
    scroll_offset = None

    while True:
        response = QdrantVectorStore.scroll(
            collection_name=collection_name,
            scroll_filter=None,  # No filters — fetch all
            limit=batch_size,
            offset=scroll_offset,
            with_payload=True,
            with_vectors=False  # Set True if you also want the vectors
        )

        points, scroll_offset = response

        if not points:
            break

        for point in points:
            print("🔹 ID:", point.id)
            print("   Payload:", point.payload)
            print("   Vector: Not fetched (set with_vectors=True if needed)\n")

def save_to_knowledge_graph(mem_client, chat_client):
    driver = GraphDatabase.driver(os.getenv('NEO4J_URL'), auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD')))

    system_prompt = """
    You are a helpful assistant for converting table details into a simple message that creates relation to save that into a knwoledge graph. You are provided with the JSON containing schema name, table name and column name with column type,
    your job is to convert the provided json into cypher queries.

    Rules:
    - You will only use the provided JSON to create the cypher queries.
    - The output should be in the form of array of strings i.e., I can parse it as json.
    - You will not hallucinate or assume anything.
    - You will not use any other data or information to create the cypher queries.
    - Verify the output yourself before giving to the user.

    Output will be array of string something like this: 
    [
        "CREATE
            (table_name:Person {name: 'Charlie Sheen', bornIn: 'New York', chauffeurName: 'John Brown'}),
            (martin:Person {name: 'Martin Sheen', bornIn: 'Ohio', chauffeurName: 'Bob Brown'}),
            (michael:Person {name: 'Michael Douglas', bornIn: 'New Jersey', chauffeurName: 'John Brown'}),
            (oliver:Person {name: 'Oliver Stone', bornIn: 'New York', chauffeurName: 'Bill White'}),
            (rob:Person {name: 'Rob Reiner', bornIn: 'New York', chauffeurName: 'Ted Green'}),
            (wallStreet:Movie {title: 'Wall Street'}),
            (theAmericanPresident:Movie {title: 'The American President'}),
            (charlie)-[:ACTED_IN]->(wallStreet),
            (martin)-[:ACTED_IN]->(wallStreet),
            (michael)-[:ACTED_IN]->(wallStreet),
            (martin)-[:ACTED_IN]->(theAmericanPresident),
            (michael)-[:ACTED_IN]->(theAmericanPresident),
            (oliver)-[:DIRECTED]->(wallStreet),
            (rob)-[:DIRECTED]->(theAmericanPresident)"
    ]

    Example:
    User Query: Create the cypher queries for the given database schema
    {
        "schema": "public",
        "table": "user_reset_token",
        "columns": [
            "already_used: boolean",
            "is_active: boolean",
            "is_deleted: boolean",
            "created_on: timestamp without time zone",
            "id: bigint",
            "updated_on: timestamp without time zone",
            "user_id: bigint",
            "otp: character varying"
        ]
    }
    Output:
    [
        "CREATE (user_reset_token: Table {name: 'user_reset_token'}),
           (user_reset_token__already_used: Column {name: 'already_used', type: 'boolean'}),
           (user_reset_token__is_active: Column {name: 'is_active', type: 'boolean'}),
           (user_reset_token__is_deleted: Column {name: 'is_deleted', type: 'boolean'}),
           (user_reset_token__created_on: Column {name: 'created_on', type: 'timestamp without time zone'}),
           (user_reset_token__id: Column {name: 'id', type: 'bigint'}),
           (user_reset_token__updated_on: Column {name: 'updated_on', type: 'timestamp without time zone'}),
           (user_reset_token__user_id: Column {name: 'user_id', type: 'bigint'}),
           (user_reset_token__otp: Column {name: 'otp', type: 'character varying'}),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__already_used),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__is_active),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__is_deleted),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__created_on),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__id),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__updated_on),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__user_id),
           (user_reset_token)-[:HAS_COLUMN]->(user_reset_token__otp)"
    ]

    Example:
    User Query: Create the cypher queries for the given schema relations
    {
        "relations": [
            "user_reset_token__user_id→user__id"
            "company__admin_user_id→user__id"
        ]
    }
    Output:
    [
        "MATCH (src:Table {name: 'user_reset_token'})-[:HAS_COLUMN]->(src_col:Column {name: 'user_id'}), (dst:Table {name: 'user'})-[:HAS_COLUMN]->(dst_col:Column {name: 'id'})
            MERGE (src_col)-[:HAS_REFERENCE]->(dst_col);",
        "MATCH (src:Table {name: 'company'})-[:HAS_COLUMN]->(src_col:Column {name: 'admin_user_id'}), (dst:Table {name: 'user'})-[:HAS_COLUMN]->(dst_col:Column {name: 'id'})
            MERGE (src_col)-[:HAS_REFERENCE]->(dst_col);"
    ]
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        cursor = conn.cursor()
        # Step 1: Get non-system schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema');
        """)
        schemas = cursor.fetchall()
        
        for schema in schemas:
            relations = []
            schema_name = schema[0]
            print(f"\n📂 Schema: {schema_name}")
            # create collection with schema name
            
            documentContent = ''
            # Step 2: Get tables in this schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE';
            """, (schema_name,))
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                documentContent += f"Table: {table_name}"

                # Step 3: Get columns in this table
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s;
                """, (schema_name, table_name))
                columns = cursor.fetchall()

                columnsText = []
                for column in columns:
                    col_name, col_type = column
                    columnsText.append(col_name + ': ' + col_type)

                cursor.execute("""
                    SELECT 
                        kcu.column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM 
                        information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema = %s
                        AND tc.table_name = %s;
                """, (schema_name, table_name))

                fks = cursor.fetchall()
                for fk in fks:
                    local_col, ref_schema, ref_table, ref_col = fk
                    relations.append(table_name + '__' + local_col + '→' + ref_table + '__' + ref_col)
                metadata = {
                    "schema": schema_name,
                    "table": table_name,
                    "columns": columnsText
                }

                # TODO: Request llm model to create cypher query for schema, table and columns
                response = chat_with_json_response(chat_client, system_prompt, f'Create the cypher queries for the given database schema: {json.dumps(metadata)}')
                jsonResponse = json.loads(response)
                print("Cypher Queries for table", table_name, ":", response)
                for query in jsonResponse:
                    with driver.session() as session:
                        result = session.run(query, {})
                        print("Cypher Query Result:", result)
                documentContent = ''
            
            # TODO: Request llm model to create cypher queries for relations in the schema
            metadata = {
                "schema": schema_name,
                "relations": relations
            }
            response = chat_with_json_response(chat_client, system_prompt, f'Create the cypher queries for the given schema relations: {json.dumps(metadata)}')
            jsonResponse = json.loads(response)
            print("Cypher Queries for relations", schema_name, ":", response)
            for query in jsonResponse:
                with driver.session() as session:
                    result = session.run(query, {})
                    print("Cypher Query Result:", result)
        print("✅ Injection in Memory done successfully")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn:
            conn.close()
        if driver:
            driver.close()

def save_memory(mem_client, chat_client):
    system_prompt = """
        You are a Memory-Aware Fact Extraction Agent, an advanced AI designed to
        systematically analyze input content, extract structured knowledge, and maintain an
        optimized memory store. Your primary function is information distillation
        and knowledge preservation with contextual awareness.

        Tone: Professional analytical, precision-focused, with clear uncertainty signaling

        Example:
        Create a memory for the following content:
        {
            "schema": "public",
            "table": "token",
            "columns": [
                "expired: boolean",
                "is_valid: boolean",
                "revoked: boolean",
                "id: bigint",
                "user_id: bigint",
                "token: character varying",
                "token_type: character varying"
            ]
        }

        This is a table with name token and it has the following columns:
        - expired: boolean
        - is_valid: boolean
        - revoked: boolean
        - id: bigint
        - user_id: bigint
        - token: character varying
        - token_type: character varying
        It's column user_id is related to id column of users table in public schema.

        Example:
        Create a memory for the following content:
        {
            "relations": [
                "user_reset_token__user_id→user__id"
                "company__admin_user_id→user__id"
            ]
        }

        Ok, these are relations with the following details:
        - user_id column of user_reset_token table is related to id column of user table in public schema.
        - admin_user_id column of company table is related to id column of user table in public schema.
    """

    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        cursor = conn.cursor()
        # Step 1: Get non-system schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
        """)
        schemas = cursor.fetchall()
        
        for schema in schemas:
            relations = []
            schema_name = schema[0]
            print(f"Schema: {schema_name}")
            # create collection with schema name
            
            documentContent = ''
            # Step 2: Get tables in this schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE';
            """, (schema_name,))
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                documentContent += f"Table: {table_name}"

                # Step 3: Get columns in this table
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s;
                """, (schema_name, table_name))
                columns = cursor.fetchall()

                columnsText = []
                for column in columns:
                    col_name, col_type = column
                    columnsText.append(col_name + ': ' + col_type)

                cursor.execute("""
                    SELECT 
                        kcu.column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM 
                        information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema = %s
                        AND tc.table_name = %s;
                """, (schema_name, table_name))

                fks = cursor.fetchall()
                for fk in fks:
                    local_col, ref_schema, ref_table, ref_col = fk
                    relations.append(table_name + '__' + local_col + '→' + ref_table + '__' + ref_col)
                metadata = {
                    "schema": schema_name,
                    "table": table_name,
                    "columns": columnsText
                }

                query = f'Create the cypher queries for the given database schema: {json.dumps(metadata)}'
                messages=[
                    { 'role': 'system', 'content': system_prompt },
                    { 'role': 'user', 'content': query }
                ]
                response = chat(chat_client, system_prompt, query)
                messages.append(
                    { "role": "assistant", "content": response }
                )
                mem_client.add(messages, schema_name)
                documentContent = ''
            
            metadata = {
                "schema": schema_name,
                "relations": relations
            }
            query = f'Create the cypher queries for the given schema relations: {json.dumps(metadata)}'
            response = chat(chat_client, system_prompt, query)
            messages.append(
                { "role": "assistant", "content": response }
            )
            mem_client.add(messages, schema_name)
        print("✅ Injection in Memory done successfully")
    # except Exception as e:
    #     print("❌ Error:", e)
    finally:
        if conn:
            conn.close()