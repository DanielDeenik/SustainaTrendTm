import { json } from '@sveltejs/kit';
import { storage } from '$lib/db/storage';
import { insertAnalysisSchema } from '$lib/types/schema';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
  const reportId = Number(url.searchParams.get('reportId'));
  if (!reportId || isNaN(reportId)) {
    return json({ error: 'Report ID is required' }, { status: 400 });
  }
  const analyses = await storage.getAnalyses(reportId);
  return json(analyses);
};

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = await request.json();
    const analysis = insertAnalysisSchema.parse(body);
    const created = await storage.createAnalysis(analysis);
    return json(created, { status: 201 });
  } catch (error) {
    console.error('Error creating analysis:', error);
    return json({ error: 'Invalid analysis data' }, { status: 400 });
  }
};
