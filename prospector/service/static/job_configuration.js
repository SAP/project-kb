
// Function to retrieve the job ID from the query string
function getJobIdFromQueryString() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('jobId');
}

function populatePage() {
    jobId = getJobIdFromQueryString()
    fetch(`/jobs/${jobId}`, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const jobData = data.job_data;
            document.getElementById('job-id').textContent = jobData.job_id;
            document.getElementById('job-status').textContent = jobData.job_status
            const jobParams = jobData.job_params.slice(1, -1).split(',');
            document.getElementById('repo').value = jobParams[1];
            document.getElementById('versions').value = jobParams[2]
        })
        .catch(error => {
            console.log('Error:', error);
        });
}

// Function to enqueue the job
function callEnqueue() {
    jobId = getJobIdFromQueryString()
    const repoInput = document.getElementById('repo').value;
    const versionsInput = document.getElementById('versions').value;

    const requestBody = {
        repo: repoInput,
        version: versionsInput,
        created_from: jobId
    };

    console.log('Request Body:', requestBody);

    fetch(`/jobs/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
    })
        .then(response => {
            console.log('Job enqueued successfully');
        })
        .catch(error => {
            console.log('Error:', error);
        });
}
