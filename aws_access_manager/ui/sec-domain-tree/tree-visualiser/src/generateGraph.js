import { ElementDefinition } from "cytoscape";

function randint(min: number, max: number): number {
  return min + Math.floor(Math.random() * (max - min));
}

export function generateGraphFromDict(str_src) {
  var dict_src = JSON.parse(str_src);

  console.log("dict_src: ", dict_src)
  console.log("nodes: ", dict_src.nodes)

  const elements: ElementDefinition[] = [];

  dict_src.nodes.forEach((node) => {
    let id = node.id
    let label = node.label
    elements.push({ data: { id, label: label } });
  });

  dict_src.edges.forEach((edge) => {
    let id1= edge.source;
    let id2= edge.target;
    let label= edge.label;
    elements.push({ data: { source: id1, target: id2, label: label} });
  });

  return elements;
}

export function generateGraph(n = 8, m = n * 2, acyclic = false) {
  const ids = [];
  for (let i = 0; i < n; i++) {
    ids.push(String.fromCharCode("a".charCodeAt(0) + i));
  }

  const elements: ElementDefinition[] = [];

  ids.forEach((id) => {
    elements.push({ data: { id, label: id } });
  });

  for (let i = 0; i < m; i++) {
    const idIndex1 = randint(0, ids.length);
    const id1 = ids[idIndex1];
    const id2 = ids[randint(acyclic ? idIndex1 + 1 : 0, ids.length)];
    elements.push({ data: { source: id1, target: id2 } });
  }
  return elements;
}
