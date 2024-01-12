import React, { useState } from "react";
import "./style.css";
import CytoscapeComponent from "react-cytoscapejs";

function fetch_json(file_path){
   console.log('Loading json from: ', file_path)


   var jsonfile = require('jsonfile')
   console.log("jsonfile", jsonfile)
   jsonfile.readFile(file_path, function(err, obj) {
   console.dir(obj)
    });

   var fs = require('fs');

   //console.log("fs: ", fs);
   fs.readFile('file.txt', function (err, data) {
            if (err) {
                return console.error(err);
            }
            console.log("Asynchronous read: " + data.toString());
        });
   var str = readFileSync(file_path, 'utf8');

   fs.readFileSync(file_path, (err, data) => {
    if (err) console.log('Error: ', err);
    else return JSON.parse(data);
  });
}

export default function App() {
  var loc = window.location.pathname;
  var dir = loc.substring(0, loc.lastIndexOf('/'));
  console.log("dir:", dir)

  const [width, setWith] = useState("100%");
  const [height, setHeight] = useState("400px");
  const nodes_loaded = fetch_json("/Users/alexey.beley/git/horey/aws_access_manager/horey/aws_access_manager/ui/security-domain-tree/tests/nodes.json");
  console.log('Loaded nodes:', nodes_loaded)
  const [graphData, setGraphData] = useState({
    nodes: nodes_loaded,
    edges: [
      {
        data: { source: "1", target: "2", label: "Node2" }
      },
      {
        data: { source: "3", target: "4", label: "Node4" }
      },
      {
        data: { source: "3", target: "5", label: "Node5" }
      },
      {
        data: { source: "6", target: "5", label: " 6 -> 5" }
      },
      {
        data: { source: "6", target: "7", label: " 6 -> 7" }
      },
      {
        data: { source: "6", target: "8", label: " 6 -> 8" }
      },
      {
        data: { source: "6", target: "9", label: " 6 -> 9" }
      },
      {
        data: { source: "3", target: "13", label: " 3 -> 13" }
      }
    ]
  });

  const layout = {
    name: "breadthfirst",
    fit: true,
    // circle: true,
    directed: true,
    padding: 50,
    // spacingFactor: 1.5,
    animate: true,
    animationDuration: 1000,
    avoidOverlap: true,
    nodeDimensionsIncludeLabels: false
  };

  const styleSheet = [
    {
      selector: "node",
      style: {
        backgroundColor: "#4a56a6",
        width: 30,
        height: 30,
        label: "data(label)",

        // "width": "mapData(score, 0, 0.006769776522008331, 20, 60)",
        // "height": "mapData(score, 0, 0.006769776522008331, 20, 60)",
        // "text-valign": "center",
        // "text-halign": "center",
        "overlay-padding": "6px",
        "z-index": "10",
        //text props
        "text-outline-color": "#4a56a6",
        "text-outline-width": "2px",
        color: "white",
        fontSize: 20
      }
    },
    {
      selector: "node:selected",
      style: {
        "border-width": "6px",
        "border-color": "#AAD8FF",
        "border-opacity": "0.5",
        "background-color": "#77828C",
        width: 50,
        height: 50,
        //text props
        "text-outline-color": "#77828C",
        "text-outline-width": 8
      }
    },
    {
      selector: "node[type='device']",
      style: {
        shape: "rectangle"
      }
    },
    {
      selector: "edge",
      style: {
        width: 3,
        // "line-color": "#6774cb",
        "line-color": "#AAD8FF",
        "target-arrow-color": "#6774cb",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier"
      }
    }
  ];

  let myCyRef;

  return (
    <>
      <div>
        <h1>Cytoscape example</h1>
        <div
          style={{
            border: "1px solid",
            backgroundColor: "#f5f6fe"
          }}
        >
          <CytoscapeComponent
            elements={CytoscapeComponent.normalizeElements(graphData)}
            // pan={{ x: 200, y: 200 }}
            style={{ width: width, height: height }}
            zoomingEnabled={true}
            maxZoom={3}
            minZoom={0.1}
            autounselectify={false}
            boxSelectionEnabled={true}
            layout={layout}
            stylesheet={styleSheet}
            cy={cy => {
              myCyRef = cy;

              console.log("EVT", cy);

              cy.on("tap", "node", evt => {
                var node = evt.target;
                console.log("EVT", evt);
                console.log("TARGET", node.data());
                console.log("TARGET TYPE", typeof node[0]);
              });
            }}
            abc={console.log("myCyRef", myCyRef)}
          />
        </div>
      </div>
    </>
  );
}
