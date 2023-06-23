// Function to update the job table with new data
async function updateJobTable(jobList) {
    const tableBody = $('#job-table tbody');
    tableBody.empty();

    for (const job of jobList) {
        const row = $('<tr>').addClass('highlight');

        const statusBadge = $('<td>').html(`<span class="badge ${{
            'finished': 'badge-success',
            'started': 'badge-info',
            'failed': 'badge-danger',
        }[job.status || ''] || 'badge-dark'}">${job.status}</span>`);
        row.append(statusBadge);

        const jobIdCell = $('<td>').text(job._id);
        row.append(jobIdCell);

        const resultCell = $('<td>');
        const resultLink = $('<a>').attr('href', `/jobs/${job._id}`).text('Result');
        resultCell.append(resultLink);
        row.append(resultCell);

        const settingsCell = $('<td>');
        const configureBtn = $('<button>')
            .addClass('btn btn-sm btn-primary configure-btn')
            .text('Configure')
            .attr('onclick', `configureJob('${job._id}')`);
        settingsCell.append(configureBtn);
        row.append(settingsCell);

        tableBody.append(row);
    }
}

// Function to fetch job data from the /jobs endpoint and update the table
async function fetchJobData() {
    fetch('/jobs')
        .then(response => response.json())
        .then(data => {
            updateJobTable(data);
        })
        .catch(error => {
            console.error(error);
            // Handle the error as needed
        });
}

// Function to handle the "Configure" button click
function configureJob(jobId) {
    // Redirect to the configure page with the job ID in the query string
    window.location.href = `job_configuration.html?jobId=${jobId}`;
}

// Call fetchJobData initially to populate the table
fetchJobData();

// Call fetchJobData every 4 seconds to update the table
setInterval(fetchJobData, 1000);
