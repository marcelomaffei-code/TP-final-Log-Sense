from storage.node import BPlusNode
class BPlusTree:
    def __init__(self,order=4): self.order=order; self.root=BPlusNode(True)
    def _find_leaf(self,key):
      c=self.root
      while not c.is_leaf:
       i=0
       while i<len(c.keys) and key>=c.keys[i]: i+=1
       c=c.children[i]
      return c
    def insert(self,key,value):
      leaf=self._find_leaf(key); i=0
      while i<len(leaf.keys) and key>leaf.keys[i]: i+=1
      leaf.keys.insert(i,key); leaf.children.insert(i,value)
      if len(leaf.keys)>=self.order: self._split_leaf(leaf)
    def _split_leaf(self,leaf):
      new=BPlusNode(True); mid=len(leaf.keys)//2
      new.keys=leaf.keys[mid:]; new.children=leaf.children[mid:]
      leaf.keys=leaf.keys[:mid]; leaf.children=leaf.children[:mid]
      new.next_leaf=leaf.next_leaf; leaf.next_leaf=new
      pk=new.keys[0]
      if leaf==self.root:
       r=BPlusNode(); r.keys=[pk]; r.children=[leaf,new]; leaf.parent=r; new.parent=r; self.root=r
      else: self._insert_parent(leaf.parent,pk,new)
    def _insert_parent(self,parent,key,child):
      i=0
      while i<len(parent.keys) and key>parent.keys[i]: i+=1
      parent.keys.insert(i,key); parent.children.insert(i+1,child); child.parent=parent
    def search(self,key):
      leaf=self._find_leaf(key)
      for i,k in enumerate(leaf.keys):
       if k==key: return leaf.children[i]
      return None
    def range_search(self,start,end):
      res=[]; leaf=self._find_leaf(start)
      while leaf:
       for i,k in enumerate(leaf.keys):
        if start<=k<=end: res.append(leaf.children[i])
        elif k>end: return res
       leaf=leaf.next_leaf
      return res
