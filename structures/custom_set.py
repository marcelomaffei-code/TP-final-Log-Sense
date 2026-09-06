class CustomSet:
    """Set implementation from scratch using hash table"""
    
    def __init__(self, initial_capacity=16):
        self._capacity = initial_capacity
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]
    
    def _hash(self, item):
        """Simple hash function"""
        return hash(item) % self._capacity
    
    def _rehash(self):
        """Resize the hash table when load factor is high"""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        
        for bucket in old_buckets:
            for item in bucket:
                self.add(item)
    
    def add(self, item):
        """Add an item to the set"""
        bucket_index = self._hash(item)
        bucket = self._buckets[bucket_index]
        
        if item not in bucket:
            bucket.append(item)
            self._size += 1
            
            # Rehash if load factor > 0.75
            if self._size / self._capacity > 0.75:
                self._rehash()
    
    def remove(self, item):
        """Remove an item from the set"""
        bucket_index = self._hash(item)
        bucket = self._buckets[bucket_index]
        
        if item in bucket:
            bucket.remove(item)
            self._size -= 1
        else:
            raise KeyError(item)
    
    def contains(self, item):
        """Check if an item is in the set"""
        bucket_index = self._hash(item)
        return item in self._buckets[bucket_index]
    
    def is_empty(self):
        """Check if the set is empty"""
        return self._size == 0
    
    def size(self):
        """Return the number of items in the set"""
        return self._size
    
    def clear(self):
        """Remove all items from the set"""
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
    
    def to_list(self):
        """Return all items as a list"""
        result = []
        for bucket in self._buckets:
            result.extend(bucket)
        return result
