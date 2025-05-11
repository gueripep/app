// Function to fetch search results from FastAPI
async function fetchSearchResults(query) {
    const response = await fetch(`http://localhost:8000/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query })
    });
    const data = await response.json();
    return data;
}

document.getElementById('search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('search-btn').click();
    }
});

document.getElementById('search-btn').addEventListener('click', async () => {
    const query = document.getElementById('search-input').value;
    if (!query) return;

    const results = await fetchSearchResults(query);

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';  // Clear previous results

    results.hits.forEach(result => {
        const template = document.getElementById('result-template');
        const clone = template.content.cloneNode(true);

        // Fill in the template with the result data
        const name = clone.querySelector('.name');
        name.innerHTML = result._formatted.filename;

        const content = clone.querySelector('.content');
        content.innerHTML = result._formatted.text;

        // Add the onclick event
        clone.querySelector('.pdf-result').onclick = () => showPDF(result.filename);

        // Append the cloned and populated template to the results container
        resultsDiv.appendChild(clone);
    });
});


// Function to show PDF preview
function showPDF(filename) {
    window.open(`http://localhost:8000/${filename}`, '_blank');
}