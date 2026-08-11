"""Query the disposable research lineage index."""
import argparse, json, sqlite3
from pathlib import Path
DB=Path('outputs/lineage/research_lineage.sqlite')
def query(db: Path, kind: str, value: str=''):
 with sqlite3.connect(db) as c:
  c.row_factory=sqlite3.Row
  if kind=='runs': rows=c.execute('SELECT * FROM runs ORDER BY started_at DESC').fetchall()
  elif kind=='artifact': rows=c.execute('SELECT * FROM artifacts WHERE path=? ORDER BY run_id DESC',(value,)).fetchall()
  elif kind=='node': rows=c.execute('SELECT * FROM nodes WHERE node_id=? ORDER BY run_id DESC',(value,)).fetchall()
  elif kind=='decision': rows=c.execute('SELECT * FROM decisions WHERE decision_id=? ORDER BY run_id DESC',(value,)).fetchall()
  else: raise ValueError(kind)
  return [dict(row) for row in rows]
def main():
 p=argparse.ArgumentParser(); p.add_argument('kind',choices=['runs','artifact','node','decision']); p.add_argument('value',nargs='?',default=''); p.add_argument('--db',type=Path,default=DB); p.add_argument('--json',action='store_true'); a=p.parse_args(); rows=query(a.db,a.kind,a.value)
 if a.json: print(json.dumps(rows,indent=2,ensure_ascii=False))
 else:
  for row in rows: print(' | '.join(f'{k}={v}' for k,v in row.items()))
 return 0
if __name__=='__main__': raise SystemExit(main())
