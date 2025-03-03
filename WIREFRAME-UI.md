# SustainaTrend™ Intelligence Platform - UI Wireframes

This document provides wireframe illustrations and UI descriptions for the SustainaTrend™ Intelligence Platform.

## Overall UI Structure

The SustainaTrend™ platform features a modern, responsive interface with a dark green sidebar and clean, white content areas. The UI is designed to be intuitive, accessible, and focused on data visualization and actionable insights.

```
+--------------------------------------+
|           HEADER/NAVBAR              |
+------+-------------------------------+
|      |                               |
|      |                               |
|      |                               |
|      |                               |
|  S   |       MAIN CONTENT            |
|  I   |                               |
|  D   |                               |
|  E   |                               |
|  B   |                               |
|  A   |                               |
|  R   |                               |
|      |                               |
|      |                               |
+------+-------------------------------+
|             FOOTER                   |
+--------------------------------------+
```

## Key UI Components

### 1. Navigation Sidebar

The left sidebar provides navigation through the application's main sections and features a consistent green branding.

```
+-------------------------+
| Sustainability          |
| Intelligence            |
+-------------------------+
| [•] Home                |
| [•] Dashboard           |
| [•] Analytics           |
+-------------------------+
| ANALYSIS TOOLS          |
+-------------------------+
| [•] AI Search           |
| [•] Gemini AI Search    |
| [•] Trend Analysis      |
| [•] Sustainability      |
|     Analysis            |
| [•] Sustainability      |
|     Stories             |
| [•] Monetization        |
|     Strategy            |
+-------------------------+
| SYSTEM                  |
+-------------------------+
| [•] API Status    [•]   |
| [•] Debug Info          |
| [•] Preferences         |
| [•] Help & Support      |
| [•] Account             |
+-------------------------+
```

The API Status item includes a colored indicator showing the current status:
- 🟢 Green: All APIs are available and functioning
- 🟠 Yellow: In fallback mode, some APIs unavailable
- 🔴 Red: No external APIs available, using mock data

### 2. Home Dashboard

The home page provides an overview of the platform's key features and quick access to main functions.

```
+---------------------------------------------------+
| SUSTAINABILITY INTELLIGENCE PLATFORM              |
+---------------------------------------------------+
| Welcome to SustainaTrend™                         |
|                                                   |
| +----------------+  +-------------------------+    |
| | QUICK SEARCH   |  | RECENT INSIGHTS         |    |
| | [Search bar]   |  | • Carbon trends rising  |    |
| | [Search button]|  | • Water usage improved  |    |
| +----------------+  | • New regulations       |    |
|                     +-------------------------+    |
|                                                   |
| +-------------------+  +----------------------+   |
| | SUSTAINABILITY    |  | AI-POWERED           |   |
| | METRICS           |  | STORYTELLING         |   |
| | [Metrics Chart]   |  | [Story Preview]      |   |
| |                   |  |                      |   |
| +-------------------+  +----------------------+   |
|                                                   |
| +-------------------------------------------+     |
| | TRENDING TOPICS IN SUSTAINABILITY         |     |
| | [Topic Cards with Icons]                  |     |
| +-------------------------------------------+     |
+---------------------------------------------------+
```

### 3. Gemini AI Search Interface

The Gemini-powered search interface combines advanced AI capabilities with a user-friendly design.

