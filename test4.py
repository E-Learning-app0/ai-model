import requests

API_KEY = "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"  # ex: sk-or-xxxxxxxxxxxxx

URL = "https://openrouter.ai/api/v1/chat/completions"

def test_openrouter():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "user", "content": "Hello! Give me a JSON with one short question about databases."}
        ]
    }

    response = requests.post(URL, headers=headers, json=payload)
    print("Status code:", response.status_code)

    try:
        data = response.json()
        print("Response JSON: ", data)

        if "choices" in data:
            print("AI answer:", data["choices"][0]["message"]["content"])
        else:
            print("No 'choices' key in the response. Something went wrong.")
    except Exception as e:
        print("Error parsing JSON:", str(e))

if __name__ == "__main__":
    test_openrouter()
