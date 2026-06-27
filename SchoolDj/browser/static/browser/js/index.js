const searchForm = document.querySelector('.search-form');
const searchInput = document.querySelector('.search-input');

searchForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const query = searchInput.value.trim();
    
    if (query) {
        window.location.href = `/search/${encodeURIComponent(query)}`;
    } else {
        searchInput.classList.add('empty-textbox');
        searchInput.placeholder = 'Поле не может быть пустым';
        setTimeout(() => {
            searchInput.placeholder = 'Введите трек';
            searchInput.classList.remove('empty-textbox');
        }, 2000);
    }
});