import { j as json } from "../../../../chunks/index2.js";
import { s as storage, b as insertReportSchema } from "../../../../chunks/storage.js";
const GET = async () => {
  const reports = await storage.getReports();
  return json(reports);
};
const POST = async ({ request }) => {
  try {
    const body = await request.json();
    const report = insertReportSchema.parse(body);
    const created = await storage.createReport(report);
    return json(created, { status: 201 });
  } catch (error) {
    console.error("Error creating report:", error);
    return json({ error: "Invalid report data" }, { status: 400 });
  }
};
export {
  GET,
  POST
};
