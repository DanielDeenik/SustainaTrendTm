// Improved SustainaTrend Dashboard
// This is a manually created bundle that connects to our API
(function() {
  console.log('SustainaTrend React Dashboard loading...');
  
  document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('react-trend-dashboard');
    if (container) {
      // First, show a loading indicator
      container.innerHTML = `
        <div class="d-flex justify-content-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
      `;
      
      // Fetch trend data
      fetch('/api/trends')
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            renderDashboard(container, data);
          } else {
            container.innerHTML = `
              <div class="alert alert-danger">
                Error loading trend data: ${data.error || 'Unknown error'}
              </div>
            `;
          }
        })
        .catch(error => {
          console.error('Error fetching trend data:', error);
          container.innerHTML = `
            <div class="alert alert-danger">
              Failed to fetch trend data. Please try again later.
            </div>
          `;
        });
    }
  });
  
  function renderDashboard(container, data) {
    console.log('Rendering dashboard with data:', data);
    const { trends, chart_data, category_counts } = data;
    
    // Create the dashboard structure
    container.innerHTML = `
      <div class="container py-4">
        <div class="row mb-4">
          <div class="col-md-8 offset-md-2">
            <div class="card">
              <div class="card-body">
                <form id="trend-filter-form" class="d-flex flex-wrap gap-3 justify-content-between">
                  <div class="form-group">
                    <label for="category-filter">Filter by Category</label>
                    <select id="category-filter" class="form-select">
                      <option value="all">All Categories</option>
                      ${Object.keys(category_counts).map(cat => 
                        `<option value="${cat}">${cat.charAt(0).toUpperCase() + cat.slice(1)} (${category_counts[cat]})</option>`
                      ).join('')}
                    </select>
                  </div>
                  <div class="form-group">
                    <label for="sort-by">Sort by</label>
                    <select id="sort-by" class="form-select">
                      <option value="virality">Virality Score</option>
                      <option value="date">Date</option>
                      <option value="name">Name</option>
                    </select>
                  </div>
                  <div class="d-flex align-items-end">
                    <button type="button" id="apply-filters-btn" class="btn btn-primary">Apply Filters</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
        
        <div class="row mb-4">
          <div class="col-md-12">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">Sustainability Trends Overview</h5>
                <div class="chart-period">
                  <small class="text-muted">Trend Period: Last 6 months</small>
                </div>
              </div>
              <div class="card-body">
                <div id="trend-chart" style="height: 350px;" class="mt-3"></div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="row mb-4">
          <div class="col-md-6">
            <div class="card h-100">
              <div class="card-header">
                <h5 class="card-title">Category Distribution</h5>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-8">
                    <canvas id="category-chart" height="220"></canvas>
                  </div>
                  <div class="col-md-4">
                    <div class="d-flex flex-column gap-2 mt-3">
                      ${Object.entries(category_counts).map(([cat, count]) => `
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="badge bg-${getCategoryColor(cat)} me-2">${cat}</span>
                          <span class="fw-bold">${count}</span>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-6">
            <div class="card h-100">
              <div class="card-header">
                <h5 class="card-title">Top Trending Metrics</h5>
              </div>
              <div class="card-body">
                <ul class="list-group">
                  ${trends
                    .sort((a, b) => b.virality_score - a.virality_score)
                    .slice(0, 5)
                    .map(trend => `
                      <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                          <span class="badge bg-${getCategoryColor(trend.category)} me-2">${trend.category}</span>
                          ${trend.name}
                        </div>
                        <span class="badge bg-${getViralityColor(trend.virality_score)} rounded-pill">
                          ${Math.round(trend.virality_score)}
                        </span>
                      </li>
                    `).join('')}
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <h4 class="mb-3">Sustainability Trend Analysis</h4>
        <div class="row" id="trend-cards">
          ${trends.map(trend => `
            <div class="col-md-4 mb-4">
              <div class="card">
                <div class="card-header bg-${getCategoryColor(trend.category)} text-white">
                  <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${trend.name}</h5>
                    <span class="badge bg-light text-dark">${trend.category}</span>
                  </div>
                </div>
                <div class="card-body">
                  <div class="d-flex justify-content-between mb-3">
                    <div>
                      <h6>Current Value</h6>
                      <h4>${trend.current_value} ${trend.unit}</h4>
                    </div>
                    <div class="text-end">
                      <h6>Virality Score</h6>
                      <h3 class="text-${getViralityColor(trend.virality_score)}">${Math.round(trend.virality_score)}</h3>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <div class="d-flex justify-content-between">
                      <span>Trend Direction:</span>
                      <span class="text-${trend.trend_direction === 'improving' ? 'success' : 'danger'}">
                        ${trend.trend_direction === 'improving' ? '↑' : '↓'} ${Math.abs(trend.percent_change).toFixed(1)}%
                      </span>
                    </div>
                    <div class="d-flex justify-content-between">
                      <span>Duration:</span>
                      <span>${trend.trend_duration}</span>
                    </div>
                  </div>
                  
                  <div>
                    <small class="text-muted">Keywords:</small>
                    <div class="mt-1">
                      ${trend.keywords.map(kw => `<span class="badge bg-light text-dark me-1 mb-1">${kw}</span>`).join('')}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    
    // Initialize filter functionality
    const filterForm = document.getElementById('trend-filter-form');
    const categoryFilter = document.getElementById('category-filter');
    const sortByFilter = document.getElementById('sort-by');
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    
    applyFiltersBtn.addEventListener('click', function() {
      const category = categoryFilter.value;
      const sortBy = sortByFilter.value;
      
      let filteredTrends = [...trends];
      
      // Apply category filter
      if (category && category !== 'all') {
        filteredTrends = filteredTrends.filter(trend => trend.category === category);
      }
      
      // Apply sorting
      if (sortBy === 'virality') {
        filteredTrends.sort((a, b) => b.virality_score - a.virality_score);
      } else if (sortBy === 'date') {
        filteredTrends.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      } else if (sortBy === 'name') {
        filteredTrends.sort((a, b) => a.name.localeCompare(b.name));
      }
      
      // Update trend cards
      const trendCardsContainer = document.getElementById('trend-cards');
      trendCardsContainer.innerHTML = filteredTrends.length > 0 
        ? filteredTrends.map(trend => `
            <div class="col-md-4 mb-4">
              <div class="card">
                <div class="card-header bg-${getCategoryColor(trend.category)} text-white">
                  <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${trend.name}</h5>
                    <span class="badge bg-light text-dark">${trend.category}</span>
                  </div>
                </div>
                <div class="card-body">
                  <div class="d-flex justify-content-between mb-3">
                    <div>
                      <h6>Current Value</h6>
                      <h4>${trend.current_value} ${trend.unit}</h4>
                    </div>
                    <div class="text-end">
                      <h6>Virality Score</h6>
                      <h3 class="text-${getViralityColor(trend.virality_score)}">${Math.round(trend.virality_score)}</h3>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <div class="d-flex justify-content-between">
                      <span>Trend Direction:</span>
                      <span class="text-${trend.trend_direction === 'improving' ? 'success' : 'danger'}">
                        ${trend.trend_direction === 'improving' ? '↑' : '↓'} ${Math.abs(trend.percent_change).toFixed(1)}%
                      </span>
                    </div>
                    <div class="d-flex justify-content-between">
                      <span>Duration:</span>
                      <span>${trend.trend_duration}</span>
                    </div>
                  </div>
                  
                  <div>
                    <small class="text-muted">Keywords:</small>
                    <div class="mt-1">
                      ${trend.keywords.map(kw => `<span class="badge bg-light text-dark me-1 mb-1">${kw}</span>`).join('')}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          `).join('') 
        : `
          <div class="col-12">
            <div class="alert alert-info text-center">
              No trend data available for the selected filters.
            </div>
          </div>
        `;
    });
    
    console.log('SustainaTrend Dashboard loaded successfully');
  }
  
  function getCategoryColor(category) {
    const colorMap = {
      emissions: 'success',
      energy: 'primary',
      water: 'info',
      waste: 'secondary',
      social: 'purple'
    };
    return colorMap[category] || 'dark';
  }
  
  function getViralityColor(score) {
    if (score >= 70) return 'danger';
    if (score >= 40) return 'warning';
    return 'success';
  }
})();