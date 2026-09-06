class CustomDict:
    """Dictionary implementation from scratch using hash table"""
    
    def __init__(self, initial_capacity=16):
        self._capacity = initial_capacity
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]
    
    def _hash(self, key):
        """Simple hash function"""
        return hash(key) % self._capacity
    
    def _rehash(self):
        """Resize the hash table when load factor is high"""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        
        for bucket in old_buckets:
            for key, value in bucket:
                self[key] = value
    
    def __setitem__(self, key, value):
        """Set a key-value pair"""
        bucket_index = self._hash(key)
        bucket = self._buckets[bucket_index]
        
        # Check if key already exists
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        # Add new key-value pair
        bucket.append((key, value))
        self._size += 1
        
        # Rehash if load factor > 0.75
        if self._size / self._capacity > 0.75:
            self._rehash()
    
    def __getitem__(self, key):
        """Get the value for a key"""
        bucket_index = self._hash(key)
        bucket = self._buckets[bucket_index]
        
        for k, v in bucket:
            if k == key:
                return v
        
        raise KeyError(key)
    
    def get(self, key, default=None):
        """Get the value for a key, return default if not found"""
        try:
            return self[key]
        except KeyError:
            return default
    
    def contains(self, key):
        """Check if a key exists in the dictionary"""
        bucket_index = self._hash(key)
        bucket = self._buckets[bucket_index]
        
        for k, _ in bucket:
            if k == key:
                return True
        
        return False
    
    def remove(self, key):
        """Remove a key-value pair"""
        bucket_index = self._hash(key)
        bucket = self._buckets[bucket_index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return
        
        raise KeyError(key)
    
    def is_empty(self):
        """Check if the dictionary is empty"""
        return self._size == 0
    
    def size(self):
        """Return the number of key-value pairs"""
        return self._size
    
    def clear(self):
        """Remove all key-value pairs"""
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
    
    def keys(self):
        """Return all keys"""
        result = []
        for bucket in self._buckets:
            for key, _ in bucket:
                result.append(key)
        return result
    
    def values(self):
        """Return all values"""
        result = []
        for bucket in self._buckets:
            for _, value in bucket:
                result.append(value)
        return result
    
    def items(self):
        """Return all key-value pairs"""
        result = []
        for bucket in self._buckets:
            result.extend(bucket)
        return result
