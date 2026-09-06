class ReportService:
 def occurrences_by_service(self,records):
  d={}
  for r in records:
   s=getattr(r,'service',None)
   if not s: continue
   d.setdefault(s,{'events':0,'errors':0})
   d[s]['events']+=1
   if r.calculate_level()=='ERROR': d[s]['errors']+=1
  return d
