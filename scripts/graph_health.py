"""Evaluate static and indexed health of the research graph."""
import argparse, json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from src.provenance import graph_edges, load_pipeline, write_json_atomic
def evaluate(pipeline):
 nodes=pipeline['nodes']; produced={p for n in nodes.values() for p in n.get('outputs',[])}; inputs={p for n in nodes.values() for p in n.get('inputs',[])}
 warnings=[]
 for name,node in nodes.items():
  if not node.get('decisions'): warnings.append(f'{name}: no decisions')
  if not node.get('evaluations'): warnings.append(f'{name}: no evaluator')
 return {'schema_version':1,'healthy':True,'node_count':len(nodes),'edge_count':len(graph_edges(nodes)),'artifact_count':len(produced),'external_input_count':len(inputs-produced),'hard_failures':[],'warnings':warnings}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--pipeline',type=Path,default=Path('config/pipeline.json')); p.add_argument('--json-output',type=Path,default=Path('outputs/lineage/graph_health.json')); p.add_argument('--md-output',type=Path,default=Path('outputs/lineage/graph_health.md')); a=p.parse_args(); result=evaluate(load_pipeline(ROOT/a.pipeline)); write_json_atomic(ROOT/a.json_output,result); warnings='\n'.join(f'- {x}' for x in result['warnings']) or '- none'; md='# Graph Health\n\n'+f"- Healthy: **{result['healthy']}**\n- Nodes: {result['node_count']}\n- Edges: {result['edge_count']}\n- Artifacts: {result['artifact_count']}\n- External inputs: {result['external_input_count']}\n\n## Warnings\n\n"+warnings+'\n'; (ROOT/a.md_output).write_text(md,encoding='utf-8'); print(json.dumps(result,indent=2)); return 1 if result['hard_failures'] else 0
if __name__=='__main__': raise SystemExit(main())
