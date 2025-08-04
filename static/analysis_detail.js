// analysis_detail.js
// Clean JavaScript for analysis detail page

function initializeAnalysisDetail(defectsData, analysisData) {
    if (defectsData && defectsData.length > 0) {
        // Create summary statistics
        const summary = {};
        defectsData.forEach(defect => {
            summary[defect.type] = (summary[defect.type] || 0) + 1;
        });
        
        // Populate summary div
        populateSummary(summary, defectsData.length);
        
        // Create chart
        createDefectChart(summary);
    }
}

function populateSummary(summary, totalDefects) {
    const summaryDiv = document.getElementById('defectSummary');
    if (summaryDiv) {
        let summaryHTML = '';
        
        Object.entries(summary).forEach(([type, count]) => {
            const percentage = ((count / totalDefects) * 100).toFixed(1);
            summaryHTML += `
                <div class="d-flex justify-content-between align-items-center mb-3 p-2 bg-light rounded">
                    <div>
                        <strong>${type}</strong>
                        <br>
                        <small class="text-muted">${percentage}% of total defects</small>
                    </div>
                    <span class="badge bg-primary fs-6">${count}</span>
                </div>
            `;
        });
        
        summaryDiv.innerHTML = summaryHTML;
    }
}

function createDefectChart(summary) {
    const ctx = document.getElementById('detailChart');
    if (ctx) {
        new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: Object.keys(summary),
                datasets: [{
                    data: Object.values(summary),
                    backgroundColor: [
                        '#dc3545', '#007bff', '#fd7e14', '#198754', 
                        '#6f42c1', '#ffc107', '#20c997'
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
}

function exportDetailedCSV(defectsData, analysisData) {
    const csvData = [
        ['Analysis ID', 'Filename', 'Defect #', 'Type', 'Severity', 'Confidence', 'Context']
    ];
    
    defectsData.forEach((defect, index) => {
        csvData.push([
            analysisData.analysisId || 'unknown',
            analysisData.filename || 'unknown',
            index + 1,
            defect.type,
            defect.severity,
            defect.confidence,
            defect.sentence.substring(0, 300)
        ]);
    });
    
    let csvContent = csvData.map(row => 
        row.map(field => '"' + String(field).replace(/"/g, '""') + '"').join(',')
    ).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `detailed_analysis_${analysisData.analysisId || 'unknown'}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function printAnalysis() {
    window.print();
}
