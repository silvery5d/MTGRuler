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
  understanding_complexity: number | null;
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
  understanding_complexity: number | null;
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

export interface VersionInfo {
  set_code: string;
  set_name: string;
  release_date: string | null;
  prev_set_code: string | null;
  next_set_code: string | null;
}

export interface MetricsRecord {
  set_code: string;
  set_name: string;
  release_date: string | null;
  scale: {
    rule_count: number;
    rule_total_words: number;
    rule_avg_length: number;
    chapter_count: number;
    max_rule_depth: number;
  };
  graph: {
    concept_count: number;
    concept_count_by_type: Record<string, number>;
    relation_count: number;
    relation_count_by_type: Record<string, number>;
    isolated_concepts: number;
    highly_connected_count: number;
  };
  cognitive: {
    uc_total: number;
    uc_max: number;
    uc_avg: number;
    uc_p50: number;
    uc_p90: number;
    uc_p99: number;
    uc_top10_concepts: { id: string; uc: number; name_en: string }[];
    depends_on_chain_max: number;
  };
  mechanic: {
    keyword_count: number;
    keywords_added_since_prev: string[];
    keywords_removed_since_prev: string[];
    card_type_count: number;
    evergreen_keyword_count: number;
    high_complexity_keywords: number;
  };
}

export interface SpikeAnalysis {
  primary_culprits: {
    name: string;
    type: string;
    explanation: string;
    affected_concepts: string[];
    estimated_contribution_pct: number;
  }[];
  secondary_factors: any[];
  summary: string;
}

export interface SpikeRecord {
  set_code: string;
  set_name: string;
  release_date: string | null;
  prev_set_code: string;
  spiked_metrics: string[];
  deltas: Record<string, { pct: number; abs: number }>;
  delta_summary: string;
  analysis: SpikeAnalysis;
}
