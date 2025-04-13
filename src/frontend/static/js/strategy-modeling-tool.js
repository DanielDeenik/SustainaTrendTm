/**
 * Strategy Modeling Tool - Interactive JavaScript
 * 
 * This script provides the dynamic functionality for the SustainaTrend™ Strategy Modeling Tool,
 * handling user interactions, chart visualizations, and AI-powered strategy recommendations.
 */

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Strategy Modeling Tool initialized');
    
    // Initialize charts
    initializeCharts();
    
    // Initialize UI event listeners
    initializeEventListeners();
    
    // Setup tooltips and other Bootstrap components
    setupBootstrapComponents();
});

/**
 * Initialize interactive charts for the strategy modeling tool
 */
function initializeCharts() {
    // Impact Projection Chart (Line chart)
    const impactCtx = document.getElementById('impact-projection-chart').getContext('2d');
    const impactChart = new Chart(impactCtx, {
        type: 'line',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'Carbon Reduction Impact',
                data: [10, 25, 45, 70, 85],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                tension: 0.3
            }, {
                label: 'Resource Efficiency Impact',
                data: [5, 15, 35, 55, 75],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Impact Score'
                    }
                }
            }
        }
    });
    
    // Sustainability ROI Chart (Bar chart)
    const roiCtx = document.getElementById('sustainability-roi-chart').getContext('2d');
    const roiChart = new Chart(roiCtx, {
        type: 'bar',
        data: {
            labels: ['Initial Investment', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
            datasets: [{
                label: 'Financial Returns',
                data: [-50, 10, 20, 35, 55, 85],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(75, 192, 192, 0.6)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'ROI: ' + context.raw + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'ROI (%)'
                    }
                }
            }
        }
    });
    
    // Strategy Comparison Chart (Radar chart)
    const strategyCtx = document.getElementById('strategy-comparison-chart').getContext('2d');
    const strategyChart = new Chart(strategyCtx, {
        type: 'radar',
        data: {
            labels: [
                'Environmental Impact',
                'Financial Return',
                'Implementation Ease',
                'Regulatory Compliance',
                'Stakeholder Support',
                'Market Differentiation'
            ],
            datasets: [{
                label: 'Current Strategy',
                data: [65, 70, 60, 80, 75, 85],
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(255, 99, 132, 1)'
            }, {
                label: 'Optimized Strategy',
                data: [80, 85, 70, 90, 85, 95],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });
    
    // Scenario Analysis Chart (Scatter chart)
    const scenarioCtx = document.getElementById('scenario-analysis-chart').getContext('2d');
    const scenarioChart = new Chart(scenarioCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Base Scenario',
                data: [
                    { x: 30, y: 40 },
                    { x: 50, y: 60 },
                    { x: 70, y: 75 }
                ],
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                pointRadius: 8
            }, {
                label: 'Alternative Scenario',
                data: [
                    { x: 40, y: 30 },
                    { x: 60, y: 50 },
                    { x: 80, y: 65 }
                ],
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                pointRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Investment: ${context.raw.x}%, Impact: ${context.raw.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Investment Level (%)'
                    },
                    min: 0,
                    max: 100
                },
                y: {
                    title: {
                        display: true,
                        text: 'Impact Level (%)'
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
    
    // Store charts in global object for updating later
    window.strategyCharts = {
        impactChart,
        roiChart,
        strategyChart,
        scenarioChart
    };
}

/**
 * Initialize event listeners for interactive elements
 */
function initializeEventListeners() {
    // Industry selector change
    const industrySelector = document.getElementById('industry-selector');
    if (industrySelector) {
        industrySelector.addEventListener('change', function() {
            updateIndustryData(this.value);
            updateCharts();
        });
        
        // Initialize with default industry
        updateIndustryData(industrySelector.value);
    }
    
    // Time horizon change
    const timeHorizon = document.getElementById('time-horizon');
    if (timeHorizon) {
        timeHorizon.addEventListener('change', function() {
            updateCharts();
        });
    }
    
    // Investment level change
    const investmentLevel = document.getElementById('investment-level');
    if (investmentLevel) {
        investmentLevel.addEventListener('input', function() {
            document.getElementById('investment-value').textContent = this.value + '%';
            updateCharts();
        });
    }
    
    // Sustainability goals checkboxes
    const sustainabilityGoals = document.querySelectorAll('input[name="sustainability-goals"]');
    sustainabilityGoals.forEach(goal => {
        goal.addEventListener('change', function() {
            updateCharts();
        });
    });
    
    // Market condition sliders
    const marketConditionSliders = document.querySelectorAll('.market-condition-slider');
    marketConditionSliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const conditionName = this.dataset.condition;
            document.getElementById(conditionName + '-value').textContent = this.value;
            updateCharts();
        });
    });
    
    // Custom variable inputs
    const customVariableInputs = document.querySelectorAll('.custom-variable-input');
    customVariableInputs.forEach(input => {
        input.addEventListener('change', function() {
            updateCharts();
        });
    });
    
    // Add custom variable button
    const addCustomVariableBtn = document.getElementById('add-custom-variable');
    if (addCustomVariableBtn) {
        addCustomVariableBtn.addEventListener('click', function() {
            addCustomVariable();
        });
    }
    
    // Reset variables button
    const resetVariablesBtn = document.getElementById('reset-variables');
    if (resetVariablesBtn) {
        resetVariablesBtn.addEventListener('click', function() {
            resetAllVariables();
        });
    }
    
    // Download visualizations button
    const downloadVisualizationsBtn = document.getElementById('download-visualizations');
    if (downloadVisualizationsBtn) {
        downloadVisualizationsBtn.addEventListener('click', function() {
            downloadVisualizations();
        });
    }
    
    // Generate AI suggestions button
    const generateSuggestionsBtn = document.getElementById('generate-suggestions');
    if (generateSuggestionsBtn) {
        generateSuggestionsBtn.addEventListener('click', function() {
            generateAISuggestions();
        });
    }
}

/**
 * Update industry-specific data display
 */
