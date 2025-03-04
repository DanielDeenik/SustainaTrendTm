import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from 'recharts';
import { 
  ArrowUpRight, 
  ArrowDownRight, 
  Droplet, 
  Zap, 
  Recycle, 
  Cloud, 
  Users, 
  TrendingUp, 
  Filter, 
  BarChart2, 
  Circle, 
  PieChart as PieIcon,
  Award,
  Search,
  Sliders,
  RefreshCw
} from 'lucide-react';

// Category colors matching our CSS
const CATEGORY_COLORS = {
  emissions: '#10b981',
  energy: '#0ea5e9',
  water: '#06b6d4',
  waste: '#64748b',
  social: '#7c3aed'
};

// Virality score colors
const VIRALITY_COLORS = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#10b981'
};

const TrendCard = ({ trend }) => {
  // Determine icon based on category
  const renderCategoryIcon = (category) => {
    switch(category) {
      case 'emissions': return <Cloud size={20} />;
      case 'energy': return <Zap size={20} />;
      case 'water': return <Droplet size={20} />;
      case 'waste': return <Recycle size={20} />;
      case 'social': return <Users size={20} />;
      default: return <TrendingUp size={20} />;
    }
  };

  // Determine virality level
  const getViralityLevel = (score) => {
    if (score > 80) return 'high';
    if (score > 50) return 'medium';
    return 'low';
  };

  const viralityLevel = getViralityLevel(trend.virality_score);
  
  return (
    <div className="trend-card">
      <div className={`trend-header trend-${trend.category}`}>
        <span>{trend.name}</span>
        {renderCategoryIcon(trend.category)}
      </div>
      <div className="trend-body">
        <div className={`virality-score virality-${viralityLevel}`}>
          {Math.round(trend.virality_score)}
        </div>
        
        <h5 className="text-center mb-3">Virality Score</h5>
        
        <div className="mb-3">
          <strong>Trend Direction:</strong>
          <span className={trend.trend_direction === 'increasing' ? 'text-success' : 'text-danger'}>
            {trend.trend_direction === 'increasing' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
            {trend.trend_direction.charAt(0).toUpperCase() + trend.trend_direction.slice(1)}
          </span>
        </div>
        
        <div className="mb-3">
          <strong>Duration:</strong> 
          <span>
            {trend.trend_duration.charAt(0).toUpperCase() + trend.trend_duration.slice(1)}
          </span>
        </div>
        
        <div>
          <strong>Keywords:</strong>
          <div className="mt-2">
            {trend.keywords.split(',').map((keyword, index) => (
              <span key={index} className="keyword-chip">
                {keyword.trim()}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const FilterBar = ({ categories, onFilterChange }) => {
  const [category, setCategory] = useState('all');
  const [sort, setSort] = useState('virality');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onFilterChange({ category, sort });
  };
  
  return (
    <div className="filter-bar">
      <form onSubmit={handleSubmit} className="w-100 d-flex flex-wrap gap-3">
        <div className="filter-group">
          <span className="filter-group-label">Category</span>
          <div className="filter-control">
            <select 
              className="filter-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="all">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="filter-group">
          <span className="filter-group-label">Sort By</span>
          <div className="filter-control">
            <select 
              className="filter-select"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              <option value="virality">Virality Score</option>
              <option value="date">Date</option>
              <option value="name">Name</option>
            </select>
          </div>
        </div>
        
        <button type="submit" className="btn btn-primary">Apply Filters</button>
      </form>
    </div>
  );
};

const TrendChart = ({ chartData, categories }) => {
  if (!chartData || chartData.length === 0) {
    return <div className="alert alert-info">No trend data available for charting</div>;
  }
  
  // Use the categories props or extract from the chart data
  const chartCategories = categories || 
    [...new Set(Object.keys(chartData[0]).filter(key => key !== 'timestamp'))];
  
  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis domain={[0, 100]} label={{ value: 'Virality Score', angle: -90, position: 'insideLeft' }} />
        <Tooltip formatter={(value) => Math.round(value)} />
        <Legend />
        {chartCategories.map(category => (
          <Line 
            key={category}
            type="monotone"
            dataKey={category}
            name={category.charAt(0).toUpperCase() + category.slice(1)}
            stroke={CATEGORY_COLORS[category] || '#8884d8'}
            activeDot={{ r: 8 }}
            strokeWidth={2}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

// Summary metrics chart
const SummaryChart = ({ trends }) => {
  if (!trends || trends.length === 0) {
    return <div className="alert alert-info">No trend data available</div>;
  }
  
  // Calculate average virality by category
  const categoryData = {};
  trends.forEach(trend => {
    if (!categoryData[trend.category]) {
      categoryData[trend.category] = {
        total: 0,
        count: 0
      };
    }
    categoryData[trend.category].total += trend.virality_score;
    categoryData[trend.category].count += 1;
  });
  
  const data = Object.keys(categoryData).map(category => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    value: categoryData[category].total / categoryData[category].count
  }));
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" name="Avg. Virality Score">
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name.toLowerCase()] || '#8884d8'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

const TrendDistributionChart = ({ trends }) => {
  if (!trends || trends.length === 0) {
    return <div className="alert alert-info">No trend data available</div>;
  }
  
  // Count trends by category
  const categoryCount = {};
  trends.forEach(trend => {
    if (!categoryCount[trend.category]) {
      categoryCount[trend.category] = 0;
    }
    categoryCount[trend.category]++;
  });
  
  const data = Object.keys(categoryCount).map(category => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    value: categoryCount[category]
  }));
  
  const COLORS = Object.values(CATEGORY_COLORS);
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name.toLowerCase()] || COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

// Sustainability Screener Component
const SustainabilityScreener = ({ trends, onFilter }) => {
  const [viralityRange, setViralityRange] = useState([0, 100]);
  const [selectedCategories, setSelectedCategories] = useState([]); 
  const [trendDirections, setTrendDirections] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [materiality, setMateriality] = useState(0);
  const [complianceImpact, setComplianceImpact] = useState(0);
  
  const uniqueCategories = [...new Set(trends.map(trend => trend.category))];
  const uniqueDirections = [...new Set(trends.map(trend => trend.trend_direction))];
  
  const handleCategoryToggle = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter(c => c !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };
  
  const handleDirectionToggle = (direction) => {
    if (trendDirections.includes(direction)) {
      setTrendDirections(trendDirections.filter(d => d !== direction));
    } else {
      setTrendDirections([...trendDirections, direction]);
    }
  };
  
  const handleApplyFilters = () => {
    onFilter({
      viralityRange,
      categories: selectedCategories.length ? selectedCategories : null,
      directions: trendDirections.length ? trendDirections : null,
      materiality: materiality > 0 ? materiality : null,
      complianceImpact: complianceImpact > 0 ? complianceImpact : null
    });
  };
  
  const handleReset = () => {
    setViralityRange([0, 100]);
    setSelectedCategories([]);
    setTrendDirections([]);
    setMateriality(0);
    setComplianceImpact(0);
    
    onFilter({
      viralityRange: [0, 100],
      categories: null,
      directions: null,
      materiality: null,
      complianceImpact: null
    });
  };
  
  return (
    <div className="screener-panel">
      <div className="screener-title">
        <Sliders size={18} className="me-2" /> Sustainability Screener
        <div className="ms-auto">
          <button 
            className="btn btn-sm btn-outline-primary" 
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
          </button>
        </div>
      </div>
      
      <div className="screener-filters">
        <div>
          <label className="filter-label">Virality Score Range</label>
          <input
            type="range"
            className="range-slider"
            min="0"
            max="100"
            value={viralityRange[1]}
            onChange={(e) => setViralityRange([viralityRange[0], parseInt(e.target.value)])}
          />
          <div className="range-value-display">
            <span>{viralityRange[0]}</span>
            <span>{viralityRange[1]}</span>
          </div>
        </div>
        
        <div>
          <label className="filter-label">Categories</label>
          <div className="d-flex flex-wrap gap-2 mt-2">
            {uniqueCategories.map(category => (
              <button
                key={category}
                className={`btn btn-sm ${selectedCategories.includes(category) ? 'btn-primary' : 'btn-outline-secondary'}`}
                onClick={() => handleCategoryToggle(category)}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </button>
            ))}
          </div>
        </div>
        
        <div>
          <label className="filter-label">Trend Direction</label>
          <div className="d-flex gap-2 mt-2">
            {uniqueDirections.map(direction => (
              <button
                key={direction}
                className={`btn btn-sm ${trendDirections.includes(direction) ? 'btn-primary' : 'btn-outline-secondary'}`}
                onClick={() => handleDirectionToggle(direction)}
              >
                {direction === 'improving' ? (
                  <><ArrowUpRight size={14} className="me-1" /> Improving</>
                ) : (
                  <><ArrowDownRight size={14} className="me-1" /> Worsening</>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {showAdvanced && (
        <div className="screener-filters mt-3 border-top pt-3">
          <div>
            <label className="filter-label">Materiality Impact</label>
            <input
              type="range"
              className="range-slider"
              min="0"
              max="10"
              value={materiality}
              onChange={(e) => setMateriality(parseInt(e.target.value))}
            />
            <div className="range-value-display">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>
          
          <div>
            <label className="filter-label">Compliance Impact</label>
            <input
              type="range"
              className="range-slider"
              min="0"
              max="10"
              value={complianceImpact}
              onChange={(e) => setComplianceImpact(parseInt(e.target.value))}
            />
            <div className="range-value-display">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>
        </div>
      )}
      
      <div className="d-flex justify-content-end gap-2 mt-3">
        <button 
          className="btn btn-outline-secondary" 
          onClick={handleReset}
        >
          <RefreshCw size={16} className="me-1" /> Reset
        </button>
        <button 
          className="btn btn-primary" 
          onClick={handleApplyFilters}
        >
          <Filter size={16} className="me-1" /> Apply Filters
        </button>
      </div>
    </div>
  );
};

// Circular Chart Component 
const CircularChart = ({ value, color, label }) => {
  const circumference = 2 * Math.PI * 38; // 2πr where r is 38
  const strokeDashoffset = circumference - (value / 100) * circumference;
  
  return (
    <div className="circular-indicator">
      <svg width="120" height="120" viewBox="0 0 100 100">
        <circle 
          cx="50" 
          cy="50" 
          r="38" 
          className="circular-indicator-track" 
        />
        <circle 
          cx="50" 
          cy="50" 
          r="38" 
          className="circular-indicator-progress" 
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform="rotate(-90 50 50)"
        />
      </svg>
      <div className="circular-indicator-text">
        <p className="circular-indicator-value">{Math.round(value)}%</p>
        <p className="circular-indicator-label">{label}</p>
      </div>
    </div>
  );
};

// Radar Chart Component
const SustainabilityRadarChart = ({ trends }) => {
  if (!trends || trends.length === 0) {
    return <div className="alert alert-info">No trend data available</div>;
  }
  
  // Process data for radar chart
  const categoryData = {};
  const directionMultiplier = { 'improving': 1, 'worsening': -1 };
  
  trends.forEach(trend => {
    if (!categoryData[trend.category]) {
      categoryData[trend.category] = {
        score: 0,
        count: 0
      };
    }
    
    // Factor in trend direction for scoring
    const directionFactor = directionMultiplier[trend.trend_direction] || 1;
    categoryData[trend.category].score += trend.virality_score * directionFactor;
    categoryData[trend.category].count += 1;
  });
  
  // Normalize scores to be positive for radar display
  const radarData = [
    Object.keys(categoryData).reduce((obj, key) => {
      // Convert to 0-100 scale with positive values
      const avgScore = categoryData[key].count > 0 
        ? (categoryData[key].score / categoryData[key].count)
        : 0;
      
      // Make all values positive for radar display, but preserve relative magnitude
      const normalizedScore = Math.abs(avgScore);
      
      obj[key] = normalizedScore;
      obj.fullMark = 100;
      return obj;
    }, {})
  ];
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart outerRadius={90} data={radarData}>
        <PolarGrid />
        <PolarAngleAxis dataKey="name" />
        <PolarRadiusAxis domain={[0, 100]} />
        {Object.keys(categoryData).map((category) => (
          <Radar
            key={category}
            name={category.charAt(0).toUpperCase() + category.slice(1)}
            dataKey={category}
            stroke={CATEGORY_COLORS[category]}
            fill={CATEGORY_COLORS[category]}
            fillOpacity={0.3}
          />
        ))}
        <Legend />
        <Tooltip />
      </RadarChart>
    </ResponsiveContainer>
  );
};

// Company Benchmarking Component
const CompanyBenchmarking = () => {
  const mockCompanies = [
    { name: 'Your Company', emissions: 82, energy: 78, water: 90, waste: 65, social: 72 },
    { name: 'Industry Average', emissions: 65, energy: 60, water: 70, waste: 55, social: 60 },
    { name: 'Top Performer', emissions: 90, energy: 85, water: 95, waste: 85, social: 90 },
  ];
  
  // Calculate average scores
  const companies = mockCompanies.map(company => {
    const totalScore = (company.emissions + company.energy + company.water + company.waste + company.social) / 5;
    return { ...company, totalScore };
  });
  
  return (
    <div className="card">
      <div className="card-header">
        <h5 className="card-title d-flex align-items-center">
          <Award size={18} className="me-2" /> Company Benchmarking
        </h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Emissions</th>
                <th>Energy</th>
                <th>Water</th>
                <th>Waste</th>
                <th>Social</th>
                <th>Overall</th>
              </tr>
            </thead>
            <tbody>
              {companies.map((company, index) => (
                <tr key={index} className={company.name === 'Your Company' ? 'table-primary' : ''}>
                  <td><strong>{company.name}</strong></td>
                  <td>{company.emissions}%</td>
                  <td>{company.energy}%</td>
                  <td>{company.water}%</td>
                  <td>{company.waste}%</td>
                  <td>{company.social}%</td>
                  <td><strong>{Math.round(company.totalScore)}%</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Component
const TrendDashboard = () => {
  const [trends, setTrends] = useState([]);
  const [filteredTrends, setFilteredTrends] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryCount, setCategoryCount] = useState({});
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(document.documentElement.classList.contains('dark-mode'));
  const [displayMode, setDisplayMode] = useState('charts'); // 'charts' or 'cards'
  
  useEffect(() => {
    // Fetch trend data
    fetch('/api/trends')
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Set trends data
          if (data.trends) {
            setTrends(data.trends);
            setFilteredTrends(data.trends);
            
            // Extract unique categories
            const uniqueCategories = [...new Set(data.trends.map(trend => trend.category))];
            setCategories(uniqueCategories);
          }
          
          // Set chart data
          if (data.chart_data) {
            setChartData(data.chart_data);
          }
          
          // Set category counts
          if (data.category_counts) {
            setCategoryCount(data.category_counts);
          }
        }
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching trend data:', error);
        setLoading(false);
      });
  }, []);
  
  const handleFilterChange = ({ category, sort }) => {
    let filtered = [...trends];
    
    // Apply category filter
    if (category && category !== 'all') {
      filtered = filtered.filter(trend => trend.category === category);
    }
    
    // Apply sorting
    if (sort === 'virality') {
      filtered.sort((a, b) => b.virality_score - a.virality_score);
    } else if (sort === 'date') {
      filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    } else if (sort === 'name') {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    }
    
    setFilteredTrends(filtered);
  };
  
  const handleScreenerFilter = (filters) => {
    let filtered = [...trends];
    
    // Apply virality range filter
    if (filters.viralityRange) {
      filtered = filtered.filter(trend => 
        trend.virality_score >= filters.viralityRange[0] && 
        trend.virality_score <= filters.viralityRange[1]
      );
    }
    
    // Apply category filter
    if (filters.categories && filters.categories.length) {
      filtered = filtered.filter(trend => filters.categories.includes(trend.category));
    }
    
    // Apply direction filter
    if (filters.directions && filters.directions.length) {
      filtered = filtered.filter(trend => filters.directions.includes(trend.trend_direction));
    }
    
    setFilteredTrends(filtered);
  };
  
  const toggleTheme = () => {
    const isDarkMode = !darkMode;
    setDarkMode(isDarkMode);
    
    if (isDarkMode) {
      document.documentElement.classList.add('dark-mode');
      document.documentElement.classList.remove('light-mode');
    } else {
      document.documentElement.classList.add('light-mode');
      document.documentElement.classList.remove('dark-mode');
    }
  };
  
  if (loading) {
    return (
      <div className="d-flex justify-content-center my-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container py-4">
      {/* Theme Toggle */}
      <div className="d-flex justify-content-end mb-4">
        <div className="d-flex align-items-center me-3">
          <label className="toggle-switch me-2">
            <input 
              type="checkbox" 
              checked={darkMode} 
              onChange={toggleTheme}
            />
            <span className="toggle-slider"></span>
          </label>
          <span>{darkMode ? 'Dark Mode' : 'Light Mode'}</span>
        </div>
        
        <div className="btn-group">
          <button 
            className={`btn ${displayMode === 'charts' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setDisplayMode('charts')}
          >
            <BarChart2 size={16} className="me-1" /> Charts
          </button>
          <button 
            className={`btn ${displayMode === 'cards' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setDisplayMode('cards')}
          >
            <PieIcon size={16} className="me-1" /> Cards
          </button>
        </div>
      </div>
      
      {/* Sustainability Screener */}
      <div className="row mb-4">
        <div className="col-md-12">
          <SustainabilityScreener 
            trends={trends}
            onFilter={handleScreenerFilter}
          />
        </div>
      </div>
      
      {displayMode === 'charts' ? (
        <>
          {/* Charts View */}
          <div className="row mb-4">
            <div className="col-md-12">
              <div className="card">
                <div className="card-header">
                  <h5 className="card-title d-flex align-items-center">
                    <TrendingUp size={18} className="me-2" /> Sustainability Trends Overview
                  </h5>
                </div>
                <div className="card-body">
                  <TrendChart 
                    chartData={chartData} 
                    categories={categories} 
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div className="row mb-4">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5 className="card-title d-flex align-items-center">
                    <BarChart2 size={18} className="me-2" /> Average Virality by Category
                  </h5>
                </div>
                <div className="card-body">
                  <SummaryChart trends={trends} />
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5 className="card-title d-flex align-items-center">
                    <PieIcon size={18} className="me-2" /> Trend Distribution
                  </h5>
                </div>
                <div className="card-body">
                  <TrendDistributionChart trends={trends} />
                </div>
              </div>
            </div>
          </div>
          
          <div className="row mb-4">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5 className="card-title d-flex align-items-center">
                    <Circle size={18} className="me-2" /> Sustainability Performance
                  </h5>
                </div>
                <div className="card-body">
                  <SustainabilityRadarChart trends={filteredTrends} />
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5 className="card-title d-flex align-items-center">
                    <Search size={18} className="me-2" /> Key Metrics
                  </h5>
                </div>
                <div className="card-body">
                  <div className="row">
                    <div className="col-md-6 col-lg-4 mb-4">
                      <CircularChart 
                        value={75} 
                        color={CATEGORY_COLORS.emissions} 
                        label="Emissions" 
                      />
                    </div>
                    <div className="col-md-6 col-lg-4 mb-4">
                      <CircularChart 
                        value={62} 
                        color={CATEGORY_COLORS.energy} 
                        label="Energy" 
                      />
                    </div>
                    <div className="col-md-6 col-lg-4 mb-4">
                      <CircularChart 
                        value={88} 
                        color={CATEGORY_COLORS.water} 
                        label="Water" 
                      />
                    </div>
                    <div className="col-md-6 col-lg-4 mb-4">
                      <CircularChart 
                        value={81} 
                        color={CATEGORY_COLORS.waste} 
                        label="Waste" 
                      />
                    </div>
                    <div className="col-md-6 col-lg-4 mb-4">
                      <CircularChart 
                        value={70} 
                        color={CATEGORY_COLORS.social} 
                        label="Social" 
                      />
                    </div>
                    <div className="col-md-6 col-lg-4 mb-4">
                      <CircularChart 
                        value={79} 
                        color="#6366f1" 
                        label="Governance" 
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="row mb-4">
            <div className="col-md-12">
              <CompanyBenchmarking />
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Cards View */}
          <div className="row mb-4">
            <div className="col-md-12">
              <FilterBar 
                categories={categories} 
                onFilterChange={handleFilterChange} 
              />
            </div>
          </div>
          
          <div className="row">
            {filteredTrends.length > 0 ? (
              filteredTrends.map((trend, index) => (
                <div className="col-md-4 mb-4" key={index}>
                  <TrendCard trend={trend} />
                </div>
              ))
            ) : (
              <div className="col-12">
                <div className="alert alert-info text-center">
                  No trend data available for the selected filters.
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

// Render the component when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('react-trend-dashboard');
  if (container) {
    const root = createRoot(container);
    root.render(<TrendDashboard />);
  }
});

export default TrendDashboard;