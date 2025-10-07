import requests
import json

def ask_agent(question):
    response = requests.post(
        'http://138.124.101.59/chat',
        headers={'Content-Type': 'application/json'},
        json={'user_id': 'test', 'message': question},
        stream=True
    )
    
    print(f"\n🧑 YOU: {question}")
    print("🤖 AGENT: ", end='')
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                if data.get('type') == 'chunk':
                    print(data['content'], end='', flush=True)
    print("\n" + "="*60)

# Test questions
ask_agent("How many calories in 3 eggs?")
ask_agent("Create a beginner workout plan")
ask_agent("How many calories in chicken breast?")