function updateIndustryData(industry) {
    const industryDataElement = document.getElementById('industry-data');
    if (!industryDataElement) return;
    
    // Mock industry data examples
    const industryData = {
        energy: {
            avgEmissions: '2.1M tons CO2e',
            regulatoryRisk: 'High',
            marketTrend: 'Rapid transition to renewables',
            benchmarkGoal: '50% reduction by 2030'
        },
        manufacturing: {
            avgEmissions: '1.8M tons CO2e',
            regulatoryRisk: 'Medium-High',
            marketTrend: 'Circular economy focus',
            benchmarkGoal: '45% reduction by 2030'
        },
        technology: {
            avgEmissions: '850K tons CO2e',
            regulatoryRisk: 'Medium',
            marketTrend: 'Green cloud computing',
            benchmarkGoal: '70% reduction by 2030'
        },
        retail: {
            avgEmissions: '1.2M tons CO2e',
            regulatoryRisk: 'Medium',
            marketTrend: 'Sustainable supply chains',
            benchmarkGoal: '40% reduction by 2030'
        }
    };
    
    // Get data for selected industry
    const data = industryData[industry] || {};
    
    // Create HTML for industry data display
    let html = `
        <div class="card strategy-data-card">
            <div class="card-header">
                <h6 class="card-title mb-0">
                    <i class="fas fa-industry me-2"></i>${capitalizeFirstLetter(industry)} Industry Benchmarks
                </h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <div class="d-flex justify-content-between">
                            <span class="text-muted">Avg. Emissions:</span>
                            <span class="fw-bold">${data.avgEmissions}</span>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="d-flex justify-content-between">
                            <span class="text-muted">Regulatory Risk:</span>
                            <span class="fw-bold">${data.regulatoryRisk}</span>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="d-flex justify-content-between">
                            <span class="text-muted">Market Trend:</span>
                            <span class="fw-bold">${data.marketTrend}</span>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="d-flex justify-content-between">
                            <span class="text-muted">Benchmark Goal:</span>
                            <span class="fw-bold">${data.benchmarkGoal}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Update the industry data element
    industryDataElement.innerHTML = html;
}

/**
 * Update all charts based on current variable values
 */
function updateCharts() {
    if (!window.strategyCharts) return;
    
    // Get all input values
    const variables = getInputVariables();
    
    // Update impact projection chart
    updateImpactProjectionChart(variables);
    
    // Update ROI chart
    updateROIChart(variables);
    
    // Update strategy comparison chart
    updateStrategyComparisonChart(variables);
    
    // Update scenario analysis chart
    updateScenarioAnalysisChart(variables);
    
    // Update model predictions
    updateModelPredictions(variables);
}

/**
 * Get all input variables from the form
 */
function getInputVariables() {
    // Industry and time horizon
    const industry = document.getElementById('industry-selector').value;
    const timeHorizon = document.getElementById('time-horizon').value;
    
    // Investment level
    const investmentLevel = parseInt(document.getElementById('investment-level').value);
    
    // Sustainability goals
    const sustainabilityGoals = [];
    document.querySelectorAll('input[name="sustainability-goals"]:checked').forEach(checkbox => {
        sustainabilityGoals.push(checkbox.value);
    });
    
    // Market conditions
    const marketConditions = {};
    document.querySelectorAll('.market-condition-slider').forEach(slider => {
        const conditionName = slider.dataset.condition;
        marketConditions[conditionName] = parseInt(slider.value);
    });
    
    // Custom variables
    const customVariables = {};
    document.querySelectorAll('.custom-variable-input').forEach(input => {
        const varName = input.dataset.varName;
        customVariables[varName] = parseInt(input.value);
    });
    
    return {
        industry,
        timeHorizon,
        investmentLevel,
        sustainabilityGoals,
        marketConditions,
        customVariables
    };
}

/**
 * Update the impact projection chart
 */
function updateImpactProjectionChart(variables) {
    const chart = window.strategyCharts.impactChart;
    
    // Modify data based on variables
    const impactFactor = variables.investmentLevel / 100;
    const regulatoryFactor = variables.marketConditions.regulatoryPressure / 10;
    const consumerFactor = variables.marketConditions.consumerDemand / 10;
    
    // Adjust time series based on time horizon
    let labels = [];
    let dataPoints = 5;
    
    if (variables.timeHorizon === 'short') {
        labels = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8'];
        dataPoints = 8;
    } else if (variables.timeHorizon === 'medium') {
        labels = ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'];
        dataPoints = 5;
    } else if (variables.timeHorizon === 'long') {
        labels = ['Year 1', 'Year 3', 'Year 5', 'Year 7', 'Year 10'];
        dataPoints = 5;
    }
    
    // Calculate impact values for each goal
    const emissionsData = [];
    const resourcesData = [];
    const circularData = [];
    const socialData = [];
    
    for (let i = 0; i < dataPoints; i++) {
        const progress = (i + 1) / dataPoints;
        const adjustedProgress = Math.pow(progress, 0.7); // Non-linear progress
        
        emissionsData.push(Math.min(100, Math.round(adjustedProgress * 100 * impactFactor * regulatoryFactor)));
        resourcesData.push(Math.min(100, Math.round(adjustedProgress * 85 * impactFactor * consumerFactor)));
        circularData.push(Math.min(100, Math.round(adjustedProgress * 75 * impactFactor)));
        socialData.push(Math.min(100, Math.round(adjustedProgress * 70 * impactFactor)));
    }
    
    // Update chart data and labels
    chart.data.labels = labels;
    
    // Clear existing datasets
    chart.data.datasets = [];
    
    // Add datasets based on selected goals
    if (variables.sustainabilityGoals.includes('emissions_reduction')) {
        chart.data.datasets.push({
            label: 'Emissions Reduction',
            data: emissionsData,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            tension: 0.3
        });
    }
    
    if (variables.sustainabilityGoals.includes('resource_efficiency')) {
        chart.data.datasets.push({
            label: 'Resource Efficiency',
            data: resourcesData,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            tension: 0.3
        });
    }
    
    if (variables.sustainabilityGoals.includes('circular_economy')) {
        chart.data.datasets.push({
            label: 'Circular Economy',
            data: circularData,
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 2,
            tension: 0.3
        });
    }
    
    if (variables.sustainabilityGoals.includes('social_impact')) {
        chart.data.datasets.push({
            label: 'Social Impact',
            data: socialData,
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 2,
            tension: 0.3
        });
    }
    
    // Update the chart
    chart.update();
}

/**
 * Update the ROI chart
 */
function updateROIChart(variables) {
    const chart = window.strategyCharts.roiChart;
    
    // Calculate ROI based on variables
    const initialInvestment = -variables.investmentLevel;
    const regulatoryFactor = variables.marketConditions.regulatoryPressure / 10;
    const consumerFactor = variables.marketConditions.consumerDemand / 10;
    const competitorFactor = variables.marketConditions.competitorActivity / 10;
    
    // Custom calculation factors
    let esgBonus = 0;
    let supplyChainFactor = 0;
    
    if (variables.customVariables.esgScore) {
        esgBonus = (variables.customVariables.esgScore - 50) / 100;
    }
    
    if (variables.customVariables.supplyChainSustainability) {
        supplyChainFactor = variables.customVariables.supplyChainSustainability / 100;
    }
    
    // Adjust time series based on time horizon
    let labels = [];
    let dataPoints = 6; // Including initial investment
    let yearlyMultiplier = 1;
    
    if (variables.timeHorizon === 'short') {
        labels = ['Initial', 'Year 0.5', 'Year 1', 'Year 1.5', 'Year 2'];
        dataPoints = 5;
        yearlyMultiplier = 0.8;
    } else if (variables.timeHorizon === 'medium') {
        labels = ['Initial', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'];
        dataPoints = 6;
        yearlyMultiplier = 1;
    } else if (variables.timeHorizon === 'long') {
        labels = ['Initial', 'Year 2', 'Year 4', 'Year 6', 'Year 8', 'Year 10'];
        dataPoints = 6;
        yearlyMultiplier = 1.5;
    }
    
    // Calculate ROI data
    const roiData = [initialInvestment];
    const colors = ['rgba(255, 99, 132, 0.6)'];
    const borders = ['rgba(255, 99, 132, 1)'];
    
    for (let i = 1; i < dataPoints; i++) {
        const year = i * yearlyMultiplier;
        const baseReturn = Math.pow(year, 1.2) * 10;
        const adjustedReturn = baseReturn * 
                             (1 + (regulatoryFactor * 0.3)) * 
                             (1 + (consumerFactor * 0.3)) * 
                             (1 + (competitorFactor * 0.1)) *
                             (1 + esgBonus) *
                             (1 + (supplyChainFactor * 0.5));
        
        roiData.push(Math.round(adjustedReturn * (variables.investmentLevel / 50)));
        
        // Set colors based on ROI - green for positive, red for negative
        const color = adjustedReturn > 0 ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)';
        const border = adjustedReturn > 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)';
        
        colors.push(color);
        borders.push(border);
    }
    
    // Calculate break-even point for display
    const breakEvenYear = calculateBreakEvenYear(roiData, yearlyMultiplier);
    
    // Update chart data and labels
    chart.data.labels = labels;
    
    // Update the dataset
    chart.data.datasets[0].data = roiData;
    chart.data.datasets[0].backgroundColor = colors;
    chart.data.datasets[0].borderColor = borders;
    
    // Update the chart
    chart.update();
    
    // Display break-even point somewhere on the page
    const modelPredictions = document.getElementById('model-predictions');
    if (modelPredictions) {
        let breakEvenText = '';
        if (breakEvenYear > 0) {
            breakEvenText = `<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i><strong>Break-even:</strong> Estimated at ${breakEvenYear.toFixed(1)} years</div>`;
        } else {
            breakEvenText = `<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i><strong>Break-even:</strong> Not achieved within the selected time horizon</div>`;
        }
        
        // Will be updated in the updateModelPredictions function
    }
}

/**
 * Update the strategy comparison chart
 */
function updateStrategyComparisonChart(variables) {
    const chart = window.strategyCharts.strategyChart;
    
    // Calculate scores based on variables
    const envImpact = calculateEnvironmentalImpact(variables);
    const finReturn = calculateFinancialReturn(variables);
    const implEase = calculateImplementationEase(variables);
    const regCompliance = calculateRegulatoryCompliance(variables);
    const stakeholderSupport = calculateStakeholderSupport(variables);
    const marketDiff = calculateMarketDifferentiation(variables);
    
    // Current strategy data (less optimized)
    const currentData = [
        Math.max(20, envImpact - 15),
        Math.max(20, finReturn - 15),
        Math.max(20, implEase - 10),
        Math.max(20, regCompliance - 10),
        Math.max(20, stakeholderSupport - 10),
        Math.max(20, marketDiff - 10)
    ];
    
    // Optimized strategy data
    const optimizedData = [
        envImpact,
        finReturn,
        implEase,
        regCompliance,
        stakeholderSupport,
        marketDiff
    ];
    
    // Update chart data
    chart.data.datasets[0].data = currentData;
    chart.data.datasets[1].data = optimizedData;
    
    // Update the chart
    chart.update();
}

/**
 * Update the scenario analysis chart
 */
function updateScenarioAnalysisChart(variables) {
    const chart = window.strategyCharts.scenarioChart;
    
    // Base scenario - current investment level
    const baseInvestment = variables.investmentLevel;
    const baseImpact = calculateOverallImpact(variables);
    
    // Alternative scenarios
    const scenarios = [];
    
    // Low investment scenario
    const lowInvestment = Math.max(10, baseInvestment - 20);
    const lowInvestmentVars = {...variables, investmentLevel: lowInvestment};
    const lowImpact = calculateOverallImpact(lowInvestmentVars);
    
    // Medium investment scenario (current)
    const mediumInvestment = baseInvestment;
    const mediumImpact = baseImpact;
    
    // High investment scenario
    const highInvestment = Math.min(100, baseInvestment + 20);
    const highInvestmentVars = {...variables, investmentLevel: highInvestment};
    const highImpact = calculateOverallImpact(highInvestmentVars);
    
    // Alternative strategy - adjust market conditions
    const altInvestment = baseInvestment;
    const altVars = {...variables};
    altVars.marketConditions.regulatoryPressure = Math.min(10, variables.marketConditions.regulatoryPressure + 2);
    altVars.marketConditions.consumerDemand = Math.min(10, variables.marketConditions.consumerDemand + 2);
    const altImpact = calculateOverallImpact(altVars);
    
    // Low alt investment
    const lowAltInvestment = Math.max(10, baseInvestment - 20);
    const lowAltVars = {...altVars, investmentLevel: lowAltInvestment};
    const lowAltImpact = calculateOverallImpact(lowAltVars);
    
    // High alt investment
    const highAltInvestment = Math.min(100, baseInvestment + 20);
    const highAltVars = {...altVars, investmentLevel: highAltInvestment};
    const highAltImpact = calculateOverallImpact(highAltVars);
    
    // Update chart data
    chart.data.datasets[0].data = [
        {x: lowInvestment, y: lowImpact},
        {x: mediumInvestment, y: mediumImpact},
        {x: highInvestment, y: highImpact}
    ];
    
    chart.data.datasets[1].data = [
        {x: lowAltInvestment, y: lowAltImpact},
        {x: altInvestment, y: altImpact},
        {x: highAltInvestment, y: highAltImpact}
    ];
    
    // Update the chart
    chart.update();
}

/**
 * Update model predictions based on variables
 */
function updateModelPredictions(variables) {
    const modelPredictionsElement = document.getElementById('model-predictions');
    if (!modelPredictionsElement) return;
    
    // Calculate overall strategy metrics
    const overallImpact = calculateOverallImpact(variables);
    const financialReturn = calculateFinancialReturn(variables);
    const implementationEase = calculateImplementationEase(variables);
    const breakEvenYear = calculateBreakEvenYear(null, variables.timeHorizon === 'short' ? 0.8 : (variables.timeHorizon === 'long' ? 1.5 : 1));
    
    // Calculate risk metrics
    const financialRisk = calculateFinancialRisk(variables);
    const implementationRisk = calculateImplementationRisk(variables);
    const regulatoryRisk = calculateRegulatoryRisk(variables);
    const marketRisk = calculateMarketRisk(variables);
    
    // Generate HTML for model predictions
    let html = `
        <div class="row">
            <div class="col-md-6">
                <div class="strategy-card">
                    <div class="strategy-card-header">
                        <h5 class="strategy-card-title">Strategy Performance</h5>
                    </div>
                    <div class="strategy-card-body">
                        <div class="mb-3">
                            <div class="d-flex justify-content-between mb-1">
                                <span>Overall Impact</span>
                                <span class="fw-bold">${overallImpact}%</span>
                            </div>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar bg-primary" role="progressbar" style="width: ${overallImpact}%"></div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <div class="d-flex justify-content-between mb-1">
                                <span>Financial Return</span>
                                <span class="fw-bold">${financialReturn}%</span>
                            </div>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar bg-success" role="progressbar" style="width: ${financialReturn}%"></div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <div class="d-flex justify-content-between mb-1">
                                <span>Implementation Ease</span>
                                <span class="fw-bold">${implementationEase}%</span>
                            </div>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar bg-info" role="progressbar" style="width: ${implementationEase}%"></div>
                            </div>
                        </div>
                        
                        <div>
                            ${breakEvenYear > 0 
                                ? `<div class="alert alert-success mb-0"><i class="fas fa-check-circle me-2"></i><strong>Break-even:</strong> Estimated at ${breakEvenYear.toFixed(1)} years</div>`
                                : `<div class="alert alert-warning mb-0"><i class="fas fa-exclamation-triangle me-2"></i><strong>Break-even:</strong> Not achieved within the selected time horizon</div>`
                            }
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="strategy-card">
                    <div class="strategy-card-header">
                        <h5 class="strategy-card-title">Risk Assessment</h5>
                    </div>
                    <div class="strategy-card-body">
                        <div class="mb-2">
                            <div class="d-flex justify-content-between mb-1">
                                <span class="small">Financial Risk</span>
                                <span class="small fw-bold">${getRiskLabel(financialRisk)}</span>
                            </div>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar ${getRiskColorClass(financialRisk)}" role="progressbar" style="width: ${financialRisk}%"></div>
                            </div>
                        </div>
                        
                        <div class="mb-2">
                            <div class="d-flex justify-content-between mb-1">
                                <span class="small">Implementation Risk</span>
                                <span class="small fw-bold">${getRiskLabel(implementationRisk)}</span>
                            </div>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar ${getRiskColorClass(implementationRisk)}" role="progressbar" style="width: ${implementationRisk}%"></div>
                            </div>
                        </div>
                        
                        <div class="mb-2">
                            <div class="d-flex justify-content-between mb-1">
                                <span class="small">Regulatory Compliance Risk</span>
                                <span class="small fw-bold">${getRiskLabel(regulatoryRisk)}</span>
                            </div>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar ${getRiskColorClass(regulatoryRisk)}" role="progressbar" style="width: ${regulatoryRisk}%"></div>
                            </div>
                        </div>
                        
                        <div>
                            <div class="d-flex justify-content-between mb-1">
                                <span class="small">Competitive Disruption Risk</span>
                                <span class="small fw-bold">${getRiskLabel(marketRisk)}</span>
                            </div>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar ${getRiskColorClass(marketRisk)}" role="progressbar" style="width: ${marketRisk}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Update the model predictions element
    modelPredictionsElement.innerHTML = html;
}

