class SkeletonGenerator:
    def __init__(self, endpoint="http://172.16.30.8:11434/api/chat", model="gemma:2b"):
        self.endpoint = endpoint
        self.model = model
    def generate_skeleton(self, prompt):
        import requests
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": f"Generate a markdown structure for: {prompt}"}],
                "stream": False,
                "format": "json"
            }
            response = requests.post(self.endpoint, json=payload, timeout=10)
            return response.json()["message"]["content"]
        except Exception as e:
            return None
