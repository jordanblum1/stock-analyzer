from openai import OpenAI

def summarize_article(article, openai_key):
    client = OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Summarize the following news article"},
            {"role": "user", "content": article}
        ],
        model="gpt-3.5-turbo"
    )
    return response.choices[0].message.content
