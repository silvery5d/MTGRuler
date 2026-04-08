import { useEffect, useMemo, useState, useCallback } from "react";
import { GraphView } from "./components/GraphView.js";
import { SearchBar } from "./components/SearchBar.js";
import { DetailPanel } from "./components/DetailPanel.js";
import { PathQuery } from "./components/PathQuery.js";
import { StatusBar } from "./components/StatusBar.js";
import { ViewSwitcher } from "./components/ViewSwitcher.js";
import { HeatMap } from "./components/DesignerView/HeatMap.js";
import { ChapterOverview } from "./components/DesignerView/ChapterOverview.js";
import { InteractionMatrix } from "./components/DesignerView/InteractionMatrix.js";
import { DependencyGraph } from "./components/DesignerView/DependencyGraph.js";
import { useGraph } from "./hooks/useGraph.js";
import { useSearch } from "./hooks/useSearch.js";
import { api } from "./services/api.js";
import type { Stats } from "./types/index.js";

export default function App() {
  const graph = useGraph();
  const search = useSearch();
  const [pathMode, setPathMode] = useState(false);
  const [stats, setStats] = useState<Stats | null>(null);

  // Load initial graph + stats
  useEffect(() => {
    graph.loadGraph({ chapter: "4" }); // Start small — chapter 4 (zones)
    api.getStats().then(setStats);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reload graph when chapter filter changes
  useEffect(() => {
    if (graph.filters.chapter) {
      graph.loadGraph({ chapter: graph.filters.chapter });
    } else {
      graph.loadGraph();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graph.filters.chapter]);

  const handleNodeClick = useCallback(
    (nodeId: string) => {
      graph.selectConcept(nodeId);
    },
    [graph],
  );

  const handleSearchResultClick = useCallback(
    (conceptId: string) => {
      graph.selectConcept(conceptId);
      graph.loadGraph({ center: conceptId, depth: "2" });
    },
    [graph],
  );

  const handleChapterClick = useCallback(
    (chapter: string) => {
      graph.setFilters({ ...graph.filters, chapter });
      graph.setViewMode("graph");
    },
    [graph],
  );

  const searchForPath = useCallback(async (q: string) => {
    return api.search(q);
  }, []);

  const pathHighlightedNodes = useMemo(() => {
    if (!graph.pathResult) return undefined;
    return new Set(graph.pathResult.nodes.map((n) => n.id));
  }, [graph.pathResult]);

  const pathHighlightedEdges = useMemo(() => {
    if (!graph.pathResult) return undefined;
    return new Set(graph.pathResult.edges.map((e) => `${e.source}-${e.target}-${e.type}`));
  }, [graph.pathResult]);

  const renderView = () => {
    switch (graph.viewMode) {
      case "heatmap":
        return <HeatMap graphData={graph.graphData} onNodeClick={handleNodeClick} />;
      case "chapter-overview":
        return <ChapterOverview onChapterClick={handleChapterClick} />;
      case "interaction-matrix":
        return <InteractionMatrix onConceptClick={handleNodeClick} />;
      case "dependency":
        return <DependencyGraph onNodeClick={handleNodeClick} />;
      default:
        return (
          <GraphView
            elements={graph.cytoscapeElements}
            onNodeClick={handleNodeClick}
            highlightedNodes={pathHighlightedNodes}
            highlightedEdges={pathHighlightedEdges}
          />
        );
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-950 text-white overflow-hidden">
      <div className="flex items-center gap-2 flex-shrink-0">
        <div className="flex-1">
          <SearchBar
            query={search.query}
            results={search.results}
            loading={search.loading}
            onSearch={search.search}
            onClear={search.clear}
            onResultClick={handleSearchResultClick}
            onChapterFilter={(ch) => graph.setFilters({ ...graph.filters, chapter: ch })}
            onTypeFilter={(t) => graph.setFilters({ ...graph.filters, type: t })}
          />
        </div>
        <div className="pr-3 bg-gray-900 border-b border-gray-700 h-full flex items-center">
          <ViewSwitcher current={graph.viewMode} onChange={graph.setViewMode} />
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {renderView()}
        <DetailPanel
          detail={graph.selectedConcept}
          onClose={graph.clearSelection}
          onConceptClick={handleNodeClick}
        />
      </div>

      <StatusBar
        nodeCount={graph.graphData?.nodes.length ?? 0}
        totalCount={stats?.totals.concepts ?? null}
        loading={graph.loading}
        error={graph.error}
      >
        <PathQuery
          active={pathMode}
          pathResult={graph.pathResult}
          onToggle={() => {
            setPathMode(!pathMode);
            graph.clearPath();
          }}
          onFindPath={graph.findPath}
          onClear={graph.clearPath}
          searchFn={searchForPath}
        />
      </StatusBar>
    </div>
  );
}
