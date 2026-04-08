export interface Concept {
  id: string;
  name_en: string;
  name_cn: string;
  type: string;
  rule_ref: string | null;
  definition_en: string | null;
  definition_cn: string | null;
  chapter: string | null;
  complexity: number | null;
  design_notes: string | null;
}

export interface Relation {
  source_id: string;
  target_id: string;
  type: string;
  rule_ref: string | null;
  description: string | null;
}

export interface RuleText {
  rule_ref: string;
  text_en: string | null;
  text_cn: string | null;
  parent_concept_id: string | null;
}

export interface GraphNode {
  id: string;
  name_en: string;
  name_cn: string;
  type: string;
  complexity: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ConceptDetail {
  concept: Concept;
  rule_texts: RuleText[];
  related: Concept[];
}

export interface PathResult {
  nodes: Concept[];
  edges: { source: string; target: string; type: string }[];
}

export interface Stats {
  totals: { concepts: number; relations: number; rule_texts: number };
  concepts_by_type: { type: string; count: number }[];
  concepts_by_chapter: { chapter: string; count: number }[];
  concepts_by_complexity: { complexity: number; count: number }[];
  relations_by_type: { type: string; count: number }[];
}

export type ViewMode = "graph" | "dependency" | "heatmap" | "chapter-overview" | "interaction-matrix";

export type NodeType = "Chapter" | "Concept" | "Zone" | "CardType" | "Phase" | "Step" | "Keyword" | "Action" | "MechanicPattern";
