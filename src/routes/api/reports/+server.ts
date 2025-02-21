import { json } from '@sveltejs/kit';
import { storage } from '$lib/db/storage';
import { insertReportSchema } from '$lib/types/schema';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
  const reports = await storage.getReports();
  return json(reports);
};

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = await request.json();
    const report = insertReportSchema.parse(body);
    const created = await storage.createReport(report);
    return json(created, { status: 201 });
  } catch (error) {
    console.error('Error creating report:', error);
    return json({ error: 'Invalid report data' }, { status: 400 });
  }
};
