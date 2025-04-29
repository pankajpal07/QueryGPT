import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import CharacterTextSplitter
import psycopg2
from langchain_community.document_loaders import TextLoader

def initiate_indexing(chat_client, mem_client):
    chuking_schema()
    # generate_readable_format(chat_client, mem_client)

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
        max_tokens=150000,
    )

    f = open('output.json', 'w')
    f.write(response.choices[0].message.content)
    f.close()

def chuking_schema():
    # try:
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
            
            document = ''
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
                document += f"Table: {table_name}"

                # Step 3: Get columns in this table
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s;
                """, (schema_name, table_name))
                columns = cursor.fetchall()

                for column in columns:
                    col_name, col_type = column
                    document += f" - Column: {col_name} ({col_type})"
                documents.append(document)
                document = ''

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

            split_documents = text_splitter.create_documents(documents)

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
        print("Injection in Vector Store done successfully")
    # except Exception as e:
    #     print("❌ Error:", e)