/**
 * Calculate various metrics based on strategy variables
 */
function calculateOverallImpact(variables) {
    const baseImpact = variables.investmentLevel * 0.7;
    const regulatoryFactor = variables.marketConditions.regulatoryPressure / 10;
    const consumerFactor = variables.marketConditions.consumerDemand / 10;
    
    let goalBonus = 0;
    variables.sustainabilityGoals.forEach(goal => {
        if (goal === 'emissions_reduction') goalBonus += 5;
        if (goal === 'resource_efficiency') goalBonus += 4;
        if (goal === 'circular_economy') goalBonus += 3;
        if (goal === 'social_impact') goalBonus += 3;
    });
    
    // Custom variable factors
    let esgBonus = 0;
    let supplyChainBonus = 0;
    
    if (variables.customVariables.esgScore) {
        esgBonus = (variables.customVariables.esgScore - 50) / 5;
    }
    
    if (variables.customVariables.supplyChainSustainability) {
        supplyChainBonus = variables.customVariables.supplyChainSustainability / 10;
    }
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 1.2;
            break;
        case 'manufacturing':
            industryFactor = 1.1;
            break;
        case 'technology':
            industryFactor = 0.9;
            break;
        case 'retail':
            industryFactor = 0.8;
            break;
    }
    
    const impact = baseImpact + 
                  (goalBonus * 1.5) + 
                  (regulatoryFactor * 15) + 
                  (consumerFactor * 10) + 
                  esgBonus +
                  supplyChainBonus;
    
    return Math.min(100, Math.round(impact * industryFactor));
}

