// results.js - JavaScript for defect analysis results page

function initializeResultsPage(summaryData, defectsData, filename) {
    // Set current date
    const currentDate = new Date().toLocaleString();
    document.getElementById('currentDate').textContent = currentDate;
    
    // Create defect chart if we have summary data
    if (summaryData && Object.keys(summaryData).length > 0) {
        createDefectChart(summaryData);
    }
    
    // Store data for CSV export
    window.defectsData = defectsData;
    window.filename = filename;
}

function createDefectChart(summaryData) {
    const ctx = document.getElementById('defectChart');
    if (!ctx) return;
    
    const labels = Object.keys(summaryData);
    const data = Object.values(summaryData);
    
    new Chart(ctx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB', 
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF1744'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function exportToPDF() {
    alert('PDF export feature coming soon!');
}

function exportToCSV() {
    if (!window.defectsData || !window.filename) {
        alert('No data available for export');
        return;
    }
    
    const csvData = [
        ['Type', 'Keyword', 'Severity', 'Context']
    ];
    
    window.defectsData.forEach(defect => {
        csvData.push([
            defect.type,
            defect.keyword,
            defect.severity,
            defect.sentence.substring(0, 200) // Limit context length
        ]);
    });
    
    let csvContent = csvData.map(row => 
        row.map(field => '"' + String(field).replace(/"/g, '""') + '"').join(',')
    ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'defect_analysis_' + window.filename + '.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}
