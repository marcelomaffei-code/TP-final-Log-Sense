import pickle
from exceptions.custom_exceptions import StorageCorruptionError
class PersistenceManager:
 @staticmethod
 def save(tree,file):
  with open(file,"wb") as f: pickle.dump(tree,f)
 @staticmethod
 def load(file):
  try:
   with open(file,"rb") as f:return pickle.load(f)
  except Exception as e: raise StorageCorruptionError(str(e))
