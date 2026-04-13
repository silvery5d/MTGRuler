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

export function GraphView({
  elements,
  onNodeClick,
  highlightedNodes,
  highlightedEdges,
}: GraphViewProps) {
  const onNodeClickRef = useRef(onNodeClick);
  onNodeClickRef.current = onNodeClick;

  // react-cytoscapejs calls `props.cy(this._cy)` on EVERY componentDidUpdate.
  // We use this to our advantage: run different updates at different
  // frequencies by guarding with flags on the cy instance itself.
  const handleCy = useCallback(
    (cy: cytoscape.Core) => {
      const cyAny = cy as any;

      // --- Listeners: attach exactly once per cy instance ---
      if (!cyAny._listenersAttached) {
        cyAny._listenersAttached = true;

        cy.on("tap", "node", (evt) => {
          onNodeClickRef.current(evt.target.id());
        });

        cy.on("dbltap", "node", (evt) => {
          cy.animate({
            center: { eles: evt.target },
            zoom: cy.zoom() * 1.5,
          });
        });
      }

      // --- Layout: re-run only when node count changes ---
      const nodeCount = cy.nodes().length;
      if (nodeCount > 0 && cyAny._lastNodeCount !== nodeCount) {
        cyAny._lastNodeCount = nodeCount;

        try {
          // Scale layout parameters aggressively by node count to prevent overlap.
          const edgeCount = cy.edges().length;
          const density = nodeCount > 0 ? edgeCount / nodeCount : 1;

          // Repulsion scales quadratically with node count for large graphs
          const baseRepulsion = nodeCount > 500
            ? 80000 + nodeCount * 100
            : nodeCount > 200
              ? 40000 + nodeCount * 50
              : Math.max(10000, 4500 * (1 + density));

          // Edge length grows with node count so clusters spread out
          const edgeLen = nodeCount > 500
            ? 300 + nodeCount * 0.2
            : nodeCount > 200
              ? 200 + nodeCount * 0.3
              : Math.max(150, 80 + nodeCount * 0.5);

          // Node separation — minimum gap between non-connected nodes
          const separation = nodeCount > 500 ? 300 : nodeCount > 200 ? 200 : 150;

          cy.layout({
            name: "fcose",
            animate: nodeCount < 200,
            animationDuration: 400,
            nodeRepulsion: () => baseRepulsion,
            idealEdgeLength: () => edgeLen,
            nodeSeparation: separation,
            padding: 80,
            quality: nodeCount > 500 ? "draft" : "default",
            randomize: true,
            nodeDimensionsIncludeLabels: true,
          } as cytoscape.LayoutOptions).run();
        } catch {
          cy.layout({ name: "grid", padding: 30 }).run();
        }
      }

      // --- Highlights: update every time (cheap, batched) ---
      cy.batch(() => {
        cy.elements().removeClass("dimmed highlighted");
        if (highlightedNodes || highlightedEdges) {
          cy.elements().addClass("dimmed");
          highlightedNodes?.forEach((id) => {
            cy.getElementById(id).removeClass("dimmed").addClass("highlighted");
          });
          highlightedEdges?.forEach((id) => {
            cy.getElementById(id).removeClass("dimmed").addClass("highlighted");
          });
        }
      });
    },
    [highlightedNodes, highlightedEdges],
  );

  return (
    <div className="flex-1 relative min-w-0 overflow-hidden">
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
