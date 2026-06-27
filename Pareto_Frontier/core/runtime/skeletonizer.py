class SkeletonGenerator:
    def __init__(self, endpoint="http://172.16.30.8:11434/api/chat", model="gemma:2b"):
        self.endpoint = endpoint
        self.model = model
    def generate_skeleton(self, prompt):
        return "# Skeleton\n- Point 1\n- Point 2"
