import { useRef, useCallback } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import { defaultStylesheet } from "../styles/cytoscape.js";

interface GraphViewProps {
  elements: cytoscape.ElementDefinition[];
  onNodeClick: (nodeId: string) => void;
  highlightedNodes?: Set<string>;
  highlightedEdges?: Set<string>;
}

export function GraphView({ elements, onNodeClick, highlightedNodes, highlightedEdges }: GraphViewProps) {
  const cyRef = useRef<cytoscape.Core | null>(null);

  const handleCy = useCallback(
    (cy: cytoscape.Core) => {
      cyRef.current = cy;

      cy.removeAllListeners();

      cy.on("tap", "node", (evt) => {
        const nodeId = evt.target.id();
        onNodeClick(nodeId);
      });

      cy.on("dbltap", "node", (evt) => {
        const node = evt.target;
        cy.animate({
          center: { eles: node },
          zoom: cy.zoom() * 1.5,
        });
      });

      if (highlightedNodes || highlightedEdges) {
        cy.elements().addClass("dimmed");
        if (highlightedNodes) {
          highlightedNodes.forEach((id) => {
            cy.getElementById(id).removeClass("dimmed").addClass("highlighted");
          });
        }
        if (highlightedEdges) {
          highlightedEdges.forEach((id) => {
            cy.getElementById(id).removeClass("dimmed").addClass("highlighted");
          });
        }
      } else {
        cy.elements().removeClass("dimmed highlighted");
      }

      cy.layout({
        name: "cose",
        animate: true,
        animationDuration: 500,
        nodeRepulsion: () => 8000,
        idealEdgeLength: () => 100,
        padding: 50,
      } as cytoscape.LayoutOptions).run();
    },
    [onNodeClick, highlightedNodes, highlightedEdges],
  );

  return (
    <div className="flex-1 relative">
      {elements.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          Loading graph...
        </div>
      ) : (
        <CytoscapeComponent
          elements={elements}
          stylesheet={defaultStylesheet}
          cy={handleCy}
          className="w-full h-full"
          style={{ width: "100%", height: "100%" }}
        />
      )}
    </div>
  );
}
