import express from "express";
import cors from "cors";
import { getDb, closeDb } from "./db.js";
import { createConceptsRouter } from "./routes/concepts.js";
import { createRelationsRouter } from "./routes/relations.js";
import { createSearchRouter } from "./routes/search.js";
import { createPathRouter } from "./routes/path.js";
import { createGraphRouter } from "./routes/graph.js";
import { createStatsRouter } from "./routes/stats.js";

const app = express();
const PORT = parseInt(process.env.PORT || "3001");

app.use(cors());
app.use(express.json());

const db = getDb();

app.use("/api/v1/concepts", createConceptsRouter(db));
app.use("/api/v1/relations", createRelationsRouter(db));
app.use("/api/v1/search", createSearchRouter(db));
app.use("/api/v1/path", createPathRouter(db));
app.use("/api/v1/graph", createGraphRouter(db));
app.use("/api/v1/stats", createStatsRouter(db));

app.get("/api/v1/health", (_req, res) => {
  res.json({ status: "ok" });
});

const server = app.listen(PORT, () => {
  console.log(`MTGRuler API server running on http://localhost:${PORT}`);
  console.log(`  Endpoints: /api/v1/{concepts,relations,search,path,graph,stats}`);
});

process.on("SIGINT", () => {
  console.log("\nShutting down...");
  closeDb();
  server.close();
  process.exit(0);
});