```
+---------------------------------------------------+
| GEMINI AI SEARCH                                  |
+---------------------------------------------------+
| Search for sustainability insights:               |
| +-----------------------------------------------+ |
| | [Search query input]             [Search]     | |
| +-----------------------------------------------+ |
|                                                   |
| Search Mode: [Hybrid ▼]  Category: [All ▼]        |
|                                                   |
| +-----------------------------------------------+ |
| | API STATUS                                    | |
| | Gemini AI: Available    Google Search: Error  | |
| | Status: Using Fallback Mode: Gemini only      | |
| | Error: Google API key too short               | |
| +-----------------------------------------------+ |
|                                                   |
| +-----------------------------------------------+ |
| | FILTERS                     [▼]               | |
| | Category [✓] Environment [✓] Social          | |
| | ...                                           | |
| | Sort By: [Relevance ▼]                        | |
| | [Apply Filters]    [Reset]                    | |
| +-----------------------------------------------+ |
|                                                   |
| Found 15 results (15 shown)                       |
|                                                   |
| +-----------------------------------------------+ |
| | Carbon Neutrality in Manufacturing            | |
| | https://example.com/carbon-neutrality         | |
| | This article discusses the latest approaches  | |
| | to achieving carbon neutrality in...          | |
| |                                               | |
| | 2025-01-15  ENVIRONMENT  GEMINI  95          | |
| +-----------------------------------------------+ |
|                                                   |
| +-----------------------------------------------+ |
| | Water Conservation Technologies               | |
| | ...                                           | |
| +-----------------------------------------------+ |
+---------------------------------------------------+
```

### 4. API Status Dashboard

The API Status Dashboard provides detailed information about the status of all external APIs used by the platform.

```
+---------------------------------------------------+
| API STATUS DASHBOARD                              |
+---------------------------------------------------+
|                                                   |
| +-------------------+  +----------------------+   |
| | GEMINI AI         |  | GOOGLE SEARCH        |   |
| | ● ONLINE          |  | ○ OFFLINE            |   |
| |                   |  |                      |   |
| | Status: Available |  | Status: Unavailable  |   |
| | API Key: Valid    |  | API Key: Invalid     |   |
| | Models: 37        |  | CSE ID: Valid        |   |
| |                   |  |                      |   |
| | Error: None       |  | Error: Google API    |   |
| |                   |  | key too short        |   |
| |                   |  |                      |   |
| | Last 5 Requests:  |  | Last 5 Requests:     |   |
| | 20:15:32 - 200 OK |  | 20:15:44 - 200 OK    |   |
| | 20:14:21 - 200 OK |  | 20:14:32 - 200 OK    |   |
| | ...               |  | ...                  |   |
| +-------------------+  +----------------------+   |
|                                                   |
| +-------------------------------------------+     |
| | SYSTEM STATUS                             |     |
| | Current Mode: Fallback - Gemini only      |     |
| | Using Real APIs: Yes                      |     |
| | Redis Cache: Offline                      |     |
| | Backend Status: Not Connected             |     |
| | Database Status: Not Connected            |     |
| +-------------------------------------------+     |
|                                                   |
| +-------------------------------------------+     |
| | API HEALTH HISTORY                        |     |
| | Gemini API Uptime (7 days): [95%]         |     |
| | Google Search API Uptime (7 days): [98%]  |     |
| |                                           |     |
| | [Response time chart would appear here]   |     |
| +-------------------------------------------+     |
|                                                   |
| +-------------------------------------------+     |
| | API CONFIGURATION                         |     |
| | Gemini API Key: AIza********************* |     |
| | Google API Key: ************************* |     |
| | Google CSE ID: 01757************:******* |     |
| +-------------------------------------------+     |
|                                                   |
| [Back to Dashboard]    [Refresh Status]           |
+---------------------------------------------------+
```

### 5. Trend Analysis Dashboard

The Trend Analysis Dashboard visualizes sustainability trends with predictive analytics.

