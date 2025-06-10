document.addEventListener('DOMContentLoaded', function () {
    const analysisTypeSelect = document.getElementById('analysis_type');
    const groupedFields = document.getElementById('grouped-fields');
    const aggregateFields = document.getElementById('aggregate-fields');
    const statsForm = document.getElementById('stats-form');
    const resultsTitle = document.getElementById('results-title');
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const chartContainer = document.getElementById('chart-container');
    const tableContainer = document.getElementById('table-container');
    const chartCanvas = document.getElementById('stats-chart');
    let myChart; // Variable to hold the chart instance

    // Function to toggle form fields based on analysis type
    function toggleFormFields() {
        if (analysisTypeSelect.value === 'grouped') {
            groupedFields.style.display = 'flex';
            aggregateFields.style.display = 'none';
        } else {
            groupedFields.style.display = 'none';
            aggregateFields.style.display = 'flex';
        }
    }

    // Function to render results as a chart
    function renderChart(data) {
        if (myChart) {
            myChart.destroy(); // Destroy previous chart instance
        }
        chartContainer.style.display = 'block';
        
        const labels = data.results.map(item => item.group);
        const values = data.results.map(item => item.value);
        
        myChart = new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: data.parameters.group_by || 'Result',
                    data: values,
                    backgroundColor: 'rgba(0, 123, 255, 0.5)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
    
    // Function to render results as a simple table
    function renderTable(data) {
        let tableHTML = '<table class="table table-striped table-bordered">';
        tableHTML += '<thead><tr><th>Group</th><th>Value</th></tr></thead>';
        tableHTML += '<tbody>';
        data.results.forEach(item => {
            tableHTML += `<tr><td>${item.group}</td><td>${item.value.toLocaleString()}</td></tr>`;
        });
        tableHTML += '</tbody></table>';
        tableContainer.innerHTML = tableHTML;
    }

    // Event listener for the form submission
    statsForm.addEventListener('submit', function (e) {
        e.preventDefault();
        resultsPlaceholder.style.display = 'none';
        tableContainer.innerHTML = '<h6>Loading...</h6>';


        const formData = new FormData(statsForm);
        // We need to add the 'aggregate_field' manually for some operations
        if (formData.get('analysis_type') === 'grouped' && formData.get('aggregate_op') !== 'count') {
            formData.append('aggregate_field', 'danger_score');
        }
        if (formData.get('analysis_type') === 'aggregate') {
            formData.append('numeric_field', 'danger_score');
        }

        const params = new URLSearchParams(formData);
        const apiUrl = `/api/v1/reports/statistics/?${params.toString()}`;
        
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    tableContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    chartContainer.style.display = 'none';
                    return;
                }
                
                resultsTitle.innerText = `Report Results: ${data.parameters.group_by || 'Overall ' + data.parameters.operation}`;
                
                if (data.analysis_type === 'grouped') {
                    renderChart(data);
                    renderTable(data);
                } else {
                    // Display single aggregate value
                    chartContainer.style.display = 'none';
                    tableContainer.innerHTML = `<div class="alert alert-info fs-4"><strong>Result:</strong> ${data.result.toLocaleString()}</div>`;
                }
            })
            .catch(error => {
                tableContainer.innerHTML = `<div class="alert alert-danger">An error occurred: ${error}</div>`;
            });
    });

    // Initial setup
    analysisTypeSelect.addEventListener('change', toggleFormFields);
    toggleFormFields(); // Call it once on page load
});