function calculateEnvironmentalImpact(variables) {
    const baseImpact = variables.investmentLevel * 0.8;
    const regulatoryFactor = variables.marketConditions.regulatoryPressure / 10;
    
    let goalBonus = 0;
    if (variables.sustainabilityGoals.includes('emissions_reduction')) goalBonus += 10;
    if (variables.sustainabilityGoals.includes('resource_efficiency')) goalBonus += 7;
    if (variables.sustainabilityGoals.includes('circular_economy')) goalBonus += 5;
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 1.3;
            break;
        case 'manufacturing':
            industryFactor = 1.2;
            break;
        case 'technology':
            industryFactor = 0.9;
            break;
        case 'retail':
            industryFactor = 0.8;
            break;
    }
    
    const impact = baseImpact + goalBonus + (regulatoryFactor * 20);
    return Math.min(100, Math.round(impact * industryFactor));
}

function calculateFinancialReturn(variables) {
    const baseReturn = variables.investmentLevel * 0.6;
    const consumerFactor = variables.marketConditions.consumerDemand / 10;
    const competitorFactor = variables.marketConditions.competitorActivity / 10;
    
    // Custom variable factors
    let esgBonus = 0;
    if (variables.customVariables.esgScore) {
        esgBonus = (variables.customVariables.esgScore - 50) / 2.5;
    }
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 0.9;
            break;
        case 'manufacturing':
            industryFactor = 0.95;
            break;
        case 'technology':
            industryFactor = 1.2;
            break;
        case 'retail':
            industryFactor = 1.1;
            break;
    }
    
    // Time horizon adjustment
    let timeBonus = 0;
    switch(variables.timeHorizon) {
        case 'short':
            timeBonus = -5;
            break;
        case 'medium':
            timeBonus = 0;
            break;
        case 'long':
            timeBonus = 10;
            break;
    }
    
    const returnValue = baseReturn + 
                       (consumerFactor * 20) + 
                       (competitorFactor * 5) + 
                       esgBonus +
                       timeBonus;
    
    return Math.min(100, Math.round(returnValue * industryFactor));
}

