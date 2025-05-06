import os
import time

def chat(chat_client, system_prompt, query):
    query_executed = False
    max_tries = 3
    print('🧠 Executing Query...: ', query)
    while not query_executed and max_tries > 0:
        try:
            # Execute the query
            response = chat_client.chat.completions.create(
                model=os.getenv('MODEL'),
                # response_format={"type": "json_object"},
                messages=[
                    { 'role': 'system', 'content': system_prompt },
                    { 'role': 'user', 'content': query }
                ],
                max_tokens=32768,
            )
            query_executed = True
            responseText = response.choices[0].message.content
            print('🤖: ', responseText)
            return responseText
        except Exception as e:
            print(f"Error executing query: {e}")
            max_tries -=1
            time.sleep(45)

def chat_with_json_response(chat_client, system_prompt, query):
    query_executed = False
    max_tries = 3
    print('🧠 Executing Query...: ', query)
    while not query_executed and max_tries > 0:
        try:
            # Execute the query
            response = chat_client.chat.completions.create(
                model=os.getenv('MODEL'),
                response_format={"type": "json_object"},
                messages=[
                    { 'role': 'system', 'content': system_prompt },
                    { 'role': 'user', 'content': query }
                ],
                max_tokens=32768,
            )
            query_executed = True
            responseText = response.choices[0].message.content
            print('🤖: ', responseText)
            return responseText
        except Exception as e:
            print(f"Error executing query: {e}")
            max_tries -=1
            time.sleep(45)
