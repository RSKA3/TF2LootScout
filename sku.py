from schema import Schema

class Sku():
    def __init__(self, API_KEY="9F67B4D4BF8B8B95E17BD50C4E550079"):
        schema = Schema()
        self.schema = schema.get_schema(API_KEY=API_KEY)

    def to_sku(self, item):
        pass    