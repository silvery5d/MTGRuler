# Findings & Decisions

## Requirements
-

## Research Findings

### 参考文章：用 Claude Code 将 Obsidian 笔记变成知识图谱
- **核心方法**：用 Claude Code 直接解析 Obsidian Markdown 笔记 → 提取概念和关系 → 生成交互式知识图谱网站
- **三层结构**：10个投资概念 → 61家公司档案 → 7位关键人物（分层组织）
- **技术要点**：
  - LLM 负责从非结构化文本中抽取实体、关系、属性
  - 不只是翻译，而是重新组织和结构化信息
  - 最终部署为静态站点（GitHub Pages / Cloudflare Pages）
  - 从 Obsidian 笔记到上线，一个会话内完成
- **对本项目的启发**：
  - 可以用 LLM 辅助解析万智牌规则文本，提取概念和关系
  - 分层结构适合万智牌规则（大章节 → 子章节 → 具体规则条目）
  - 交互式可视化是最终呈现形态
- **部署地址**：https://farther-homes-are.pages.dev

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
|          |           |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
-

## Visual/Browser Findings
-

---
*Update this file after every 2 view/browser/search operations*