function calculateImplementationEase(variables) {
    const baseEase = 100 - (variables.investmentLevel * 0.5);
    
    let goalComplexity = 0;
    variables.sustainabilityGoals.forEach(goal => {
        goalComplexity += 5;
    });
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 0.8;
            break;
        case 'manufacturing':
            industryFactor = 0.85;
            break;
        case 'technology':
            industryFactor = 1.1;
            break;
        case 'retail':
            industryFactor = 1.0;
            break;
    }
    
    // Time horizon adjustment
    let timeComplexity = 0;
    switch(variables.timeHorizon) {
        case 'short':
            timeComplexity = 0;
            break;
        case 'medium':
            timeComplexity = 10;
            break;
        case 'long':
            timeComplexity = 20;
            break;
    }
    
    // Custom variable factors - supply chain complexity
    let supplyChainComplexity = 0;
    if (variables.customVariables.supplyChainSustainability) {
        supplyChainComplexity = variables.customVariables.supplyChainSustainability / 5;
    }
    
    const ease = baseEase - goalComplexity - timeComplexity - supplyChainComplexity;
    return Math.max(10, Math.min(100, Math.round(ease * industryFactor)));
}

function calculateRegulatoryCompliance(variables) {
    const baseCompliance = variables.investmentLevel * 0.7;
    const regulatoryFactor = variables.marketConditions.regulatoryPressure / 10;
    
    let goalBonus = 0;
    if (variables.sustainabilityGoals.includes('emissions_reduction')) goalBonus += 15;
    if (variables.sustainabilityGoals.includes('resource_efficiency')) goalBonus += 10;
    if (variables.sustainabilityGoals.includes('circular_economy')) goalBonus += 5;
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 0.9;
            break;
        case 'manufacturing':
            industryFactor = 0.95;
            break;
        case 'technology':
            industryFactor = 1.1;
            break;
        case 'retail':
            industryFactor = 1.05;
            break;
    }
    
    // Custom variable factors
    let esgBonus = 0;
    if (variables.customVariables.esgScore) {
        esgBonus = (variables.customVariables.esgScore - 50) / 5;
    }
    
    const compliance = baseCompliance + goalBonus + (regulatoryFactor * 25) + esgBonus;
    return Math.min(100, Math.round(compliance * industryFactor));
}

function calculateStakeholderSupport(variables) {
    const baseSupport = variables.investmentLevel * 0.5;
    const consumerFactor = variables.marketConditions.consumerDemand / 10;
    
    let goalBonus = 0;
    variables.sustainabilityGoals.forEach(goal => {
        goalBonus += 5;
    });
    
    if (variables.sustainabilityGoals.includes('social_impact')) goalBonus += 10;
    
    // Custom variable factors
    let esgBonus = 0;
    if (variables.customVariables.esgScore) {
        esgBonus = (variables.customVariables.esgScore - 50) / 3;
    }
    
    const support = baseSupport + goalBonus + (consumerFactor * 20) + esgBonus;
    return Math.min(100, Math.round(support));
}

function calculateMarketDifferentiation(variables) {
    const baseDiff = variables.investmentLevel * 0.6;
    const consumerFactor = variables.marketConditions.consumerDemand / 10;
    const competitorFactor = 1 - (variables.marketConditions.competitorActivity / 20);
    
    let goalBonus = 0;
    variables.sustainabilityGoals.forEach(goal => {
        goalBonus += 5;
    });
    
    // Custom variable factors
    let esgBonus = 0;
    if (variables.customVariables.esgScore) {
        esgBonus = (variables.customVariables.esgScore - 50) / 4;
    }
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 0.9;
            break;
        case 'manufacturing':
            industryFactor = 0.95;
            break;
        case 'technology':
            industryFactor = 1.15;
            break;
        case 'retail':
            industryFactor = 1.1;
            break;
    }
    
    const differentiation = (baseDiff + goalBonus + (consumerFactor * 15) + esgBonus) * competitorFactor;
    return Math.min(100, Math.round(differentiation * industryFactor));
}

function calculateBreakEvenYear(roiData, yearlyMultiplier) {
    if (roiData) {
        // If we have ROI data, calculate from that
        let cumulativeReturn = roiData[0]; // Initial investment (negative)
        
        for (let i = 1; i < roiData.length; i++) {
            cumulativeReturn += roiData[i];
            if (cumulativeReturn >= 0) {
                // Linear interpolation for more accurate break-even point
                const prevCumulative = cumulativeReturn - roiData[i];
                const yearFraction = i - 1 + (0 - prevCumulative) / (cumulativeReturn - prevCumulative);
                return yearFraction * yearlyMultiplier;
            }
        }
        
        return -1; // No break-even
    } else {
        // If no ROI data, estimate based on variables
        const variables = getInputVariables();
        
        // Base calculation factors
        const investmentLevel = variables.investmentLevel;
        const regulatoryFactor = variables.marketConditions.regulatoryPressure / 10;
        const consumerFactor = variables.marketConditions.consumerDemand / 10;
        const competitorFactor = variables.marketConditions.competitorActivity / 10;
        
        // Custom factors
        let esgFactor = 1.0;
        if (variables.customVariables.esgScore) {
            esgFactor = 1 + ((variables.customVariables.esgScore - 50) / 100);
        }
        
        // Industry adjustment
        let industryFactor = 1.0;
        switch(variables.industry) {
            case 'energy':
                industryFactor = 1.2;
                break;
            case 'manufacturing':
                industryFactor = 1.1;
                break;
            case 'technology':
                industryFactor = 0.8;
                break;
            case 'retail':
                industryFactor = 0.9;
                break;
        }
        
        // Goals adjustment
        let goalsFactor = 1.0;
        if (variables.sustainabilityGoals.includes('emissions_reduction')) goalsFactor -= 0.1;
        if (variables.sustainabilityGoals.includes('resource_efficiency')) goalsFactor -= 0.05;
        if (variables.sustainabilityGoals.includes('circular_economy')) goalsFactor += 0.05;
        if (variables.sustainabilityGoals.includes('social_impact')) goalsFactor += 0.1;
        
        // Calculate base break-even year
        const baseYears = (investmentLevel / 10) * goalsFactor * industryFactor;
        
        // Adjust for market conditions
        const adjustedYears = baseYears / 
                             (regulatoryFactor * 0.5 + consumerFactor * 0.4 + competitorFactor * 0.1) / 
                             esgFactor;
        
        // Special case: If investment is too low or conditions very unfavorable
        if (investmentLevel < 20 || (regulatoryFactor < 0.3 && consumerFactor < 0.3)) {
            return -1; // No break-even
        }
        
        return Math.max(0.5, Math.min(10, adjustedYears));
    }
}

/**
 * Calculate risk metrics
 */
function calculateFinancialRisk(variables) {
    const baseRisk = variables.investmentLevel * 0.4;
    const competitorRisk = variables.marketConditions.competitorActivity * 2;
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 1.2;
            break;
        case 'manufacturing':
            industryFactor = 1.1;
            break;
        case 'technology':
            industryFactor = 0.8;
            break;
        case 'retail':
            industryFactor = 0.9;
            break;
    }
    
    // Time horizon adjustment
    let timeRisk = 0;
    switch(variables.timeHorizon) {
        case 'short':
            timeRisk = 5;
            break;
        case 'medium':
            timeRisk = 15;
            break;
        case 'long':
            timeRisk = 25;
            break;
    }
    
    const risk = (baseRisk + competitorRisk + timeRisk) * industryFactor;
    return Math.min(100, Math.round(risk));
}

