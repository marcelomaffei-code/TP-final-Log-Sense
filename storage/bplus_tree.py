from storage.node import BPlusNode

class BPlusTree:
    def __init__(self, order=4):
        self.order = order
        self.root = BPlusNode(True)
    
    def _find_leaf(self, key):
        """Find the leaf node where the key should be inserted"""
        c = self.root
        while not c.is_leaf:
            i = 0
            while i < len(c.keys) and key >= c.keys[i]:
                i += 1
            c = c.children[i]
        return c

    def _make_storage_key(self, timestamp, value):
        """Build a stable composite key: timestamp plus record identity."""
        if isinstance(timestamp, tuple):
            return timestamp

        origin = getattr(value, "origin", "")
        message = getattr(value, "message", "")
        if not message:
            message = repr(sorted(getattr(value, "__dict__", {}).items()))
        return timestamp, f"{origin}|{message}"

    @staticmethod
    def _lower_bound(timestamp):
        return timestamp, ""

    @staticmethod
    def _upper_bound(timestamp):
        return timestamp, chr(0x10FFFF)

    @staticmethod
    def _display_key(key):
        return key[0] if isinstance(key, tuple) else key
    
    def insert(self, key, value):
        """Insert a key-value pair into the tree"""
        storage_key = self._make_storage_key(key, value)
        leaf = self._find_leaf(storage_key)
        
        # Find insertion position
        i = 0
        while i < len(leaf.keys) and storage_key > leaf.keys[i]:
            i += 1
        
        # Insert key and value
        leaf.keys.insert(i, storage_key)
        leaf.children.insert(i, value)
        
        # Split if overflow
        if len(leaf.keys) >= self.order:
            self._split_leaf(leaf)
    
    def _split_leaf(self, leaf):
        """Split a leaf node when it overflows"""
        new = BPlusNode(True)
        mid = len(leaf.keys) // 2
        
        # Move half the keys and values to new node
        new.keys = leaf.keys[mid:]
        new.children = leaf.children[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.children = leaf.children[:mid]
        
        # Update leaf links
        new.next_leaf = leaf.next_leaf
        leaf.next_leaf = new
        
        # Get the first key from new node (this goes up to parent)
        pk = new.keys[0]
        
        # If leaf is root, create new root
        if leaf == self.root:
            r = BPlusNode()
            r.keys = [pk]
            r.children = [leaf, new]
            leaf.parent = r
            new.parent = r
            self.root = r
        else:
            self._insert_parent(leaf.parent, pk, new)
    
    def _insert_parent(self, parent, key, child):
        """Insert a key into a parent node and handle splitting"""
        i = 0
        while i < len(parent.keys) and key > parent.keys[i]:
            i += 1
        
        parent.keys.insert(i, key)
        parent.children.insert(i + 1, child)
        child.parent = parent
        
        # Split if overflow
        if len(parent.keys) >= self.order:
            self._split_internal(parent)
    
    def _split_internal(self, node):
        """Split an internal node when it overflows"""
        new = BPlusNode(False)
        mid = len(node.keys) // 2
        
        # The middle key goes up to parent
        pk = node.keys[mid]
        
        # Move keys after mid to new node
        new.keys = node.keys[mid + 1:]
        new.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        
        # Update parent references
        for child in new.children:
            child.parent = new
        
        # If node is root, create new root
        if node == self.root:
            r = BPlusNode()
            r.keys = [pk]
            r.children = [node, new]
            node.parent = r
            new.parent = r
            self.root = r
        else:
            self._insert_parent(node.parent, pk, new)
    
    def search(self, key):
        """Search for a specific key"""
        leaf = self._find_leaf(self._lower_bound(key))
        for i, k in enumerate(leaf.keys):
            if self._display_key(k) == key:
                return leaf.children[i]
            if self._display_key(k) > key:
                break
        return None

    def search_all(self, key):
        """Return every record stored for an exact timestamp."""
        records = []
        leaf = self._find_leaf(self._lower_bound(key))
        while leaf:
            for index, storage_key in enumerate(leaf.keys):
                timestamp = self._display_key(storage_key)
                if timestamp == key:
                    records.append(leaf.children[index])
                elif timestamp > key:
                    return records
            leaf = leaf.next_leaf
        return records
    
    def range_search(self, start, end):
        """Search for all keys in a range [start, end]"""
        res = []
        lower = self._lower_bound(start)
        upper = self._upper_bound(end)
        leaf = self._find_leaf(lower)
        
        while leaf:
            for i, k in enumerate(leaf.keys):
                if lower <= k <= upper:
                    res.append(leaf.children[i])
                elif k > upper:
                    return res
            leaf = leaf.next_leaf
        
        return res
    
    def get_all_records(self):
        """Get all records in the tree (in-order traversal)"""
        res = []
        
        # Find the leftmost leaf
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        
        leaf = node
        
        while leaf:
            for i in range(len(leaf.keys)):
                res.append((self._display_key(leaf.keys[i]), leaf.children[i]))
            leaf = leaf.next_leaf
        
        return res
    
    def count_records(self):
        """Count total number of records in the tree"""
        count = 0
        
        # Find the leftmost leaf
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        
        leaf = node
        
        while leaf:
            count += len(leaf.keys)
            leaf = leaf.next_leaf
        
        return count
