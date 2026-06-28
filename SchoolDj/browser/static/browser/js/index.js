// 1. Сначала считываем токен (пример функции для чтения из cookie)
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

const csrfToken = getCookie('csrftoken'); 

let lastPollData = ''

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

async function pollApply(data) {
    if (data === lastPollData) return;
    lastPollData = data;

    console.log('pollApply received:', data); // Проверяем что пришло


    // data = { status: 201, votes: { "1": 5, "2": 3, "3": 7 } }
    let votes = data.votes; // Получаем объект с голосами

    const votesObj = {};
    if (Array.isArray(votes)) {
        votes.forEach(item => {
            votesObj[item.song_id || item.songId] = item.count || item.votes;
        });
    } else {
        Object.assign(votesObj, votes);
    }
    votes = votesObj;
    console.log('Converted array to object:', votes);
    
    // Суммируем голоса
    const totalVotes = Object.values(votes).reduce((a, b) => a + b, 0);
    console.log('totalVotes:', totalVotes);
    
    if (totalVotes === 0) return;
    
    // Получаем все элементы .song
    const songElements = document.querySelectorAll('.song');
    console.log('songElements found:', songElements.length);
    
    // Создаем массив промисов для анимаций
    const animations = Array.from(songElements).map(async (element) => {
        const songId = element.dataset.songId;
        const songVotes = votes[songId] || 0;
        const percent = (songVotes / totalVotes) * 100;
        console.log(`Song ${songId}: ${songVotes} votes, ${percent}%`);
        await animateFill(element, percent);
    });

    await Promise.all(animations);
    console.log('All animations completed');
}

async function animateFill(element, targetPercent, duration = 1000) {
    return new Promise((resolve) => {
        const startTime = performance.now();
        const maxLog = Math.log(100);
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const logProgress = Math.log(1 + progress * 99) / maxLog;
            const currentPercent = targetPercent * logProgress;
            
            // Принудительно устанавливаем фон с !important через style
            const bg = `linear-gradient(to right, #017eac ${currentPercent}%, #2b2b2b ${currentPercent}%)`;
            element.style.setProperty('background', bg, 'important');
            // ИЛИ:
            // element.style.background = bg;
            
            console.log(`Progress: ${Math.round(currentPercent)}%`); // Для отладки
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                // Фиксируем финальное значение
                element.style.setProperty('background', 
                    `linear-gradient(to right, #017eac ${targetPercent}%, #2b2b2b ${targetPercent}%)`, 
                    'important'
                );
                resolve();
            }
        }
        
        requestAnimationFrame(update);
    });
}

// В обработчике клика:
document.querySelectorAll('.song').forEach(el => {
    el.addEventListener('click', async function() {
        const songId = this.dataset.songId;
        try {
            const response = await fetch('/api/vote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({songId: songId})
            });
            
            const data = await response.json();
            console.log('Vote response:', data); // Проверяем ответ
            
            if (data.status === 201) { // У вас status 201, а не 200!
                await pollApply(data);
            } else if (data.status === 409) {
                alert(data.message); // Пользователь уже голосовал
            }
        } catch (error) {
            console.error('Ошибка', error);
        }
    });
});


async function voteUpdate() {
    try {
        const response = await fetch('/api/getvotes');
        const data = await response.json();
        const votesString = JSON.stringify(data.votes || data);
        if (data.status === 200) {
            await pollApply(data)
        }
        
    }
    catch (error) {
        console.error(error)
    }
};

setInterval(voteUpdate, 5000);

voteUpdate();