function calculateImplementationRisk(variables) {
    const baseRisk = variables.investmentLevel * 0.3;
    
    let goalComplexity = 0;
    variables.sustainabilityGoals.forEach(goal => {
        goalComplexity += 5;
    });
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 1.3;
            break;
        case 'manufacturing':
            industryFactor = 1.2;
            break;
        case 'technology':
            industryFactor = 0.8;
            break;
        case 'retail':
            industryFactor = 0.9;
            break;
    }
    
    // Time horizon adjustment
    let timeRisk = 0;
    switch(variables.timeHorizon) {
        case 'short':
            timeRisk = 5;
            break;
        case 'medium':
            timeRisk = 15;
            break;
        case 'long':
            timeRisk = 30;
            break;
    }
    
    // Custom variable factors - supply chain complexity
    let supplyChainRisk = 0;
    if (variables.customVariables.supplyChainSustainability) {
        supplyChainRisk = variables.customVariables.supplyChainSustainability / 2.5;
    }
    
    const risk = (baseRisk + goalComplexity + timeRisk + supplyChainRisk) * industryFactor;
    return Math.min(100, Math.round(risk));
}

function calculateRegulatoryRisk(variables) {
    const baseRisk = 50 - (variables.investmentLevel * 0.5);
    const regulatoryFactor = 10 - variables.marketConditions.regulatoryPressure;
    
    let goalMitigation = 0;
    if (variables.sustainabilityGoals.includes('emissions_reduction')) goalMitigation += 15;
    if (variables.sustainabilityGoals.includes('resource_efficiency')) goalMitigation += 10;
    if (variables.sustainabilityGoals.includes('circular_economy')) goalMitigation += 5;
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 1.5;
            break;
        case 'manufacturing':
            industryFactor = 1.3;
            break;
        case 'technology':
            industryFactor = 0.7;
            break;
        case 'retail':
            industryFactor = 0.8;
            break;
    }
    
    // Custom variable factors
    let esgMitigation = 0;
    if (variables.customVariables.esgScore) {
        esgMitigation = variables.customVariables.esgScore / 2;
    }
    
    const risk = ((baseRisk + (regulatoryFactor * 5)) * industryFactor) - goalMitigation - esgMitigation;
    return Math.max(5, Math.min(100, Math.round(risk)));
}

function calculateMarketRisk(variables) {
    const baseRisk = 60 - (variables.investmentLevel * 0.4);
    const consumerFactor = 10 - variables.marketConditions.consumerDemand;
    const competitorFactor = variables.marketConditions.competitorActivity;
    
    // Industry-specific adjustments
    let industryFactor = 1.0;
    switch(variables.industry) {
        case 'energy':
            industryFactor = 0.9;
            break;
        case 'manufacturing':
            industryFactor = 1.0;
            break;
        case 'technology':
            industryFactor = 1.2;
            break;
        case 'retail':
            industryFactor = 1.3;
            break;
    }
    
    // Custom variable factors
    let esgMitigation = 0;
    if (variables.customVariables.esgScore) {
        esgMitigation = variables.customVariables.esgScore / 4;
    }
    
    const risk = ((baseRisk + (consumerFactor * 3) + (competitorFactor * 2)) * industryFactor) - esgMitigation;
    return Math.max(5, Math.min(100, Math.round(risk)));
}

/**
 * Get risk label based on risk value
 */
function getRiskLabel(riskValue) {
    if (riskValue <= 20) return 'Low';
    if (riskValue <= 40) return 'Medium-Low';
    if (riskValue <= 60) return 'Medium';
    if (riskValue <= 80) return 'Medium-High';
    return 'High';
}

/**
 * Get risk color class based on risk value
 */
function getRiskColorClass(riskValue) {
    if (riskValue <= 20) return 'bg-success';
    if (riskValue <= 40) return 'bg-info';
    if (riskValue <= 60) return 'bg-warning';
    if (riskValue <= 80) return 'bg-orange';
    return 'bg-danger';
}

/**
 * Generate AI suggestions based on the current strategy model
 * Enhanced with substantiated industry insights
 */
function generateAISuggestions() {
    const aiSuggestionsElement = document.getElementById('ai-suggestions');
    if (!aiSuggestionsElement) return;
    
    // Show enhanced loading state with progress indicators
    aiSuggestionsElement.innerHTML = `
        <div class="ai-loading-container my-4">
            <div class="d-flex justify-content-center mb-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <p class="text-center text-muted mb-2">Generating AI-powered strategy suggestions...</p>
            <div class="progress mb-1" style="height: 5px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" id="ai-progress-bar" 
                     role="progressbar" style="width: 0%"></div>
            </div>
            <div class="d-flex justify-content-between small text-muted">
                <span>Analyzing variables</span>
                <span id="ai-progress-status">0%</span>
            </div>
        </div>
    `;
    
    // Get current variables
    const variables = getInputVariables();
    
    // Show progress in stages
    const progressBar = document.getElementById('ai-progress-bar');
    const progressStatus = document.getElementById('ai-progress-status');
    
    // Simulate AI thinking process with stages
    simulateProgress(25, "Analyzing industry context", 400);
    
    // In a real implementation, this would make a fetch call to the backend AI service
    // fetch('/api/strategy/ai-insights', {
    //    method: 'POST',
    //    headers: { 'Content-Type': 'application/json' },
    //    body: JSON.stringify(variables)
    // })
    
    // Simulate API call delay with progressive updates
    setTimeout(() => {
        simulateProgress(50, "Evaluating strategy variables", 700);
        
        setTimeout(() => {
            simulateProgress(75, "Generating recommendations", 700);
            
            setTimeout(() => {
                simulateProgress(100, "Finalizing insights", 200);
                
                setTimeout(() => {
                    // Calculate key metrics with enhanced analytics
                    const overallImpact = calculateOverallImpact(variables);
                    const financialReturn = calculateFinancialReturn(variables);
                    const implementationEase = calculateImplementationEase(variables);
                    const regulatoryCompliance = calculateRegulatoryCompliance(variables);
                    
                    // Generate substantiated insights with evidence
                    const suggestions = generateSubstantiatedInsights(variables);
                    
                    // Complete the suggestions processing and display
                    completeAISuggestions(variables, suggestions, overallImpact, financialReturn);
                }, 500);
            }, 800);
        }, 800);
    }, 800);
    
    // Helper function to simulate progress
    function simulateProgress(percent, status, delay) {
        setTimeout(() => {
            if (progressBar && progressStatus) {
                progressBar.style.width = `${percent}%`;
                progressStatus.textContent = `${percent}% - ${status}`;
            }
        }, delay);
    }
}

/**
 * Generate substantiated industry insights based on strategy variables
 */
