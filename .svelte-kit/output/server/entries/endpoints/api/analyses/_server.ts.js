import { j as json } from "../../../../chunks/index2.js";
import { s as storage, i as insertAnalysisSchema } from "../../../../chunks/storage.js";
const GET = async ({ url }) => {
  const reportId = Number(url.searchParams.get("reportId"));
  if (!reportId || isNaN(reportId)) {
    return json({ error: "Report ID is required" }, { status: 400 });
  }
  const analyses = await storage.getAnalyses(reportId);
  return json(analyses);
};
const POST = async ({ request }) => {
  try {
    const body = await request.json();
    const analysis = insertAnalysisSchema.parse(body);
    const created = await storage.createAnalysis(analysis);
    return json(created, { status: 201 });
  } catch (error) {
    console.error("Error creating analysis:", error);
    return json({ error: "Invalid analysis data" }, { status: 400 });
  }
};
export {
  GET,
  POST
};
