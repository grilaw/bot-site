document.getElementById('startvote-btn').addEventListener('submit', async function(e) {
    e.preventDefault();
    const response = await fetch('/api/startvote', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

    const data = await response.json(); // Парсим JSON ответ
    
    console.log(data);
    location.reload(); 
})