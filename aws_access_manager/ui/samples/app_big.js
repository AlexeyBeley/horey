import "./styles.css";
import * as React from "react";
import CytoscapeComponent from "react-cytoscapejs";
import { ErrorBoundary, FallbackProps } from "react-error-boundary";
import { JSONEditor } from "./JSONEditor";
import { layouts } from "./layouts";
import { generateGraph } from "./generateGraph";
import setupCy from "./setupCy";
import cytoscape, { Stylesheet } from "cytoscape";
setupCy();

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function getDefaultStylesheet() {
  return [{ selector: "node", style: { label: "data(label)" } }];
}

export default function App() {
  const cyRef = React.useRef<cytoscape.Core | undefined>();
  const [elements, setElements] = React.useState(() => generateGraph(8));
  const [layout, setLayout] = React.useState(layouts.klay);
  const [stylesheet, setStylesheet] = React.useState<Stylesheet[]>(
    getDefaultStylesheet
  );
  return (
    <div className="App">
      <table>
        <tbody>
          <tr>
            <td className="c">
              <button onClick={() => setElements(generateGraph())}>
                new graph
              </button>
              <button onClick={() => setElements(generateGraph(35))}>
                new big graph
              </button>
              <button onClick={() => setElements(generateGraph(35, 7))}>
                new big disconnected graph
              </button>
              <button onClick={() => setElements(generateGraph(35, 20, true))}>
                new big acyclic graph
              </button>
              <br />
              layout preset:
              <br />
              <select
                size={Object.keys(layouts).length}
                onChange={(e) => {
                  setLayout({ ...layouts[e.target.value] });
                }}
              >
                {Object.keys(layouts).map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
              <br />
              layout config:
              <br />
              <JSONEditor value={layout} onChange={setLayout} />
              <br />
              stylesheet:
              <br />
              <JSONEditor value={stylesheet} onChange={setStylesheet} />
            </td>
            <td>
              <ErrorBoundary FallbackComponent={ErrorFallback}>
                <CytoscapeComponent
                  elements={elements}
                  style={{
                    width: "800px",
                    height: "500px",
                    border: "1px solid black"
                  }}
                  layout={layout}
                  stylesheet={stylesheet}
                  cy={(cy) => (cyRef.current = cy)}
                />
              </ErrorBoundary>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
