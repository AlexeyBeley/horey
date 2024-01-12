import React, { useState } from "react";
import "./style.css";
import CytoscapeComponent from "react-cytoscapejs";
import { layouts } from "./layouts";
import { generateGraph, generateGraphFromDict } from "./generateGraph";
import setupCy from "./setupCy";
setupCy();


const base_layout = {
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

const not_base_layout = {
    name: "breadthfirst",
    fit: true,
    // circle: true,
    directed: true,
    padding: 40,
    // spacingFactor: 1.5,
    animate: true,
    animationDuration: 1000,
    avoidOverlap: true,
    nodeDimensionsIncludeLabels: false
  };

export default function App() {
  const [width, setWith] = useState("100%");
  const [height, setHeight] = useState("400px");
  const [elements, setElements] = React.useState(() => generateGraph(26, 50));
  const [layout, setLayout] = React.useState(layouts.fcose);

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
  function btnClick(){
     var textArea = document.getElementById("myTextArea");
     setElements(generateGraphFromDict(textArea.value));
     setLayout(not_base_layout);
     setLayout(base_layout);
    }
  let myCyRef;

  return (
    <>
      <div>
        <h1>Security Domain Tree</h1>
        <div
          style={{
            border: "1px solid",
            backgroundColor: "#f5f6fe"
          }}
        >
          <CytoscapeComponent
            elements={elements}
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
            id="mainGraph"
          />
        </div>
        <div>
        <label htmlFor="input-file">Specify a file:</label><br/>
        <input type="file" id="input-file" onChange={bt_press_read_file}/>
        <textarea id="myTextArea" rows="4" columns="20"></textarea>
        <button id="myButton" onClick={btnClick}>Reload Graph</button>
        </div>
      </div>
    </>
  );
}

function bt_press_read_file(file_path){

var file = document.getElementById("input-file").files[0];
var reader = new FileReader();
reader.onload = function (e) {
    var textArea = document.getElementById("myTextArea");
    textArea.value = e.target.result;
};
reader.readAsText(file);
}


