
function callEnqueue(cve) {
    const repo = document.getElementById("repo").value;
    const versions = document.getElementById("versions").value;

    url = "/jobs/enqueue/?cve=" + cve + "&repo=" + repo + "&version=" + versions

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            window.location.href = '/home';
        })
        .catch(error => console.error(error));

}
