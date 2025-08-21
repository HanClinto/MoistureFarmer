from pydantic import BaseModel

class Location(BaseModel):
    x: int
    y: int

    def distance_to(self, other: 'Location') -> float:
        # Calculate the Manhattan distance to another location
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return NotImplemented
        return self.x == other.x and self.y == other.y
    
    def __add__(self, other: 'Location') -> 'Location':
        if not isinstance(other, Location):
            return NotImplemented
        return Location(x=self.x + other.x, y=self.y + other.y)
    
    def __sub__(self, other: 'Location') -> 'Location':
        if not isinstance(other, Location):
            return NotImplemented
        return Location(x=self.x - other.x, y=self.y - other.y)
    
