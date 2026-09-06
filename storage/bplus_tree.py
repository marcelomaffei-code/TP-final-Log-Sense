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
    
    def insert(self, key, value):
        """Insert a key-value pair into the tree"""
        leaf = self._find_leaf(key)
        
        # Find insertion position
        i = 0
        while i < len(leaf.keys) and key > leaf.keys[i]:
            i += 1
        
        # Insert key and value
        leaf.keys.insert(i, key)
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
        leaf = self._find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.children[i]
        return None
    
    def range_search(self, start, end):
        """Search for all keys in a range [start, end]"""
        res = []
        leaf = self._find_leaf(start)
        
        while leaf:
            for i, k in enumerate(leaf.keys):
                if start <= k <= end:
                    res.append(leaf.children[i])
                elif k > end:
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
                res.append((leaf.keys[i], leaf.children[i]))
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
