import { z } from "zod";

// Environmental Metrics Schema
export const environmentalMetricsSchema = z.object({
  carbonEmissions: z.number().min(0),
  energyUsage: z.number().min(0),
  wasteGeneration: z.number().min(0),
  waterConsumption: z.number().min(0),
  renewableEnergyPercentage: z.number().min(0).max(100),
  timestamp: z.string().datetime(),
});

// Social Metrics Schema
export const socialMetricsSchema = z.object({
  employeeCount: z.number().min(0),
  diversityScore: z.number().min(0).max(100),
  communityInvestment: z.number().min(0),
  employeeSatisfaction: z.number().min(0).max(100),
  healthAndSafetyIncidents: z.number().min(0),
  timestamp: z.string().datetime(),
});

// Governance Metrics Schema
export const governanceMetricsSchema = z.object({
  boardDiversity: z.number().min(0).max(100),
  ethicsViolations: z.number().min(0),
  policyCompliance: z.number().min(0).max(100),
  transparencyScore: z.number().min(0).max(100),
  riskManagementScore: z.number().min(0).max(100),
  timestamp: z.string().datetime(),
});

// Combined Sustainability Metrics
export const sustainabilityMetricsSchema = z.object({
  id: z.string().uuid().optional(),
  companyId: z.string(),
  environmental: environmentalMetricsSchema,
  social: socialMetricsSchema,
  governance: governanceMetricsSchema,
  overallScore: z.number().min(0).max(100),
  lastUpdated: z.string().datetime(),
});

// Export types
export type EnvironmentalMetrics = z.infer<typeof environmentalMetricsSchema>;
export type SocialMetrics = z.infer<typeof socialMetricsSchema>;
export type GovernanceMetrics = z.infer<typeof governanceMetricsSchema>;
export type SustainabilityMetrics = z.infer<typeof sustainabilityMetricsSchema>;
