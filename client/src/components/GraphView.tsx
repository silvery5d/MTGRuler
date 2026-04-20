import { useRef, useCallback, useState, useEffect } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type cytoscape from "cytoscape";
import { defaultStylesheet, COMPLEXITY_COLORS } from "../styles/cytoscape.js";
import type { ColorMode } from "../hooks/useGraph.js";

interface GraphViewProps {
  elements: cytoscape.ElementDefinition[];
  onNodeClick: (nodeId: string) => void;
  highlightedNodes?: Set<string>;
  highlightedEdges?: Set<string>;
  colorMode?: ColorMode;
  onColorModeChange?: (mode: ColorMode) => void;
  focusNodeId?: string | null;
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
  colorMode = "type",
  onColorModeChange,
  focusNodeId,
}: GraphViewProps) {
  const onNodeClickRef = useRef(onNodeClick);
  onNodeClickRef.current = onNodeClick;
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [edgeIndicators, setEdgeIndicators] = useState<EdgeIndicator[]>([]);

  // Extract the node-highlight logic so it can be called both on tap
  // and imperatively (via focusNodeId from search results).
  const highlightNeighborsRef = useRef<((nodeId: string) => void) | null>(null);

  useEffect(() => {
    if (focusNodeId && highlightNeighborsRef.current) {
      highlightNeighborsRef.current(focusNodeId);
    }
  }, [focusNodeId]);

  const handleCy = useCallback(
    (cy: cytoscape.Core) => {
      const cyAny = cy as any;
      cyRef.current = cy;

      // --- Listeners: attach exactly once per cy instance ---
      if (!cyAny._listenersAttached) {
        cyAny._listenersAttached = true;

        const highlightNode = (node: cytoscape.NodeSingular) => {
          cy.batch(() => {
            cy.elements().addClass("dimmed").removeClass("neighbor-highlight");
            node.removeClass("dimmed").addClass("highlighted");
            const connectedEdges = node.connectedEdges();
            connectedEdges.removeClass("dimmed").addClass("neighbor-highlight");
            const neighbors = node.neighborhood("node");
            neighbors.removeClass("dimmed").addClass("neighbor-highlight");

            cy.nodes().forEach((n) => {
              if (n.hasClass("dimmed")) {
                n.ungrabify();
                n.unselectify();
              } else {
                n.grabify();
                n.selectify();
              }
            });
          });
          updateEdgeIndicators(cy, node);
        };

        // Expose to parent via ref so focusNodeId effect can invoke it
        highlightNeighborsRef.current = (nodeId: string) => {
          const n = cy.getElementById(nodeId);
          if (!n.nonempty() || !n.isNode()) return;
          highlightNode(n as cytoscape.NodeSingular);
          cyAny._selectedNode = n;
          // Center view on the focused node
          cy.animate({ center: { eles: n }, duration: 300 });
        };

        cy.on("tap", "node", (evt) => {
          const node = evt.target;
          onNodeClickRef.current(node.id());
          highlightNode(node);
        });

        // Click anything that's not a node → clear selection
        cy.on("tap", (evt) => {
          if (evt.target === cy || evt.target.isEdge()) {
            cy.batch(() => {
              cy.elements().removeClass("dimmed highlighted neighbor-highlight");
              // Restore interactivity on all nodes
              cy.nodes().grabify().selectify();
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
        const CAP_ZOOM = 2.0;
        const applyZoomCap = () => {
          const z = cy.zoom();
          if (z > CAP_ZOOM) {
            const scale = CAP_ZOOM / z;
            cy.nodes().forEach((n) => {
              const base = n.data("size") || 14;
              n.style({ width: base * scale, height: base * scale, "border-width": 2 * scale, "text-margin-y": 4 * scale });
            });
            cy.style().selector("node").style({ "font-size": 10 * scale, "text-outline-width": 2 * scale }).update();
            cy.style().selector("edge").style({ width: 2 * scale, "arrow-scale": scale }).update();
          } else {
            cy.nodes().forEach((n) => {
              const base = n.data("size") || 14;
              n.style({ width: base, height: base, "border-width": 2, "text-margin-y": 4 });
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

          // Scale aggressively with node count so dense graphs spread out
          const baseRepulsion = Math.max(25000, 8000 * (1 + density) + nodeCount * 30);
          const edgeLen = Math.max(200, 120 + nodeCount * 0.6);
          const separation = Math.max(250, 150 + nodeCount * 0.2);

          const layout = cy.layout({
            name: "fcose",
            animate: false,
            nodeRepulsion: () => baseRepulsion,
            idealEdgeLength: () => edgeLen,
            nodeSeparation: separation,
            padding: 80,
            quality: nodeCount > 500 ? "draft" : "default",
            randomize: true,
            nodeDimensionsIncludeLabels: true,
          } as cytoscape.LayoutOptions);
          layout.run();

          // Post-layout: iterative collision resolution to separate
          // overlapping nodes. Uses each node's actual size for the
          // collision radius so bigger nodes need more spacing.
          const positions = new Map<string, { x: number; y: number; r: number }>();
          cy.nodes().forEach((n) => {
            const sz = n.data("size") || 14;
            positions.set(n.id(), { ...n.position(), r: sz / 2 + 6 });
          });

          // Bucket nodes into a spatial grid to avoid O(n^2) scans.
          const CELL = 80;
          const buildGrid = () => {
            const grid = new Map<string, string[]>();
            positions.forEach((p, id) => {
              const gx = Math.floor(p.x / CELL);
              const gy = Math.floor(p.y / CELL);
              const key = `${gx},${gy}`;
              if (!grid.has(key)) grid.set(key, []);
              grid.get(key)!.push(id);
            });
            return grid;
          };

          for (let pass = 0; pass < 8; pass++) {
            const grid = buildGrid();
            let movedAny = false;
            positions.forEach((pa, aid) => {
              const gx = Math.floor(pa.x / CELL);
              const gy = Math.floor(pa.y / CELL);
              for (let dx = -1; dx <= 1; dx++) {
                for (let dy = -1; dy <= 1; dy++) {
                  const ids = grid.get(`${gx + dx},${gy + dy}`);
                  if (!ids) continue;
                  for (const bid of ids) {
                    if (aid >= bid) continue;
                    const pb = positions.get(bid)!;
                    const vx = pb.x - pa.x;
                    const vy = pb.y - pa.y;
                    const d = Math.sqrt(vx * vx + vy * vy);
                    const minDist = pa.r + pb.r;
                    if (d < minDist) {
                      const overlap = minDist - d;
                      // Avoid divide-by-zero when nodes are exactly on top
                      let nx = vx, ny = vy;
                      if (d < 0.001) {
                        const ang = (aid.length * 97 + bid.length * 31) % 360 * Math.PI / 180;
                        nx = Math.cos(ang);
                        ny = Math.sin(ang);
                      } else {
                        nx /= d;
                        ny /= d;
                      }
                      const shift = overlap / 2 + 1;
                      pa.x -= nx * shift;
                      pa.y -= ny * shift;
                      pb.x += nx * shift;
                      pb.y += ny * shift;
                      movedAny = true;
                    }
                  }
                }
              }
            });
            if (!movedAny) break;
          }

          cy.batch(() => {
            positions.forEach((pos, id) => {
              cy.getElementById(id).position({ x: pos.x, y: pos.y });
            });
          });
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
      {onColorModeChange && (
        <div className="absolute top-2 right-2 z-30 flex items-center gap-2 bg-gray-900/90 backdrop-blur rounded-lg border border-gray-700 px-2 py-1 text-xs">
          <span className="text-gray-400">Color:</span>
          <button
            onClick={() => onColorModeChange("type")}
            className={`px-2 py-0.5 rounded ${colorMode === "type" ? "bg-indigo-600 text-white" : "text-gray-300 hover:bg-gray-800"}`}
          >
            By Type
          </button>
          <button
            onClick={() => onColorModeChange("complexity")}
            className={`px-2 py-0.5 rounded ${colorMode === "complexity" ? "bg-indigo-600 text-white" : "text-gray-300 hover:bg-gray-800"}`}
          >
            By Complexity
          </button>
          {colorMode === "complexity" && (
            <div className="flex items-center gap-1 ml-2 border-l border-gray-700 pl-2">
              {COMPLEXITY_COLORS.map((c, i) => (
                <div key={i} className="flex items-center gap-0.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c }} />
                  <span className="text-gray-400">{i + 1}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
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
