document.addEventListener('DOMContentLoaded', function() {
    const statsForm = document.getElementById('stats-form');
    const analysisTypeSelect = document.getElementById('analysis-type-select');
    const paramContainers = document.querySelectorAll('.analysis-params');
    const resultsContainer = document.getElementById('report-results');
    const resultsTitle = document.getElementById('results-title');
    const resultsContent = document.getElementById('results-content');
    const chartContainer = document.getElementById('chart-container');
    const tableContainer = document.getElementById('table-container');
    const summaryContainer = document.getElementById('stats-summary-container');
    const chartCanvas = document.getElementById('stats-chart');
    let myChart;

    const aggregateOpSelect = document.getElementById('aggregate_op_select');
    const aggregateFieldContainer = document.getElementById('aggregate-field-container');

    function toggleAggregateField() {
        if (aggregateOpSelect && aggregateFieldContainer) {
            const show = aggregateOpSelect.value !== 'count';
            aggregateFieldContainer.style.display = show ? 'block' : 'none';
        }
    }

    function toggleFormFields() {
        const selectedType = analysisTypeSelect.value;
        paramContainers.forEach(container => {
            container.style.display = 'none';
        });
        const activeContainerId = (selectedType === 'regression' || selectedType === 'bivariate') ? 'bivariate-params' : `${selectedType}-params`;
        const activeContainer = document.getElementById(activeContainerId);
        if (activeContainer) {
            activeContainer.style.display = 'flex';
        }
        if (selectedType === 'grouped') {
            toggleAggregateField();
        }
    }

    function renderChart(chartType, data) {
        if (myChart) myChart.destroy();
        chartContainer.style.display = 'block';
        let chartData = {};
        let options = {};
        const colors = ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
        const labelMaps = data.label_maps || {};

        switch (data.analysis_type) {
            case 'grouped':
                {
                    const groupMap = labelMaps.group || {};
                    const labels = data.results.map(item => groupMap[item.group] || item.group);
                    options = {
                        indexAxis: 'y',
                        scales: {
                            x: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    };
                    chartData = {
                        labels: labels,
                        datasets: [{
                            label: 'Value',
                            data: data.results.map(item => item.value),
                            backgroundColor: colors
                        }]
                    };
                    break;
                }
            case 'bivariate':
            case 'regression':
                {
                    const xMap = labelMaps.x_axis || {};
                    const yMap = labelMaps.y_axis || {};
                    options = {
                        plugins: {
                            legend: {
                                display: data.analysis_type === 'regression'
                            }
                        },
                        scales: {
                            x: {
                                ticks: {
                                    callback: (value) => xMap[value.toFixed(4)] || xMap[value.toFixed(2)] || xMap[value] || value
                                }
                            },
                            y: {
                                ticks: {
                                    callback: (value) => yMap[value.toFixed(4)] || yMap[value.toFixed(2)] || yMap[value] || value
                                }
                            }
                        }
                    };
                    const scatterData = (data.analysis_type === 'regression') ? data.scatter_data : data.results.map(p => ({
                        x: p[0],
                        y: p[1]
                    }));
                    chartData = {
                        datasets: [{
                            type: 'scatter',
                            label: `${data.parameters.y_field} vs ${data.parameters.x_field}`,
                            data: scatterData,
                            backgroundColor: 'rgba(0, 123, 255, 0.6)'
                        }]
                    };
                    if (data.analysis_type === 'regression') {
                        const {
                            slope,
                            intercept
                        } = data.statistics;
                        const xValues = scatterData.map(p => p[data.parameters.x_field]);
                        const xMin = Math.min(...xValues);
                        const xMax = Math.max(...xValues);
                        chartData.datasets.push({
                            type: 'line',
                            label: 'Regression Line',
                            data: [{
                                x: xMin,
                                y: slope * xMin + intercept
                            }, {
                                x: xMax,
                                y: slope * xMax + intercept
                            }],
                            borderColor: '#F44336',
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0
                        });
                    }
                    break;
                }
            case 'kmeans':
                {
                    const k = parseInt(data.parameters.k);
                    const featureNames = data.parameters.features.split(',');
                    options = {
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        },
                        parsing: {
                            xAxisKey: featureNames[0],
                            yAxisKey: featureNames[1] || featureNames[0]
                        }
                    };
                    chartData = {
                        datasets: []
                    };
                    for (let i = 0; i < k; i++) {
                        chartData.datasets.push({
                            type: 'scatter',
                            label: `Cluster ${i}`,
                            data: data.results.filter(p => p.cluster === i),
                            backgroundColor: colors[i % colors.length]
                        });
                    }
                    break;
                }
        }
        myChart = new Chart(chartCanvas, {
            type: chartType,
            data: chartData,
            options: options
        });
    }

    function renderTable(data) {
        let dataForTable = data.results || data.scatter_data;
        if (!dataForTable || dataForTable.length === 0) {
            tableContainer.innerHTML = '';
            return;
        }

        // --- FIX FOR BIVARIATE TABLE ---
        // If the data is bivariate, transform its array-of-arrays format into an
        // array-of-objects to match the regression data structure.
        if (data.analysis_type === 'bivariate' && Array.isArray(dataForTable[0])) {
            const x_field = data.parameters.x_field;
            const y_field = data.parameters.y_field;
            dataForTable = dataForTable.map(row => ({
                [x_field]: row[0],
                [y_field]: row[1]
            }));
        }
        // --- END BIVARIATE FIX ---

        const labelMaps = data.label_maps || {};
        const groupMap = labelMaps.group || {};
        const xMap = labelMaps.x_axis || {};
        const yMap = labelMaps.y_axis || {};
        let headers = Object.keys(dataForTable[0]);
        let tableHTML = '<table class="table table-sm table-striped table-bordered">';
        tableHTML += `<thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>`;

        dataForTable.forEach(item => {
            let rowData = headers.map(header => {
                const rawValue = item[header];
                let displayValue = rawValue;

                // --- FIX FOR VALUE '1' and ALL TRANSLATIONS ---
                // This logic now robustly translates all applicable values.
                if (header === 'group') {
                    displayValue = groupMap[rawValue] || rawValue;
                } else if (header === data.parameters.x_field && typeof rawValue === 'number') {
                    // Use a robust lookup that checks for different float/integer string representations
                    displayValue = xMap[rawValue.toFixed(1)] || xMap[String(rawValue)] || xMap[rawValue] || rawValue;
                } else if (header === data.parameters.y_field && typeof rawValue === 'number') {
                    displayValue = yMap[rawValue.toFixed(1)] || yMap[String(rawValue)] || yMap[rawValue] || rawValue;
                } else if (typeof rawValue === 'number') {
                    // Format any remaining numbers (like danger_score or regression stats)
                    displayValue = rawValue.toFixed(4);
                }
                // --- END TRANSLATION FIX ---

                return `<td>${displayValue}</td>`;
            });
            tableHTML += `<tr>${rowData.join('')}</tr>`;
        });

        tableHTML += '</tbody></table>';
        tableContainer.innerHTML = tableHTML;
}

    function renderSummary(data) {
        summaryContainer.innerHTML = "";
        if (data.analysis_type === "regression" && data.statistics) {
            const stats = data.statistics;
            summaryContainer.innerHTML = `<h5>Regression Statistics</h5><ul class="list-group"><li class="list-group-item d-flex justify-content-between align-items-center">R-squared: <strong>${stats.r_squared.toFixed(4)}</strong></li><li class="list-group-item d-flex justify-content-between align-items-center">Slope: <strong>${stats.slope.toFixed(4)}</strong></li><li class="list-group-item d-flex justify-content-between align-items-center">Intercept: <strong>${stats.intercept.toFixed(4)}</strong></li></ul>`;
        }
    }

    statsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        resultsContainer.style.visibility = 'visible';
        resultsContent.style.display = 'none';
        tableContainer.innerHTML = '<h6><div class="spinner-border spinner-border-sm" role="status"></div> Loading Report...</h6>';
        summaryContainer.innerHTML = '';
        if (myChart) myChart.destroy();

        const params = new URLSearchParams(new FormData(statsForm));
        const apiUrl = `/api/v1/reports/statistics/?${params.toString()}`;

        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    tableContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    return;
                }
                resultsContent.style.display = 'flex';
                const selectedAnalysis = data.parameters.analysis_type;
                resultsTitle.innerText = `Results for: ${selectedAnalysis.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Analysis`;

                let chartType = document.getElementById('chart-type') ? document.getElementById('chart-type').value : 'bar';
                if (['bivariate', 'regression', 'kmeans'].includes(data.analysis_type)) {
                    chartType = 'scatter';
                }

                renderChart(chartType, data);
                renderTable(data);
                renderSummary(data);
            })
            .catch(error => {
                tableContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error}</div>`;
            });
    });

    if (analysisTypeSelect) {
        analysisTypeSelect.addEventListener('change', toggleFormFields);
    }
    if (aggregateOpSelect) {
        aggregateOpSelect.addEventListener('change', toggleAggregateField);
    }
    toggleFormFields();
});