```
+---------------------------------------------------+
| SUSTAINABILITY TREND ANALYSIS                     |
+---------------------------------------------------+
| Category: [All ▼]    Sort By: [Virality ▼]        |
|                                                   |
| +-------------------------------------------+     |
| | TRENDING SUSTAINABILITY TOPICS             |     |
| | [Interactive trend visualization chart]    |     |
| +-------------------------------------------+     |
|                                                   |
| +-------------------+  +----------------------+   |
| | HIGH VIRALITY     |  | TREND DURATION       |   |
| | TRENDS            |  | DISTRIBUTION         |   |
| | [Bubble chart]    |  | [Bar chart]          |   |
| +-------------------+  +----------------------+   |
|                                                   |
| Top Trending Sustainability Topics                |
|                                                   |
| +-------------------------------------------+     |
| | 1. Carbon Capture Technology              |     |
| |    ↑ 85% virality score                   |     |
| |    ↗ Improving (Long-term trend)          |     |
| |    Related: #cleantech #netzero           |     |
| +-------------------------------------------+     |
|                                                   |
| +-------------------------------------------+     |
| | 2. Biodiversity Accounting                |     |
| |    ↑ 78% virality score                   |     |
| |    → Stable (Medium-term trend)           |     |
| |    Related: #naturecapital #ESG           |     |
| +-------------------------------------------+     |
|                                                   |
| +-------------------------------------------+     |
| | PREDICTIVE INSIGHTS                       |     |
| | • Carbon metrics expected to gain 15%     |     |
| |   more attention in next quarter          |     |
| | • Water scarcity becoming critical topic  |     |
| |   in manufacturing sector                 |     |
| | • ESG reporting standards consolidation   |     |
| |   predicted within 6-8 months             |     |
| +-------------------------------------------+     |
+---------------------------------------------------+
```

### 6. Storytelling Interface

The Storytelling interface generates AI-powered sustainability narratives.

```
+---------------------------------------------------+
| SUSTAINABILITY STORYTELLING                       |
+---------------------------------------------------+
| Generate a sustainability story:                  |
|                                                   |
| Company: [Input field]       Industry: [Dropdown] |
| [Generate Story]                                  |
|                                                   |
| +-------------------------------------------+     |
| | SUSTAINABILITY TRANSFORMATION STORY       |     |
| |                                           |     |
| | Company: Acme Corporation                 |     |
| | Industry: Manufacturing                   |     |
| |                                           |     |
| | SUSTAINABILITY STRATEGY                   |     |
| | Acme Corporation has developed a          |     |
| | comprehensive approach to sustainability  |     |
| | focused on three key pillars:             |     |
| | 1. Carbon neutrality by 2030              |     |
| | 2. Zero waste manufacturing               |     |
| | 3. Sustainable supply chain               |     |
| |                                           |     |
| | COMPETITOR BENCHMARKING                   |     |
| | • Leading in energy efficiency (-15%)     |     |
| | • Behind in water conservation (+7%)      |     |
| | • Average in social impact initiatives    |     |
| |                                           |     |
| | MONETIZATION MODEL                        |     |
| | The company can monetize sustainability   |     |
| | through premium pricing (est. +4-7%),     |     |
| | operational cost savings ($1.2M/year),    |     |
| | and new market access.                    |     |
| |                                           |     |
| | INVESTMENT PATHWAY                        |     |
| | ...                                       |     |
| +-------------------------------------------+     |
|                                                   |
| [Save Story]  [Download PDF]  [Share]             |
+---------------------------------------------------+
```

### 7. Monetization Strategy Interface

The Monetization Strategy interface helps organizations identify business opportunities from sustainability initiatives.

```
+---------------------------------------------------+
| MONETIZATION STRATEGY                             |
+---------------------------------------------------+
| Develop sustainability monetization strategy:     |
|                                                   |
| Company: [Input field]       Industry: [Dropdown] |
| [Generate Strategy]                               |
|                                                   |
| +-------------------------------------------+     |
| | SUSTAINABILITY MONETIZATION STRATEGY      |     |
| |                                           |     |
| | 1. PREMIUM PRICING OPPORTUNITIES          |     |
| |    • Eco-certified product line: +12-18%  |     |
| |    • Carbon-neutral services: +8-15%      |     |
| |    • Circular packaging solutions: +5-8%  |     |
| |                                           |     |
| | 2. COST REDUCTION PATHWAYS                |     |
| |    • Energy efficiency: $1.2M/year        |     |
| |    • Waste reduction: $850K/year          |     |
| |    • Water conservation: $420K/year       |     |
| |                                           |     |
| | 3. NEW REVENUE STREAMS                    |     |
| |    • Sustainability consulting: $3-5M     |     |
| |    • Carbon credit generation: $1.8M      |     |
| |    • Technology licensing: $2.4M          |     |
| |                                           |     |
| | 4. FINANCIAL IMPACT ANALYSIS              |     |
| |    [ROI Chart]                            |     |
| |    Estimated 5-year ROI: 245%             |     |
| |    Initial investment required: $4.5M     |     |
| |    Payback period: 2.3 years              |     |
| +-------------------------------------------+     |
|                                                   |
| [Save Strategy]  [Download PDF]  [Share]          |
+---------------------------------------------------+
```

