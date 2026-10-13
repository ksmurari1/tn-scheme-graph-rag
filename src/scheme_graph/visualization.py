from __future__ import annotations
import json
from html import escape

def graph_html(nodes: list[dict], edges: list[dict]) -> str:
    """Self-contained interactive graph using vis-network from a CDN."""
    safe_nodes = json.dumps(nodes, ensure_ascii=False).replace("</", "<\\/")
    safe_edges = json.dumps(edges, ensure_ascii=False).replace("</", "<\\/")
    return f"""
    <!doctype html><html><head><meta charset="utf-8">
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
    html,body,#graph{{height:100%;width:100%;margin:0;font-family:Inter,Arial,sans-serif;background:#F7FBFF}}
    #graph{{border:1px solid #D7E8F8;border-radius:14px;}}
    </style></head><body><div id="graph"></div><script>
    const rawNodes={safe_nodes}, rawEdges={safe_edges};
    const palette={{Scheme:'#2478D4',Department:'#123A70',Source:'#73BDF2',Beneficiary:'#5CAFA3',Benefit:'#E8B85A',Eligibility:'#8B83D7'}};
    const nodes=new vis.DataSet(rawNodes.map(n=>({{...n,color:{{background:palette[n.group]||'#DCEEFF',border:'#FFFFFF',highlight:{{background:'#8CCBFA',border:'#145AA8'}}}},font:{{color:'#17324D',size:14,face:'Arial'}},shape:'dot',size:22}})));
    const edges=new vis.DataSet(rawEdges.map(e=>({{...e,arrows:'to',color:{{color:'#9BBBD9',highlight:'#2478D4'}},font:{{size:10,align:'middle',color:'#58718B',strokeWidth:3,strokeColor:'#FFFFFF'}},smooth:{{type:'dynamic'}}}})));
    const container=document.getElementById('graph');
    new vis.Network(container,{{nodes,edges}},{{interaction:{{hover:true,navigationButtons:true,keyboard:true}},physics:{{stabilization:{{iterations:150}},barnesHut:{{gravitationalConstant:-3500,springLength:150}}}},nodes:{{borderWidth:2}},edges:{{width:1.5}}}});
    </script></body></html>"""