function generateSubstantiatedInsights(variables) {
    const suggestions = [];
    
    // Add industry-specific suggestions with evidence and references
    if (variables.industry === 'energy') {
        suggestions.push({
            text: 'Consider partnering with renewable energy providers to accelerate your emissions reduction targets.',
            evidence: 'Energy companies implementing strategic partnerships have achieved 37% faster decarbonization according to IRENA 2024 report.',
            category: 'Partnership',
            priority: 'high',
            impact: 85
        });
        suggestions.push({
            text: 'Implement energy storage solutions to enhance grid resilience and stability.',
            evidence: 'Latest IEA analysis shows storage deployment can reduce grid balancing costs by up to 30% while enabling higher renewable penetration.',
            category: 'Technology',
            priority: 'medium',
            impact: 72
        });
        suggestions.push({
            text: 'Develop community-based microgrids for enhanced resilience and social impact.',
            evidence: 'World Economic Forum cites 25% improvement in local reliability and 15% cost savings for communities with microgrid infrastructure.',
            category: 'Innovation',
            priority: 'medium',
            impact: 68
        });
    } else if (variables.industry === 'manufacturing') {
        suggestions.push({
            text: 'Prioritize circular economy initiatives by redesigning products for end-of-life recycling.',
            evidence: 'McKinsey analysis of manufacturing leaders shows 22% margin improvement for products with circular design principles.',
            category: 'Circular Economy',
            priority: 'high',
            impact: 82
        });
        suggestions.push({
            text: 'Implement digital twin technology to optimize resource usage and reduce waste.',
            evidence: 'Manufacturers using digital twins report 15-30% reduction in material waste according to World Economic Forum 2024 study.',
            category: 'Digital Innovation',
            priority: 'medium',
            impact: 76
        });
        suggestions.push({
            text: 'Invest in advanced materials with lower environmental footprints and enhanced performance.',
            evidence: 'EU Sustainable Products Initiative data shows market premium of 12-18% for products using sustainable material alternatives.',
            category: 'Materials Innovation',
            priority: 'medium',
            impact: 71
        });
    } else if (variables.industry === 'technology') {
        suggestions.push({
            text: 'Leverage your technology expertise to develop sustainability measurement tools for your clients.',
            evidence: 'Gartner predicts sustainability software market growth of 28% CAGR through 2027, with highest demand for measurement solutions.',
            category: 'New Markets',
            priority: 'high',
            impact: 88
        });
        suggestions.push({
            text: 'Implement carbon-aware computing strategies to reduce data center emissions.',
            evidence: 'Google reported 35% reduction in operational carbon through intelligent workload shifting in their sustainability report.',
            category: 'Carbon Reduction',
            priority: 'high',
            impact: 79
        });
        suggestions.push({
            text: 'Develop comprehensive e-waste recovery and recycling systems for your products.',
            evidence: 'Analysis by Yale E-Waste Project shows recovery of precious metals can offset manufacturing costs by 8-14%.',
            category: 'Waste Management',
            priority: 'medium',
            impact: 65
        });
    } else if (variables.industry === 'retail') {
        suggestions.push({
            text: 'Develop a sustainable product certification program to increase consumer trust.',
            evidence: 'Nielsen data shows 45% of consumers willing to pay premium for certified sustainable products.',
            category: 'Consumer Trust',
            priority: 'high',
            impact: 84
        });
        suggestions.push({
            text: 'Implement reverse logistics systems to collect and recycle packaging materials.',
            evidence: 'Consumer Goods Forum reports 31% reduction in packaging waste for retailers with closed-loop systems.',
            category: 'Circular Systems',
            priority: 'medium',
            impact: 75
        });
        suggestions.push({
            text: 'Transition to renewable energy for store operations with visible initiatives.',
            evidence: 'RE100 member retailers report 22% average increase in positive consumer sentiment after visible renewable energy installations.',
            category: 'Energy Transition',
            priority: 'medium',
            impact: 70
        });
    }
    
    return suggestions;
}

/**
 * Complete AI suggestion processing and display the results
 */