## Mobile Responsive Design

The SustainaTrend™ platform is fully responsive, with layouts optimized for different screen sizes:

### Mobile Layout
```
+-------------------------+
| Sustainability    ☰    |
+-------------------------+
|                         |
| DASHBOARD               |
|                         |
| Quick Search:           |
| [Search field]          |
|                         |
| Recent Insights:        |
| • Carbon trends rising  |
| • Water usage improved  |
|                         |
| Sustainability Metrics: |
| [Chart - simplified]    |
|                         |
| Trending Topics:        |
| [Scrollable cards]      |
|                         |
+-------------------------+
| Mobile Drawer Menu      |
+-------------+-----------+
| Home        | Settings  |
| Dashboard   | Help      |
| Search      | API Status|
| Trends      |           |
+-------------+-----------+
```

### Tablet Layout
```
+------+-------------------------+
| S    |                         |
| I    | DASHBOARD               |
| D    |                         |
| E    | +----------+------+     |
| B    | | Search   | Insights   |
| A    | +----------+------+     |
| R    |                         |
|      | [Metrics Chart]         |
| C    |                         |
| O    | [Trending Topics]       |
| L    |                         |
| L    |                         |
| A    |                         |
| P    |                         |
| S    |                         |
| E    |                         |
| D    |                         |
+------+-------------------------+
```

## UI Component Library

The platform uses consistent UI components across all pages:

### Cards
```
+------------------------+
| CARD TITLE             |
+------------------------+
| Card content with data |
| and visualization      |
|                        |
| [Call-to-action]       |
+------------------------+
```

### Alerts
```
+------------------------+
| ℹ️ Information Alert   |
+------------------------+

+------------------------+
| ⚠️ Warning Alert       |
+------------------------+

+------------------------+
| ❌ Error Alert         |
+------------------------+

+------------------------+
| ✅ Success Alert       |
+------------------------+
```

### Data Visualizations
```
+------------------------+
| VISUALIZATION TITLE    |
+------------------------+
| [Interactive Chart]    |
|                        |
| Legend:                |
| ● Series 1             |
| ● Series 2             |
+------------------------+
```

### API Status Indicators
```
Sidebar indicator:
[•] API Status    🟢

Status widget (expanded):
+------------------------+
| API STATUS             |
+------------------------+
| Gemini AI:    🟢 Online |
| Google Search: 🔴 Error |
|                        |
| Using: Fallback Mode   |
+------------------------+
```

## Color Palette

The SustainaTrend™ platform uses a consistent color scheme representing sustainability:

- **Primary Brand Color**: Dark Green (#052e16)
- **Secondary Brand Color**: Emerald Green (#10b981)
- **Accent Colors**:
  - Light Green (#d1fae5)
  - Alert Red (#ef4444)
  - Warning Yellow (#f59e0b)
  - Info Blue (#3b82f6)
  - Success Green (#10b981)
- **Neutral Colors**:
  - White (#ffffff)
  - Light Gray (#f3f4f6)
  - Medium Gray (#9ca3af)
  - Dark Gray (#1f2937)

## Typography

- **Primary Font**: Inter (sans-serif)
- **Headers**: Inter Semi-Bold
- **Body Text**: Inter Regular
- **Code/Technical**: Roboto Mono

## Iconography

The platform uses Bootstrap Icons for consistency, with special icons for sustainability concepts:

- 🌱 Plant/Growth: Sustainability initiatives
- 🔄 Circular arrows: Recycling, circular economy
- 💧 Water drop: Water metrics
- 🌫️ Cloud: Emissions and air quality
- 💡 Light bulb: Energy efficiency
- 📊 Charts: Analytics and data visualization
- 🔍 Magnifying glass: Search functionality
- 📝 Document: Reports and stories