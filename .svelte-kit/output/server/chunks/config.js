const config = {
  apiUrl: "http://0.0.0.0:8000",
  // FastAPI backend
  development: true,
  version: "1.0.0",
  api: {
    metrics: "/api/metrics",
    reports: "/api/reports",
    analyses: "/api/analyses"
  }
};
{
  console.log("Frontend configuration:", config);
}
