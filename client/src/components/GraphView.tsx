import { useRef, useCallback, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import { defaultStylesheet } from "../styles/cytoscape.js";

interface GraphViewProps {
  elements: cytoscape.ElementDefinition[];
  onNodeClick: (nodeId: string) => void;
  highlightedNodes?: Set<string>;
  highlightedEdges?: Set<string>;
}

interface EdgeIndicator {
  id: string;
  label: string;
  color: string;
  x: number;
  y: number;
}

export function GraphView({
  elements,
  onNodeClick,
  highlightedNodes,
  highlightedEdges,
}: GraphViewProps) {
  const onNodeClickRef = useRef(onNodeClick);
  onNodeClickRef.current = onNodeClick;
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [edgeIndicators, setEdgeIndicators] = useState<EdgeIndicator[]>([]);

  const handleCy = useCallback(
    (cy: cytoscape.Core) => {
      const cyAny = cy as any;
      cyRef.current = cy;

      // --- Listeners: attach exactly once per cy instance ---
      if (!cyAny._listenersAttached) {
        cyAny._listenersAttached = true;

        cy.on("tap", "node", (evt) => {
          const node = evt.target;
          onNodeClickRef.current(node.id());

          // Highlight neighbors
          cy.batch(() => {
            cy.elements().addClass("dimmed").removeClass("neighbor-highlight");
            node.removeClass("dimmed").addClass("highlighted");
            const connectedEdges = node.connectedEdges();
            connectedEdges.removeClass("dimmed").addClass("neighbor-highlight");
            const neighbors = node.neighborhood("node");
            neighbors.removeClass("dimmed").addClass("neighbor-highlight");
          });

          // Compute edge indicators for off-screen neighbors
          updateEdgeIndicators(cy, node);
        });

        // Click background to clear
        cy.on("tap", (evt) => {
          if (evt.target === cy) {
            cy.batch(() => {
              cy.elements().removeClass("dimmed highlighted neighbor-highlight");
            });
            setEdgeIndicators([]);
          }
        });

        cy.on("dbltap", "node", (evt) => {
          cy.animate({
            center: { eles: evt.target },
            zoom: cy.zoom() * 1.5,
          });
        });

        // Update indicators on pan/zoom
        cy.on("viewport", () => {
          if (cyAny._selectedNode) {
            updateEdgeIndicators(cy, cyAny._selectedNode);
          }
        });

        // Cap the visual size of nodes and text when zoomed in.
        const CAP_ZOOM = 1.0;
        const applyZoomCap = () => {
          const z = cy.zoom();
          if (z > CAP_ZOOM) {
            const scale = CAP_ZOOM / z;
            cy.nodes().forEach((n) => {
              const base = n.data("size") || 14;
              n.style({ width: base * scale, height: base * scale, "border-width": 2 * scale });
            });
            cy.style().selector("node").style({ "font-size": 10 * scale, "text-outline-width": 2 * scale }).update();
            cy.style().selector("edge").style({ width: 2 * scale, "arrow-scale": scale }).update();
          } else {
            cy.nodes().forEach((n) => {
              const base = n.data("size") || 14;
              n.style({ width: base, height: base, "border-width": 2 });
            });
            cy.style().selector("node").style({ "font-size": 10, "text-outline-width": 2 }).update();
            cy.style().selector("edge").style({ width: 2, "arrow-scale": 1 }).update();
          }
        };
        cy.on("zoom", applyZoomCap);
      }

      // Store selected node ref for viewport updates
      cy.on("tap", "node", (evt) => {
        cyAny._selectedNode = evt.target;
      });
      cy.on("tap", (evt) => {
        if (evt.target === cy) cyAny._selectedNode = null;
      });

      // --- Layout: re-run only when node count changes ---
      const nodeCount = cy.nodes().length;
      if (nodeCount > 0 && cyAny._lastNodeCount !== nodeCount) {
        cyAny._lastNodeCount = nodeCount;

        try {
          const edgeCount = cy.edges().length;
          const density = nodeCount > 0 ? edgeCount / nodeCount : 1;

          const baseRepulsion = nodeCount > 500
            ? 200000 + nodeCount * 200
            : nodeCount > 200
              ? 60000 + nodeCount * 80
              : Math.max(10000, 4500 * (1 + density));

          const edgeLen = nodeCount > 500
            ? 500 + nodeCount * 0.3
            : nodeCount > 200
              ? 300 + nodeCount * 0.5
              : Math.max(150, 80 + nodeCount * 0.5);

          const separation = nodeCount > 500 ? 500 : nodeCount > 200 ? 300 : 150;

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
        // Only apply path highlights if present; neighbor highlights are handled by tap
        if (highlightedNodes || highlightedEdges) {
          cy.elements().addClass("dimmed").removeClass("highlighted");
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

  function updateEdgeIndicators(cy: cytoscape.Core, node: cytoscape.NodeSingular) {
    const container = cy.container();
    if (!container) { setEdgeIndicators([]); return; }

    const rect = container.getBoundingClientRect();
    const W = rect.width;
    const H = rect.height;
    const MARGIN = 12;

    const neighbors = node.neighborhood("node");
    const indicators: EdgeIndicator[] = [];

    neighbors.forEach((neighbor) => {
      const pos = neighbor.renderedPosition();
      // Check if off-screen
      if (pos.x < 0 || pos.x > W || pos.y < 0 || pos.y > H) {
        // Clamp to edge
        const cx = Math.max(MARGIN, Math.min(W - MARGIN, pos.x));
        const cy = Math.max(MARGIN, Math.min(H - MARGIN, pos.y));
        indicators.push({
          id: neighbor.id(),
          label: neighbor.data("label") || neighbor.id(),
          color: neighbor.data("color") || "#6b7280",
          x: cx,
          y: cy,
        });
      }
    });

    setEdgeIndicators(indicators);
  }

  return (
    <div className="flex-1 relative min-w-0 overflow-hidden">
      {elements.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          Loading graph...
        </div>
      ) : (
        <>
          <CytoscapeComponent
            elements={elements}
            stylesheet={defaultStylesheet}
            cy={handleCy}
            className="w-full h-full"
            style={{ width: "100%", height: "100%" }}
          />
          {/* Edge indicators for off-screen neighbors */}
          {edgeIndicators.map((ind) => (
            <button
              key={ind.id}
              onClick={() => {
                const cy = cyRef.current;
                if (!cy) return;
                const n = cy.getElementById(ind.id);
                if (n.nonempty()) {
                  cy.animate({ center: { eles: n }, duration: 300 });
                }
              }}
              className="absolute pointer-events-auto z-20 flex items-center gap-1 px-2 py-1 rounded-full text-xs text-white shadow-lg border border-white/30 backdrop-blur-sm cursor-pointer hover:scale-110 transition-transform"
              style={{
                left: ind.x,
                top: ind.y,
                transform: "translate(-50%, -50%)",
                backgroundColor: ind.color + "cc",
              }}
            >
              <span className="w-2 h-2 rounded-full bg-white/80" />
              <span className="max-w-[80px] truncate">{ind.label}</span>
            </button>
          ))}
        </>
      )}
    </div>
  );
}
