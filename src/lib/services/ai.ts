import { config } from '$lib/config';
import type { Metric } from '$lib/types/schema';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  dangerouslyAllowBrowser: true // Only for demo, use backend proxy in production
});

export interface AIAnalysis {
  summary: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  recommendations: string[];
}

export async function analyzeMetric(metric: Metric): Promise<AIAnalysis> {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4-0125-preview",
      messages: [
        {
          role: "system",
          content: "You are a sustainability metrics analyst. Analyze the given metric and provide insights."
        },
        {
          role: "user",
          content: `Analyze this sustainability metric:
            Name: ${metric.name}
            Category: ${metric.category}
            Value: ${metric.value} ${metric.unit}
            Timestamp: ${metric.timestamp}
            
            Provide a brief analysis including:
            1. A one-sentence summary
            2. The apparent trend
            3. Two specific recommendations for improvement`
        }
      ],
      temperature: 0.7,
      max_tokens: 200
    });

    const content = response.choices[0]?.message?.content;
    if (!content) throw new Error("No analysis generated");

    // Parse the response into structured format
    const [summary, trend, ...recommendations] = content.split('\n').filter(Boolean);

    return {
      summary: summary.replace(/^Summary: /, ''),
      trend: (trend.toLowerCase().includes('increasing') ? 'increasing' :
             trend.toLowerCase().includes('decreasing') ? 'decreasing' : 'stable') as AIAnalysis['trend'],
      recommendations: recommendations.map(r => r.replace(/^\d+\. /, ''))
    };
  } catch (error) {
    console.error('AI analysis failed:', error);
    throw new Error('Failed to analyze metric');
  }
}
