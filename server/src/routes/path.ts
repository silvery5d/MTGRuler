import { Router } from "express";
import type Database from "better-sqlite3";
import { findShortestPath } from "../utils/pathfinder.js";

export function createPathRouter(db: Database.Database): Router {
  const router = Router();

  router.get("/", (req, res) => {
    const from = req.query.from as string;
    const to = req.query.to as string;

    if (!from || !to) {
      res
        .status(400)
        .json({ error: "Both 'from' and 'to' parameters are required" });
      return;
    }

    const result = findShortestPath(db, from, to);
    if (!result) {
      res
        .status(404)
        .json({ error: "No path found between the specified concepts" });
      return;
    }

    res.json(result);
  });

  return router;
}
