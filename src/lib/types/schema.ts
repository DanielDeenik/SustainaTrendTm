import { pgTable, serial, text, timestamp, numeric, integer, jsonb } from 'drizzle-orm/pg-core';
import { relations, sql } from 'drizzle-orm';
import { createInsertSchema } from 'drizzle-zod';
import { z } from 'zod';

// Metrics table to store environmental data points
export const metrics = pgTable('metrics', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  category: text('category').notNull(), // e.g., 'emissions', 'water', 'energy'
  value: numeric('value').notNull(),
  unit: text('unit').notNull(),
  timestamp: timestamp('timestamp').default(sql`CURRENT_TIMESTAMP`),
  metric_metadata: jsonb('metric_metadata').default({})
});

// Reports table for sustainability reporting
export const reports = pgTable('reports', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  description: text('description'),
  period_start: timestamp('period_start').notNull(),
  period_end: timestamp('period_end').notNull(),
  status: text('status').notNull().default('draft'), // draft, published, archived
  created_at: timestamp('created_at').default(sql`CURRENT_TIMESTAMP`),
  data: jsonb('data').default({})
});

// Analysis results for AI-driven insights
export const analyses = pgTable('analyses', {
  id: serial('id').primaryKey(),
  report_id: integer('report_id').references(() => reports.id),
  type: text('type').notNull(), // e.g., 'trend', 'forecast', 'anomaly'
  results: jsonb('results').notNull(),
  created_at: timestamp('created_at').default(sql`CURRENT_TIMESTAMP`),
  model_version: text('model_version').notNull()
});

// Define relations
export const reportsRelations = relations(reports, ({ many }) => ({
  analyses: many(analyses)
}));

export const analysesRelations = relations(analyses, ({ one }) => ({
  report: one(reports, {
    fields: [analyses.report_id],
    references: [reports.id]
  })
}));

// Define insert schemas
export const insertMetricSchema = createInsertSchema(metrics)
  .omit({ id: true, timestamp: true })
  .extend({
    category: z.enum(['emissions', 'water', 'energy', 'waste', 'social', 'governance']),
    value: z.number().min(0),
    metric_metadata: z.record(z.string(), z.any()).default({})
  });

export const insertReportSchema = createInsertSchema(reports)
  .omit({ id: true, created_at: true })
  .extend({
    status: z.enum(['draft', 'published', 'archived']).default('draft')
  });

export const insertAnalysisSchema = createInsertSchema(analyses)
  .omit({ id: true, created_at: true });

// Define types
export type Metric = typeof metrics.$inferSelect;
export type InsertMetric = typeof metrics.$inferInsert;
export type Report = typeof reports.$inferSelect;
export type InsertReport = typeof reports.$inferInsert;
export type Analysis = typeof analyses.$inferSelect;
export type InsertAnalysis = typeof analyses.$inferInsert;