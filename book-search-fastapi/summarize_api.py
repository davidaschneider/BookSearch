import asyncio
from typing import List
from ollama import ChatResponse, AsyncClient, chat

    

PROMPT_TEMPLATE = '''Summarize the information contained in the following JSON object about a book.  
            Provide just a paragraph of text, in clear English, 
            summarizing the JSON as one would expect to see on a library or bookstore website, but
            with no other preface or text telling me what you're doing.  Assume all books have already been released.
            Be sure to mention the title and 
            author upfront. Only use information found in the JSON. {}'''


def summarize(json: str, model='llama3.2') -> str:
    '''Summarize information contained in a JSON blob about a book, for display to an end user.'''
    message = {
            'role': 'user',
            'content': PROMPT_TEMPLATE.format(json),
        }
    response: ChatResponse = chat(model, messages=[        
        message
    ])
    return response.message.content

async def summarize_multiple_async(jsons: List[str], model='llama3.2'):
    tasks = []
    for json in jsons:
        tasks.append(summarize_async(json, model))
    return await asyncio.gather(*tasks) 

async def summarize_async(json: str, model = 'llama3.2') -> str:
    '''An async function to summarize information contained in a JSON blob about a book, for display to an end user.'''
    message = {
            'role': 'user',
            'content': PROMPT_TEMPLATE.format(json),
        }
    try:
        response = await AsyncClient().chat(model=model, messages=[message])
        return response.message.content
    except Exception as e:
        # should probably log something...
        return None
