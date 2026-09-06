class Stack:
    """LIFO Stack implementation from scratch"""
    
    def __init__(self):
        self._items = []
    
    def push(self, item):
        """Add an item to the top of the stack"""
        self._items.append(item)
    
    def pop(self):
        """Remove and return the item from the top of the stack"""
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self._items.pop()
    
    def peek(self):
        """Return the item at the top without removing it"""
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self._items[-1]
    
    def is_empty(self):
        """Check if the stack is empty"""
        return len(self._items) == 0
    
    def size(self):
        """Return the number of items in the stack"""
        return len(self._items)
    
    def clear(self):
        """Remove all items from the stack"""
        self._items.clear()
