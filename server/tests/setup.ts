import Database from "better-sqlite3";

const SCHEMA = `
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_cn TEXT NOT NULL,
    type TEXT NOT NULL,
    rule_ref TEXT,
    definition_en TEXT,
    definition_cn TEXT,
    chapter TEXT,
    complexity INTEGER,
    design_notes TEXT
);
CREATE TABLE IF NOT EXISTS relations (
    source_id TEXT,
    target_id TEXT,
    type TEXT NOT NULL,
    rule_ref TEXT,
    description TEXT,
    PRIMARY KEY (source_id, target_id, type)
);
CREATE TABLE IF NOT EXISTS rule_texts (
    rule_ref TEXT PRIMARY KEY,
    text_en TEXT,
    text_cn TEXT,
    parent_concept_id TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
    id, name_en, name_cn, definition_en, definition_cn,
    content='concepts', content_rowid='rowid'
);
CREATE VIRTUAL TABLE IF NOT EXISTS rule_texts_fts USING fts5(
    rule_ref, text_en, text_cn,
    content='rule_texts', content_rowid='rowid'
);
`;

interface ConceptSeed {
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

interface RelationSeed {
  source_id: string;
  target_id: string;
  type: string;
  rule_ref: string | null;
  description: string | null;
}

interface RuleTextSeed {
  rule_ref: string;
  text_en: string | null;
  text_cn: string | null;
  parent_concept_id: string | null;
}

const CONCEPTS: ConceptSeed[] = [
  {
    id: "keyword.flying",
    name_en: "Flying",
    name_cn: "飞行",
    type: "Keyword",
    rule_ref: "702.9",
    definition_en: "Can't be blocked except by flying/reach",
    definition_cn: "不能被不具飞行或延势的生物阻挡",
    chapter: "7",
    complexity: 2,
    design_notes: "Core evasion",
  },
  {
    id: "keyword.reach",
    name_en: "Reach",
    name_cn: "延势",
    type: "Keyword",
    rule_ref: "702.17",
    definition_en: "Can block flying",
    definition_cn: "可以阻挡飞行",
    chapter: "7",
    complexity: 1,
    design_notes: "Flying counter",
  },
  {
    id: "concept.stack",
    name_en: "Stack",
    name_cn: "堆叠",
    type: "Concept",
    rule_ref: "405",
    definition_en: "LIFO zone for spells/abilities",
    definition_cn: "后进先出的区域",
    chapter: "4",
    complexity: 4,
    design_notes: "Core resolution mechanic",
  },
  {
    id: "concept.priority",
    name_en: "Priority",
    name_cn: "优先权",
    type: "Concept",
    rule_ref: "117",
    definition_en: "Permission to act",
    definition_cn: "允许行动的权利",
    chapter: "1",
    complexity: 4,
    design_notes: "Turn structure core",
  },
  {
    id: "phase.combat",
    name_en: "Combat Phase",
    name_cn: "战斗阶段",
    type: "Phase",
    rule_ref: "506",
    definition_en: "Phase for attacking/blocking",
    definition_cn: "攻击和阻挡的阶段",
    chapter: "5",
    complexity: 3,
    design_notes: "Core gameplay",
  },
];

const RELATIONS: RelationSeed[] = [
  {
    source_id: "keyword.flying",
    target_id: "keyword.reach",
    type: "INTERACTS_WITH",
    rule_ref: "702.9a",
    description: "Reach can block flying",
  },
  {
    source_id: "concept.stack",
    target_id: "concept.priority",
    type: "DEPENDS_ON",
    rule_ref: "405.1",
    description: "Stack uses priority",
  },
  {
    source_id: "keyword.flying",
    target_id: "phase.combat",
    type: "OCCURS_IN",
    rule_ref: "702.9",
    description: "Flying matters in combat",
  },
];

const RULE_TEXTS: RuleTextSeed[] = [
  {
    rule_ref: "702.9",
    text_en: "Flying is a keyword ability.",
    text_cn: "飞行是关键字异能。",
    parent_concept_id: "keyword.flying",
  },
  {
    rule_ref: "702.9a",
    text_en: "A creature with flying...",
    text_cn: "具有飞行异能的生物...",
    parent_concept_id: "keyword.flying",
  },
];

// Apply Phase 1 CJK workaround: insert space between consecutive Han characters
// so FTS5 unicode61 tokenizer can match them.
function splitCjk(text: string | null): string | null {
  if (text == null) return text;
  return text.replace(/([\u3400-\u9fff])(?=[\u3400-\u9fff])/g, "$1 ");
}

export function createTestDb(): Database.Database {
  const db = new Database(":memory:");
  db.exec(SCHEMA);

  const insertConcept = db.prepare(
    `INSERT INTO concepts (id, name_en, name_cn, type, rule_ref, definition_en, definition_cn, chapter, complexity, design_notes)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  );
  for (const c of CONCEPTS) {
    insertConcept.run(
      c.id,
      c.name_en,
      c.name_cn,
      c.type,
      c.rule_ref,
      c.definition_en,
      c.definition_cn,
      c.chapter,
      c.complexity,
      c.design_notes,
    );
  }

  const insertRelation = db.prepare(
    `INSERT INTO relations (source_id, target_id, type, rule_ref, description)
     VALUES (?, ?, ?, ?, ?)`,
  );
  for (const r of RELATIONS) {
    insertRelation.run(
      r.source_id,
      r.target_id,
      r.type,
      r.rule_ref,
      r.description,
    );
  }

  const insertRuleText = db.prepare(
    `INSERT INTO rule_texts (rule_ref, text_en, text_cn, parent_concept_id)
     VALUES (?, ?, ?, ?)`,
  );
  for (const rt of RULE_TEXTS) {
    insertRuleText.run(
      rt.rule_ref,
      rt.text_en,
      rt.text_cn,
      rt.parent_concept_id,
    );
  }

  // Populate FTS tables with CJK-space-split text so FTS5 unicode61 can match.
  const insertConceptFts = db.prepare(
    `INSERT INTO concepts_fts(rowid, id, name_en, name_cn, definition_en, definition_cn)
     SELECT rowid, id, ?, ?, ?, ? FROM concepts WHERE id = ?`,
  );
  for (const c of CONCEPTS) {
    insertConceptFts.run(
      c.name_en,
      splitCjk(c.name_cn),
      c.definition_en,
      splitCjk(c.definition_cn),
      c.id,
    );
  }

  const insertRuleTextFts = db.prepare(
    `INSERT INTO rule_texts_fts(rowid, rule_ref, text_en, text_cn)
     SELECT rowid, rule_ref, ?, ? FROM rule_texts WHERE rule_ref = ?`,
  );
  for (const rt of RULE_TEXTS) {
    insertRuleTextFts.run(rt.text_en, splitCjk(rt.text_cn), rt.rule_ref);
  }

  return db;
}