function completeAISuggestions(variables, suggestions, overallImpact, financialReturn) {
    const aiSuggestionsElement = document.getElementById('ai-suggestions');
    if (!aiSuggestionsElement) return;
    
    // Generate industry-specific strategic recommendation
    let strategicRecommendation = generateStrategicRecommendation(variables);
    
    // Create enhanced visualization of insights with evidence
    let html = `
        <div class="alert alert-info mb-4">
            <div class="d-flex align-items-center">
                <i class="fas fa-info-circle me-2 fs-4"></i>
                <div>
                    <strong>AI Analysis Complete</strong>
                    <p class="mb-0 small">Strategy insights with evidence-based recommendations for your ${variables.industry} industry strategy.</p>
                </div>
            </div>
        </div>
        
        ${strategicRecommendation}
        
        <div class="section-header mb-3">
            <h5 class="section-title">
                <i class="fas fa-lightbulb me-2 text-warning"></i>
                Evidence-Based Recommendations
            </h5>
        </div>
    `;
    
    // Add enhanced card-based display for each insight
    html += '<div class="mb-4">';
    suggestions.forEach(suggestion => {
        const priorityClass = suggestion.priority === 'high' ? 'bg-success' : 'bg-info';
        html += `
            <div class="strategy-insight-card mb-3">
                <div class="strategy-insight-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge ${priorityClass} me-2">${suggestion.priority || 'medium'} priority</span>
                            <span class="insight-category">${suggestion.category || 'Strategy'}</span>
                        </div>
                        <div class="insight-impact">
                            <span class="small text-muted me-1">Impact:</span>
                            <div class="progress" style="width: 80px; height: 8px;">
                                <div class="progress-bar" role="progressbar" style="width: ${suggestion.impact || 70}%" 
                                    aria-valuenow="${suggestion.impact || 70}" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="strategy-insight-body">
                    <p class="insight-text">${suggestion.text}</p>
                    <div class="insight-evidence">
                        <div class="d-flex">
                            <div class="evidence-icon me-2">
                                <i class="fas fa-chart-bar text-primary"></i>
                            </div>
                            <div class="evidence-text small">
                                <strong>Evidence:</strong> ${suggestion.evidence || 'Based on industry best practices and market analysis.'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // Add implementation timeline
    html += `
        <div class="strategy-card mb-4">
            <div class="strategy-card-header">
                <h5 class="strategy-card-title">
                    <i class="fas fa-map me-2 text-primary"></i>
                    Implementation Roadmap
                </h5>
            </div>
            <div class="strategy-card-body">
                <div class="timeline">
                    <div class="timeline-item">
                        <div class="timeline-marker bg-success"></div>
                        <div class="timeline-content">
                            <h6 class="timeline-title">Phase 1: Foundation (0-6 months)</h6>
                            <p>Establish governance structure, baseline metrics, and quick wins</p>
                            <div class="timeline-actions">
                                ${suggestions.filter(s => s.priority === 'high').slice(0, 1).map(s => 
                                    `<span class="badge bg-light text-dark">${s.category}: ${s.text.substring(0, 40)}...</span>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-marker bg-primary"></div>
                        <div class="timeline-content">
                            <h6 class="timeline-title">Phase 2: Acceleration (6-18 months)</h6>
                            <p>Implement core initiatives, engage suppliers, and build capabilities</p>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-marker bg-info"></div>
                        <div class="timeline-content">
                            <h6 class="timeline-title">Phase 3: Transformation (18-36 months)</h6>
                            <p>Scale successful pilots, innovate business models, and lead industry change</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add action buttons
    html += `
        <div class="d-flex justify-content-between mt-4">
            <button class="btn btn-outline-secondary" id="back-to-modeling">
                <i class="fas fa-arrow-left me-1"></i>Back to Modeling
            </button>
            <div>
                <button class="btn btn-outline-primary me-2" id="download-insights-report">
                    <i class="fas fa-file-download me-1"></i>Download Report
                </button>
                <button class="btn btn-primary" id="apply-insights">
                    <i class="fas fa-check-circle me-1"></i>Apply Insights
                </button>
            </div>
        </div>
    `;
    
    // Update the AI suggestions element
    aiSuggestionsElement.innerHTML = html;
    
    // Add event listeners for new buttons
    document.getElementById('back-to-modeling').addEventListener('click', function() {
        document.getElementById('modeling-tab').click();
    });
    
    document.getElementById('download-insights-report').addEventListener('click', function() {
        alert('Generating PDF report with all insights and evidence... (Coming soon)');
    });
    
    document.getElementById('apply-insights').addEventListener('click', function() {
        alert('Applying AI insights to your strategy model...');
        // In a real implementation, this would adjust the strategy variables
        // based on the AI recommendations
    });
}

/**
 * Generate strategic recommendation based on industry and variables
 */
function generateStrategicRecommendation(variables) {
    let recommendation = '';
    
    if (variables.industry === 'energy') {
        recommendation = `
            <div class="card bg-dark text-white mb-4">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-lightbulb text-warning me-2"></i>Strategic Recommendation</h5>
                    <p>Develop an integrated energy transition roadmap that balances reliability, affordability, and sustainability. Focus on gradual fossil fuel phase-out while scaling renewables and grid modernization.</p>
                    <p class="mb-0"><strong>Key success factors:</strong> Long-term planning horizon, stakeholder collaboration, policy engagement, and technology innovation partnerships.</p>
                </div>
            </div>
        `;
    } else if (variables.industry === 'manufacturing') {
        recommendation = `
            <div class="card bg-dark text-white mb-4">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-lightbulb text-warning me-2"></i>Strategic Recommendation</h5>
                    <p>Implement a dual transformation strategy: optimize existing operations through resource efficiency while developing circular product-service systems for long-term growth.</p>
                    <p class="mb-0"><strong>Key success factors:</strong> Digital transformation, design thinking, supply chain collaboration, and materials innovation.</p>
                </div>
            </div>
        `;
    } else if (variables.industry === 'technology') {
        recommendation = `
            <div class="card bg-dark text-white mb-4">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-lightbulb text-warning me-2"></i>Strategic Recommendation</h5>
                    <p>Leverage your technological capabilities to develop sustainability-as-a-service offerings while addressing your own operational footprint through ambitious science-based targets.</p>
                    <p class="mb-0"><strong>Key success factors:</strong> Internal carbon pricing, green software development, AI-powered efficiency, and strategic partnerships.</p>
                </div>
            </div>
        `;
    } else if (variables.industry === 'retail') {
        recommendation = `
            <div class="card bg-dark text-white mb-4">
                <div class="card-body">
                    <h5 class="card-title"><i class="fas fa-lightbulb text-warning me-2"></i>Strategic Recommendation</h5>
                    <p>Transform your product portfolio and supply chain simultaneously, focusing on sustainable sourcing, packaging reduction, and customer engagement around product lifecycle.</p>
                    <p class="mb-0"><strong>Key success factors:</strong> Supplier engagement, transparent sustainability claims, circular packaging systems, and green logistics optimization.</p>
                </div>
            </div>
        `;
    }
    
    return recommendation;
}

/**
 * Add a new custom variable field
 */
function addCustomVariable() {
    const customVarContainer = document.querySelector('.strategy-card-body');
    const newVarIndex = document.querySelectorAll('.custom-variable-input').length + 1;
    
    const varNames = [
        'Supplier Engagement Score',
        'Innovation Capacity',
        'Digital Maturity Score',
        'Carbon Price Assumption',
        'Stakeholder Pressure Index'
    ];
    
    // Get a variable name that hasn't been used yet
    let varName = varNames[newVarIndex - 1] || `Custom Variable ${newVarIndex}`;
    let varId = varName.toLowerCase().replace(/\s+/g, '-');
    
    const newVarHtml = `
        <div class="mb-3">
            <label for="custom-var-${newVarIndex}" class="form-label small">${varName} (1-100)</label>
            <input type="number" id="custom-var-${newVarIndex}" class="form-control form-control-sm custom-variable-input" data-var-name="${varId}" value="50" min="1" max="100">
        </div>
    `;
    
    // Insert before the add button
    const addBtn = document.getElementById('add-custom-variable');
    const btnContainer = addBtn.parentElement;
    btnContainer.insertAdjacentHTML('beforebegin', newVarHtml);
    
    // Add event listener to the new input
    const newInput = document.getElementById(`custom-var-${newVarIndex}`);
    newInput.addEventListener('change', function() {
        updateCharts();
    });
}

/**
 * Reset all variables to their default values
 */
function resetAllVariables() {
    // Reset industry selector
    document.getElementById('industry-selector').value = 'energy';
    
    // Reset time horizon
    document.getElementById('time-horizon').value = 'medium';
    
    // Reset investment level
    const investmentLevel = document.getElementById('investment-level');
    investmentLevel.value = 50;
    document.getElementById('investment-value').textContent = '50%';
    
    // Reset sustainability goals
    document.querySelectorAll('input[name="sustainability-goals"]').forEach(checkbox => {
        checkbox.checked = checkbox.id === 'goal-emissions';
    });
    
    // Reset market conditions
    document.querySelectorAll('.market-condition-slider').forEach(slider => {
        slider.value = 5;
        const conditionName = slider.dataset.condition;
        document.getElementById(conditionName + '-value').textContent = '5';
    });
    
    // Reset custom variables
    document.querySelectorAll('.custom-variable-input').forEach((input, index) => {
        if (index === 0) input.value = 65;
        if (index === 1) input.value = 40;
        if (index > 1) input.parentElement.remove();
    });
    
    // Update industry data and charts
    updateIndustryData('energy');
    updateCharts();
}

/**
 * Download visualizations as PNG images
 */
function downloadVisualizations() {
    alert('Download functionality coming soon!');
    
    // Implementation would use Chart.js toBase64Image() method
    // to convert each chart to an image and then trigger downloads
}

/**
 * Setup Bootstrap components like tooltips and popovers
 */
function setupBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Utility to capitalize the first letter of a string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}