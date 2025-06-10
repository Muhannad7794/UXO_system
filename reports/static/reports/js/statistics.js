document.addEventListener('DOMContentLoaded', function () {
    // --- DOM Element References ---
    const statsForm = document.getElementById('stats-form');
    const analysisTypeSelect = document.getElementById('analysis-type-select');
    const paramContainers = document.querySelectorAll('.analysis-params');
    const resultsContainer = document.getElementById('report-results');
    const resultsTitle = document.getElementById('results-title');
    const resultsContent = document.getElementById('results-content');
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const chartContainer = document.getElementById('chart-container');
    const tableContainer = document.getElementById('table-container');
    const summaryContainer = document.getElementById('stats-summary-container');
    const chartCanvas = document.getElementById('stats-chart');
    let myChart;

    // --- UI LOGIC: Toggles which parameter fields are visible ---
    function toggleFormFields() {
        const selectedType = analysisTypeSelect.value;
        paramContainers.forEach(container => {
            container.style.display = 'none';
        });
        
        // This correctly finds the right container to show, including for regression
        const activeContainerId = (selectedType === 'regression' || selectedType === 'bivariate') ? 'bivariate-params' : `${selectedType}-params`;
        const activeContainer = document.getElementById(activeContainerId);
        if (activeContainer) {
            activeContainer.style.display = 'flex';
        }
    }

    // --- RENDERING LOGIC ---

    function renderChart(chartType, data) {
        if (myChart) myChart.destroy();
        chartContainer.style.display = 'block';
        let chartData = {};
        let options = {};
        const colors = ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#E7E9ED', '#8D6E63'];

        switch (data.analysis_type) {
            case 'grouped':
                options = { indexAxis: 'y', scales: { x: { beginAtZero: true } }, plugins: { legend: { display: false } } };
                chartData = {
                    labels: data.results.map(item => item.group),
                    datasets: [{
                        label: 'Value',
                        data: data.results.map(item => item.value),
                        backgroundColor: colors,
                    }]
                };
                break;
            case 'bivariate':
            case 'regression':
                options = { plugins: { legend: { display: data.analysis_type === 'regression' } } };
                const scatterData = (data.analysis_type === 'regression') ? data.scatter_data : data.results.map(p => ({x: p[0], y: p[1]}));
                chartData = {
                    datasets: [{
                        type: 'scatter', label: `${data.parameters.y_field} vs ${data.parameters.x_field}`,
                        data: scatterData, backgroundColor: 'rgba(0, 123, 255, 0.6)'
                    }]
                };
                if (data.analysis_type === 'regression') {
                    const { slope, intercept } = data.statistics;
                    const xValues = scatterData.map(p => p[data.parameters.x_field]);
                    const xMin = Math.min(...xValues);
                    const xMax = Math.max(...xValues);
                    chartData.datasets.push({
                        type: 'line', label: 'Regression Line',
                        data: [{x: xMin, y: slope * xMin + intercept}, {x: xMax, y: slope * xMax + intercept}],
                        borderColor: '#F44336', fill: false, tension: 0.1
                    });
                }
                break;
            case 'kmeans':
                const k = parseInt(data.parameters.k);
                const featureNames = data.parameters.features.split(',');
                options = { plugins: { legend: { position: 'bottom' } }, parsing: { xAxisKey: featureNames[0], yAxisKey: featureNames[1] || featureNames[0] } };
                chartData = { datasets: [] };
                for (let i = 0; i < k; i++) {
                    chartData.datasets.push({
                        type: 'scatter', label: `Cluster ${i}`,
                        data: data.results.filter(p => p.cluster === i),
                        backgroundColor: colors[i % colors.length]
                    });
                }
                break;
        }
        myChart = new Chart(chartCanvas, { type: chartType, data: chartData, options: options });
    }
    
    function renderTable(data) {
        if (!data.results || data.results.length === 0) { tableContainer.innerHTML = ''; return; }
        const dataForTable = data.results || data.scatter_data;
        if (!dataForTable || dataForTable.length === 0) { tableContainer.innerHTML = ''; return; }

        let headers = Object.keys(dataForTable[0]);
        let tableHTML = '<table class="table table-sm table-striped table-bordered">';
        tableHTML += `<thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>`;
        dataForTable.forEach(item => {
            let rowData = Object.values(item).map(v => typeof v === 'number' ? v.toFixed(4) : v);
            tableHTML += `<tr>${rowData.map(d => `<td>${d}</td>`).join('')}</tr>`;
        });
        tableHTML += '</tbody></table>';
        tableContainer.innerHTML = tableHTML;
    }

    function renderSummary(data) {
        summaryContainer.innerHTML = '';
        if (data.analysis_type === 'regression' && data.statistics) {
            const stats = data.statistics;
            summaryContainer.innerHTML = `<h5>Regression Statistics</h5><ul class="list-group">
                <li class="list-group-item d-flex justify-content-between align-items-center">R-squared: <strong>${stats.r_squared.toFixed(4)}</strong></li>
                <li class="list-group-item d-flex justify-content-between align-items-center">Slope: <strong>${stats.slope.toFixed(4)}</strong></li>
                <li class="list-group-item d-flex justify-content-between align-items-center">Intercept: <strong>${stats.intercept.toFixed(4)}</strong></li>
            </ul>`;
        }
    }

    // --- MAIN EVENT LISTENER FOR FORM SUBMISSION ---
    statsForm.addEventListener('submit', function (e) {
        e.preventDefault();
        resultsContainer.style.visibility = 'visible';
        resultsPlaceholder.style.display = 'none';
        resultsContent.style.display = 'none';
        tableContainer.innerHTML = '<h6><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div> Loading Report...</h6>';
        summaryContainer.innerHTML = '';
        if (myChart) myChart.destroy();

        const selectedAnalysis = analysisTypeSelect.value;
        let params = new URLSearchParams({ analysis_type: selectedAnalysis });

        // This corrected logic only gets parameters from the VISIBLE form section
        const activeParamsDiv = document.querySelector('.analysis-params:not([style*="display: none"])');
        if (activeParamsDiv) {
            activeParamsDiv.querySelectorAll('input, select').forEach(input => {
                if (input.name && input.value) {
                    if (input.type === 'select-multiple') {
                        for (const option of input.selectedOptions) { params.append(input.name, option.value); }
                    } else {
                        params.append(input.name, input.value);
                    }
                }
            });
        }
        
        if (selectedAnalysis === 'grouped' && params.get('aggregate_op') !== 'count') {
            params.append('aggregate_field', 'danger_score');
        }

        const apiUrl = `/api/v1/reports/statistics/?${params.toString()}`;
        
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    tableContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    chartContainer.style.display = 'none';
                    return;
                }
                
                resultsContent.style.display = 'flex';
                // FIX: Corrected how the title is generated
                resultsTitle.innerText = `Results for: ${selectedAnalysis.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Analysis`;
                
                let chartType = document.getElementById('chart-type').value;
                if (['bivariate', 'regression', 'kmeans'].includes(data.analysis_type)) { chartType = 'scatter'; }

                renderChart(chartType, data);
                renderTable(data);
                renderSummary(data);
            })
            .catch(error => {
                tableContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error}</div>`;
            });
    });

    // --- Initial page setup ---
    analysisTypeSelect.addEventListener('change', toggleFormFields);
    toggleFormFields();
});