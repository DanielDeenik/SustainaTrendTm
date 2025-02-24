import { j as json } from "../../../../chunks/index2.js";
import { s as storage, a as insertMetricSchema } from "../../../../chunks/storage.js";
const GET = async ({ url }) => {
  const category = url.searchParams.get("category") || void 0;
  const metrics = await storage.getMetrics(category);
  return json(metrics);
};
const POST = async ({ request }) => {
  try {
    const body = await request.json();
    const metric = insertMetricSchema.parse(body);
    const created = await storage.createMetric(metric);
    return json(created, { status: 201 });
  } catch (error) {
    console.error("Error creating metric:", error);
    return json({ error: "Invalid metric data" }, { status: 400 });
  }
};
export {
  GET,
  POST
};
