import { json } from '@sveltejs/kit';
import { storage } from '$lib/db/storage';
import { insertMetricSchema } from '$lib/types/schema';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
  const category = url.searchParams.get('category') || undefined;
  const metrics = await storage.getMetrics(category);
  return json(metrics);
};

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = await request.json();
    const metric = insertMetricSchema.parse(body);
    const created = await storage.createMetric(metric);
    return json(created, { status: 201 });
  } catch (error) {
    console.error('Error creating metric:', error);
    return json({ error: 'Invalid metric data' }, { status: 400 });
  }
};
