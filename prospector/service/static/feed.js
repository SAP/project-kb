// Function to call the /process_vulns API
async function processVulns() {
    fetch('/feeds/process_vulns', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(JSON.stringify(data));
        })
        .catch(error => {
            console.error(error);
        });
}

// Function to call the /create_jobs API
async function createJobs() {
    await fetch('/feeds/create_jobs', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(JSON.stringify(data));
        })
        .catch(error => {
            console.error(error);
        });
}


// Function to call the /create_jobs API
async function fetchVulns() {
    const timeRange = document.getElementById("time_range").value;

    fetch('/feeds/fetch_vulns/' + timeRange, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            fetchVulnData()
        })
        .catch(error => {
            console.error(error);
        });
}



// Function to update the job table with new data
async function updatefeedTable(vulnList) {
    const tableBody = $('#vuln-table tbody');
    tableBody.empty();

    for (const vuln of vulnList) {
        const row = $('<tr>').addClass('highlight');

        const vulnIdCell = $('<td>').text(vuln.vuln_id);
        row.append(vulnIdCell);
        const pubDateCell = $('<td>').text(vuln.published_date);
        row.append(pubDateCell);
        const modDateCell = $('<td>').text(vuln.last_modified_date);
        row.append(modDateCell);
        const sourceCell = $('<td>').text(vuln.source);
        row.append(sourceCell);

        tableBody.append(row);
    }
}

// Function to fetch job data from the /jobs endpoint and update the table
async function fetchVulnData() {
    fetch('/feeds')
        .then(response => response.json())
        .then(data => {
            updatefeedTable(data);
        })
        .catch(error => {
            console.error(error);
        });
}
