// Scope selector logic
document.getElementById('scope').addEventListener('change', function(e) {
    const scope = e.target.value;
    document.getElementById('stateGroup').style.display = scope === 'state' ? 'flex' : 'none';
    document.getElementById('cityGroup').style.display = scope === 'city' ? 'flex' : 'none';
});

// Form submission
document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const scope = document.getElementById('scope').value;
    const state = document.getElementById('state').value || '';
    const city = document.getElementById('city').value || '';
    const courses = document.getElementById('courses').value;
    const max_colleges = document.getElementById('maxColleges').value;
    const delay = document.getElementById('delay').value;

    // Show status
    document.getElementById('status').style.display = 'block';
    document.getElementById('statusText').textContent = 'Scraping colleges... This may take a few minutes.';
    document.getElementById('resultsPanel').style.display = 'none';
    document.getElementById('errorPanel').style.display = 'none';

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scope,
                city,
                state,
                courses,
                max_colleges,
                delay
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || 'Scraping failed');
        }

        // Store data for download
        window.resultsData = data.data;
        window.resultsJSON = data.json;

        // Display results
        displayResults(data.data);
        document.getElementById('status').style.display = 'none';

    } catch (error) {
        document.getElementById('status').style.display = 'none';
        document.getElementById('errorPanel').style.display = 'block';
        document.getElementById('errorText').textContent = '❌ Error: ' + error.message;
    }
});

// Display results in table
function displayResults(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    data.forEach(college => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${college['College Name'] || '—'}</strong></td>
            <td>${college['City'] || '—'}</td>
            <td>${college['Phone Numbers'] || '—'}</td>
            <td>${college['Emails'] || '—'}</td>
            <td><a href="${college['Official Website'] || '#'}" target="_blank">${college['Official Website'] ? '🔗 Link' : '—'}</a></td>
        `;
        tbody.appendChild(row);
    });

    document.getElementById('resultCount').textContent = data.length;
    document.getElementById('resultsPanel').style.display = 'block';
}

// Download CSV
async function downloadCSV() {
    if (!window.resultsData) return;

    const csv = convertToCSV(window.resultsData);
    downloadFile(csv, 'colleges.csv', 'text/csv');
}

// Download JSON
function downloadJSON() {
    if (!window.resultsJSON) return;

    const json = JSON.stringify(window.resultsJSON, null, 2);
    downloadFile(json, 'colleges.json', 'application/json');
}

// Helper to convert array to CSV
function convertToCSV(data) {
    if (data.length === 0) return '';

    const headers = Object.keys(data[0]);
    const csv = [headers.join(',')];

    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            // Escape quotes and wrap in quotes if contains comma
            return typeof value === 'string' && value.includes(',') 
                ? `"${value.replace(/"/g, '""')}"` 
                : value;
        });
        csv.push(values.join(','));
    });

    return csv.join('\n');
}

// Helper to download file
function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
