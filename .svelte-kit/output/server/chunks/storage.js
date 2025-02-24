import { sql, relations, desc, eq } from "drizzle-orm";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { pgTable, jsonb, timestamp, text, numeric, serial, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
const metrics = pgTable("metrics", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  category: text("category").notNull(),
  // e.g., 'emissions', 'water', 'energy'
  value: numeric("value").notNull(),
  unit: text("unit").notNull(),
  timestamp: timestamp("timestamp").default(sql`CURRENT_TIMESTAMP`),
  metric_metadata: jsonb("metric_metadata").default({})
});
const reports = pgTable("reports", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  period_start: timestamp("period_start").notNull(),
  period_end: timestamp("period_end").notNull(),
  status: text("status").notNull().default("draft"),
  // draft, published, archived
  created_at: timestamp("created_at").default(sql`CURRENT_TIMESTAMP`),
  data: jsonb("data").default({})
});
const analyses = pgTable("analyses", {
  id: serial("id").primaryKey(),
  report_id: integer("report_id").references(() => reports.id),
  type: text("type").notNull(),
  // e.g., 'trend', 'forecast', 'anomaly'
  results: jsonb("results").notNull(),
  created_at: timestamp("created_at").default(sql`CURRENT_TIMESTAMP`),
  model_version: text("model_version").notNull()
});
const reportsRelations = relations(reports, ({ many }) => ({
  analyses: many(analyses)
}));
const analysesRelations = relations(analyses, ({ one }) => ({
  report: one(reports, {
    fields: [analyses.report_id],
    references: [reports.id]
  })
}));
const insertMetricSchema = createInsertSchema(metrics).omit({ id: true, timestamp: true }).extend({
  category: z.enum(["emissions", "water", "energy", "waste", "social", "governance"]),
  value: z.number().min(0),
  metric_metadata: z.record(z.string(), z.any()).default({})
});
const insertReportSchema = createInsertSchema(reports).omit({ id: true, created_at: true }).extend({
  status: z.enum(["draft", "published", "archived"]).default("draft")
});
const insertAnalysisSchema = createInsertSchema(analyses).omit({ id: true, created_at: true });
const schema = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  analyses,
  analysesRelations,
  insertAnalysisSchema,
  insertMetricSchema,
  insertReportSchema,
  metrics,
  reports,
  reportsRelations
}, Symbol.toStringTag, { value: "Module" }));
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});
const db = drizzle(pool, { schema });
class DatabaseStorage {
  // Metrics
  async getMetrics(category) {
    const query = db.select().from(metrics).orderBy(desc(metrics.timestamp));
    if (category) {
      return await query.where(eq(metrics.category, category));
    }
    return await query;
  }
  async createMetric(metric) {
    const [created] = await db.insert(metrics).values(metric).returning();
    return created;
  }
  // Reports
  async getReports() {
    return await db.select().from(reports).orderBy(desc(reports.created_at));
  }
  async getReport(id) {
    const [report] = await db.select().from(reports).where(eq(reports.id, id));
    return report;
  }
  async createReport(report) {
    const [created] = await db.insert(reports).values(report).returning();
    return created;
  }
  // Analyses
  async getAnalyses(reportId) {
    return await db.select().from(analyses).where(eq(analyses.report_id, reportId)).orderBy(desc(analyses.created_at));
  }
  async createAnalysis(analysis) {
    const [created] = await db.insert(analyses).values(analysis).returning();
    return created;
  }
}
const storage = new DatabaseStorage();
export {
  insertMetricSchema as a,
  insertReportSchema as b,
  insertAnalysisSchema as i,
  storage as s
};
