import type { Metric } from '$lib/types/schema';

export interface AnalyticsResult {
  trend: 'up' | 'down' | 'stable';
  percentageChange: number;
  historicalAverage: number;
  anomalies: boolean;
  insights: string[];
  timeSeriesData: Array<{
    date: Date;
    value: number;
  }>;
  statistics: {
    min: number;
    max: number;
    stdDev: number;
    variance: number;
  };
}

export class AnalyticsService {
  static calculateTrend(metrics: Metric[]): AnalyticsResult {
    const sortedMetrics = [...metrics].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    const values = sortedMetrics.map(m => Number(m.value));
    const average = values.reduce((a, b) => a + b, 0) / values.length;
    const lastValue = values[values.length - 1];
    const firstValue = values[0];

    // Calculate basic statistics
    const min = Math.min(...values);
    const max = Math.max(...values);
    const variance = values.reduce((acc, val) => acc + Math.pow(val - average, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);

    // Calculate trend and percentage change
    const percentageChange = ((lastValue - firstValue) / firstValue) * 100;
    const trend: AnalyticsResult['trend'] = 
      percentageChange > 5 ? 'up' :
      percentageChange < -5 ? 'down' : 'stable';

    // Check for anomalies using z-score
    const anomalies = Math.abs(lastValue - average) > stdDev * 2;

    // Generate time series data for visualization
    const timeSeriesData = sortedMetrics.map(metric => ({
      date: new Date(metric.timestamp),
      value: Number(metric.value)
    }));

    // Generate insights based on the analysis
    const insights = [];
    if (anomalies) {
      insights.push(`Current value shows significant deviation from average (${average.toFixed(2)})`);
    }
    if (Math.abs(percentageChange) > 10) {
      insights.push(`Significant ${trend === 'up' ? 'increase' : 'decrease'} of ${Math.abs(percentageChange).toFixed(1)}%`);
    }
    if (lastValue > average * 1.5) {
      insights.push(`Current value (${lastValue.toFixed(2)}) is notably above historical average`);
    }
    if (values.length >= 3) {
      const recentTrend = values.slice(-3);
      const allIncreasing = recentTrend.every((val, i) => i === 0 || val > recentTrend[i - 1]);
      const allDecreasing = recentTrend.every((val, i) => i === 0 || val < recentTrend[i - 1]);
      if (allIncreasing) {
        insights.push('Consistent upward trend in last 3 measurements');
      } else if (allDecreasing) {
        insights.push('Consistent downward trend in last 3 measurements');
      }
    }

    return {
      trend,
      percentageChange,
      historicalAverage: average,
      anomalies,
      insights,
      timeSeriesData,
      statistics: {
        min,
        max,
        stdDev,
        variance
      }
    };
  }

  static summarizeMetrics(metrics: Metric[]): Record<string, AnalyticsResult> {
    // Group metrics by category
    const metricsByCategory = metrics.reduce((acc, metric) => {
      if (!acc[metric.category]) {
        acc[metric.category] = [];
      }
      acc[metric.category].push(metric);
      return acc;
    }, {} as Record<string, Metric[]>);

    // Calculate analytics for each category
    return Object.entries(metricsByCategory).reduce((acc, [category, metrics]) => {
      acc[category] = this.calculateTrend(metrics);
      return acc;
    }, {} as Record<string, AnalyticsResult>);
  }
}