class RivalAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
