import type Database from "better-sqlite3";

/**
 * Compute understanding complexity for every concept in the graph.
 *
 * Definition:
 *   uc(A) = complexity(A) + Σ uc(B)  for each B where A DEPENDS_ON B
 *
 * This captures the total cognitive load: the concept's own intrinsic
 * complexity plus all prerequisite knowledge required to understand it.
 * Cycles are broken by treating back-edges as 0.
 */
export function computeUnderstandingComplexity(
  db: Database.Database,
): Map<string, number> {
  const rows = db
    .prepare("SELECT id, complexity FROM concepts")
    .all() as { id: string; complexity: number | null }[];

  const baseCplx = new Map<string, number>();
  for (const r of rows) {
    baseCplx.set(r.id, r.complexity ?? 1);
  }

  const deps = db
    .prepare(
      "SELECT source_id, target_id FROM relations WHERE type = 'DEPENDS_ON'",
    )
    .all() as { source_id: string; target_id: string }[];

  const dependsOn = new Map<string, string[]>();
  for (const d of deps) {
    let list = dependsOn.get(d.source_id);
    if (!list) {
      list = [];
      dependsOn.set(d.source_id, list);
    }
    list.push(d.target_id);
  }

  const memo = new Map<string, number>();
  const inProgress = new Set<string>();

  function compute(id: string): number {
    if (memo.has(id)) return memo.get(id)!;
    if (inProgress.has(id)) return 0; // cycle — break it

    inProgress.add(id);
    const ownComplexity = baseCplx.get(id) ?? 1;
    const dependencies = dependsOn.get(id) ?? [];
    let sum = ownComplexity;
    for (const dep of dependencies) {
      sum += compute(dep);
    }
    inProgress.delete(id);
    memo.set(id, sum);
    return sum;
  }

  for (const r of rows) {
    compute(r.id);
  }

  return memo;
}
