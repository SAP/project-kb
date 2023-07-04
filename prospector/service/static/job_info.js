
function getJobIdFromQueryString() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('jobId');
}

function JobInfoPage() {
    jobId = getJobIdFromQueryString()
    fetch(`/jobs/${jobId}`, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const jobData = data.job_data;
            document.getElementById('job-id').textContent = jobData.job_id;
            document.getElementById('job-params').textContent = jobData.job_params;
            document.getElementById('job-enqueued').textContent = jobData.job_enqueued_at;
            document.getElementById('job-started').textContent = jobData.job_started_at;
            document.getElementById('job-finished').textContent = jobData.job_finished_at;
            document.getElementById('job-result').textContent = jobData.job_results;
            document.getElementById('job-created-by').textContent = jobData.job_created_by;
            document.getElementById('job-created-from').textContent = jobData.job_created_from;
            document.getElementById('job-status').textContent = jobData.job_status;
        })
        .catch(error => {
            console.log('Error:', error);
        });
}
