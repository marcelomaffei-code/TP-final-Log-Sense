import re
from domain.api_log import ApiLog
class LogParser:
 API=re.compile(r'.*API.*')
 def parse(self,line):
  if 'API' in line: return line
  return None
