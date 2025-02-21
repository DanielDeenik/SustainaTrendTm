import { eq, desc } from 'drizzle-orm';
import { db } from './index';
import { metrics, reports, analyses } from '../types/schema';
import type { Metric, InsertMetric, Report, InsertReport, Analysis, InsertAnalysis } from '../types/schema';

export interface IStorage {
  // Metrics
  getMetrics(category?: string): Promise<Metric[]>;
  createMetric(metric: InsertMetric): Promise<Metric>;

  // Reports
  getReports(): Promise<Report[]>;
  getReport(id: number): Promise<Report | undefined>;
  createReport(report: InsertReport): Promise<Report>;

  // Analyses
  getAnalyses(reportId: number): Promise<Analysis[]>;
  createAnalysis(analysis: InsertAnalysis): Promise<Analysis>;
}

export class DatabaseStorage implements IStorage {
  // Metrics
  async getMetrics(category?: string): Promise<Metric[]> {
    const query = db.select().from(metrics).orderBy(desc(metrics.timestamp));
    if (category) {
      return await query.where(eq(metrics.category, category));
    }
    return await query;
  }

  async createMetric(metric: InsertMetric): Promise<Metric> {
    const [created] = await db.insert(metrics).values(metric).returning();
    return created;
  }

  // Reports
  async getReports(): Promise<Report[]> {
    return await db.select().from(reports).orderBy(desc(reports.created_at));
  }

  async getReport(id: number): Promise<Report | undefined> {
    const [report] = await db.select().from(reports).where(eq(reports.id, id));
    return report;
  }

  async createReport(report: InsertReport): Promise<Report> {
    const [created] = await db.insert(reports).values(report).returning();
    return created;
  }

  // Analyses
  async getAnalyses(reportId: number): Promise<Analysis[]> {
    return await db
      .select()
      .from(analyses)
      .where(eq(analyses.report_id, reportId))
      .orderBy(desc(analyses.created_at));
  }

  async createAnalysis(analysis: InsertAnalysis): Promise<Analysis> {
    const [created] = await db.insert(analyses).values(analysis).returning();
    return created;
  }
}

export const storage = new DatabaseStorage();