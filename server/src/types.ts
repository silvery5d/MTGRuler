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
