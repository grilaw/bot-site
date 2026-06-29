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
    const votesString = JSON.stringify(data.votes || data);
    if (votesString === lastPollData) return;
    lastPollData = votesString;

    let votes = data.votes;

    const votesObj = {};
    if (Array.isArray(votes)) {
        votes.forEach(item => {
            votesObj[item.song_id || item.songId] = item.count || item.votes;
        });
    } else {
        Object.assign(votesObj, votes);
    }
    votes = votesObj;
    
    const totalVotes = Object.values(votes).reduce((a, b) => a + b, 0);
    
    if (totalVotes === 0) return;
    
    // Получаем все элементы .song
    const songElements = document.querySelectorAll('.song');
    
    // Создаем массив промисов для анимаций
    const animations = Array.from(songElements).map(async (element) => {
        const songId = element.dataset.songId;
        const songVotes = votes[songId] || 0;
        const percent = (songVotes / totalVotes) * 100;
        await animateFill(element, percent);
    });

    await Promise.all(animations);
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
            
            // Меняем ширину псевдоэлемента
            element.style.setProperty('--fill-width', currentPercent + '%');
            element.style.setProperty('--target-width', targetPercent + '%');
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.style.setProperty('--fill-width', targetPercent + '%');
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
            console.log('Vote response:', data);
            
            if (response.ok) {
                await pollApply(data);
            } else if (data.status === 409) {
                alert(data.message);
            }
        } catch (error) {
            console.error('Ошибка', error);
        }
    });
});


async function voteUpdate() {
    try {
        const response = await fetch('/api/getvotes');
        if (response.ok) {
            const data = await response.json();
            await pollApply(data)
        }
        
    }
    catch (error) {
        console.error(error)
    }
};

setInterval(voteUpdate, 5000);

voteUpdate();