import { AnalyticsService, type AnalyticsResult } from './analytics';
import type { Metric } from '$lib/types/schema';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true // Note: In production, use backend proxy
});

export interface AIAnalysis {
  summary: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  recommendations: string[];
  confidence: number;
  analyticsInsights: AnalyticsResult;
}

export async function analyzeMetric(metric: Metric, historicalMetrics: Metric[] = []): Promise<AIAnalysis> {
  try {
    // Get analytics insights
    const analyticsInsights = AnalyticsService.calculateTrend([...historicalMetrics, metric]);

    const prompt = `
    Analyze this sustainability metric:
    Name: ${metric.name}
    Category: ${metric.category}
    Current Value: ${metric.value} ${metric.unit}
    Historical Average: ${analyticsInsights.historicalAverage.toFixed(2)} ${metric.unit}
    Trend: ${analyticsInsights.trend}
    Change: ${analyticsInsights.percentageChange.toFixed(1)}%
    Anomaly Detected: ${analyticsInsights.anomalies ? 'Yes' : 'No'}

    Additional Insights:
    ${analyticsInsights.insights.join('\n')}

    Provide analysis in JSON format with:
    1. summary (one sentence)
    2. trend (increasing/decreasing/stable)
    3. recommendations (array of 2-3 specific actionable items)
    4. confidence (0-1)
    `;

    const response = await openai.chat.completions.create({
      model: "gpt-4-0125-preview",
      messages: [
        { 
          role: "system", 
          content: "You are a sustainability metrics analyst. Analyze the data and provide actionable insights."
        },
        { 
          role: "user", 
          content: prompt 
        }
      ],
      temperature: 0.7,
      response_format: { type: "json_object" }
    });

    const aiResponse = JSON.parse(response.choices[0].message.content);

    return {
      ...aiResponse,
      analyticsInsights
    };
  } catch (error) {
    console.error('AI analysis failed:', error);
    throw new Error('Failed to analyze metric');
  }
}