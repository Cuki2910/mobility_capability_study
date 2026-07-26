import json, sqlite3
from pathlib import Path
import pytest
from src.provenance import graph_edges, load_pipeline, validate_artifact_contract
from scripts.graph_health import evaluate
from scripts.query_lineage import query

def test_v2_pipeline_and_edges():
 pipeline=load_pipeline(Path('config/pipeline.json')); edges=graph_edges(pipeline['nodes'])
 assert pipeline['schema_version']==2 and any(e['type']=='PRODUCED' for e in edges)
def test_pipeline_rejects_duplicate_output(tmp_path):
 p=tmp_path/'p.json'; p.write_text(json.dumps({'schema_version':2,'nodes':{'a':{'objective':'a','command':['x'],'outputs':['x']},'b':{'objective':'b','command':['x'],'outputs':['x']}}}))
 with pytest.raises(ValueError,match='Duplicate'): load_pipeline(p)
def test_artifact_contract_detects_empty(tmp_path):
 (tmp_path/'x.csv').write_text(''); node={'outputs':['x.csv'],'artifact_contract':{'x.csv':{'non_empty':True,'suffix':'.csv'}}}
 assert validate_artifact_contract(node,tmp_path)
def test_health_has_graph_counts():
 result=evaluate(load_pipeline(Path('config/pipeline.json'))); assert result['healthy'] and result['node_count']>=7
def test_lineage_query(tmp_path):
 db=tmp_path/'x.sqlite'
 with sqlite3.connect(db) as c:
  c.execute('CREATE TABLE runs (run_id TEXT, status TEXT, started_at TEXT, finished_at TEXT, git_commit TEXT, git_dirty INTEGER)'); c.execute("INSERT INTO runs VALUES ('r','ok','a','b','c',0)")
 assert query(db,'runs')[0]['run_id']=='r'
