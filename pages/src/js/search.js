const tracks = [
    {
        id: 1,
        title: 'Bohemian Rhapsody',
        author: 'Queen',
        album: 'A Night at the Opera',
        duration: 354,
        artwork: 'https://example.com/cover/bohemian100x100.jpg',
        explicit: false
    },
    {
        id: 2,
        title: 'Stairway to Heaven',
        author: 'Led Zeppelin',
        album: 'Led Zeppelin IV',
        duration: 482,
        artwork: 'https://example.com/cover/stairway100x100.jpg',
        explicit: false
    },
    {
        id: 3,
        title: 'Smells Like Teen Spirit',
        author: 'Nirvana',
        album: 'Nevermind',
        duration: 301,
        artwork: 'static/browser/img/logo.jpg',
        explicit: true
    },
    {
        id: 4,
        title: 'Hotel California',
        author: 'Eagles',
        album: 'Hotel California',
        duration: 391,
        artwork: 'https://example.com/cover/hotel100x100.jpg',
        explicit: false
    },
    {
        id: 5,
        title: 'Imagine',
        author: 'John Lennon',
        album: 'Imagine',
        duration: 183,
        artwork: 'https://example.com/cover/imagine100x100.jpg',
        explicit: false
    },
    {
        id: 6,
        title: 'Like a Rolling Stone',
        author: 'Bob Dylan',
        album: 'Highway 61 Revisited',
        duration: 373,
        artwork: 'static/browser/img/logo.jpg',
        explicit: false
    },
    {
        id: 7,
        title: 'Wonderwall',
        author: 'Oasis',
        album: '(What\'s the Story) Morning Glory?',
        duration: 258,
        artwork: 'https://example.com/cover/wonderwall100x100.jpg',
        explicit: false
    },
    {
        id: 8,
        title: 'Billie Jean',
        author: 'Michael Jackson',
        album: 'Thriller',
        duration: 294,
        artwork: 'https://example.com/cover/billie100x100.jpg',
        explicit: false
    },
    {
        id: 9,
        title: 'Purple Haze',
        author: 'Jimi Hendrix',
        album: 'Are You Experienced?',
        duration: 172,
        artwork: 'static/browser/img/logo.jpg',
        explicit: false
    },
    {
        id: 10,
        title: 'Lose Yourself',
        author: 'Eminem',
        album: '8 Mile Soundtrack',
        duration: 326,
        artwork: 'https://example.com/cover/lose100x100.jpg',
        explicit: true
    }
];

document.querySelectorAll('#poll > *').forEach(el => {
    el.addEventListener('click', () => {
        document.querySelectorAll('#poll > *').forEach(e => {
            e.classList.add('voted')
        })
    })
})

let angle = 0
async function rotate() {
    angle += 1; // Увеличиваем угол на 1 градус
    document.querySelector('.vinyl-back').style.transform = `rotate(${angle}deg)`;
    await requestAnimationFrame(rotate); // Плавная анимация
};

let clockArrow = 0;
let lastTime = 0;
function tick(timestamp) {
    if (timestamp - lastTime >= 1000) {
        clockArrow += 1;
        const angle = clockArrow * 6;
        const clock = document.querySelector('#dec-clock');
        
        if (clock) {
            clock.style.transform = `rotate(${angle}deg)`;
            clock.style.transformOrigin = 'center center';
        }
        
        lastTime = timestamp;
    }
    requestAnimationFrame(tick);
}

requestAnimationFrame(tick);

function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    
    const seconds = totalSeconds % 60;

    const paddedMinutes = String(minutes).padStart(2, '0');
    const paddedSeconds = String(seconds).padStart(2, '0');

    return `${paddedMinutes}:${paddedSeconds}`;
}

const searchResults = document.querySelector('.search-results')
const searchBox = document.querySelector('#search-box')

function resultRender(songList) {
    if (!searchResults) return;
    if (songList.length === 0) {
        searchResults.innerHTML = `
        <p class="text-white">Ничего не найдено</p>
        `;
        return
    };
    searchResults.innerHTML = songList.map(song => `
            <div class="poll-button rounded-xl hover:bg-white/5">

                <div class="grid grid-cols-[1fr_80px] items-center gap-4 px-2 py-2 sm:grid-cols-[1fr_1fr_1fr]">
                    <div class="flex min-w-0 items-center">
                    <div class="hidden mx-3 h-16 w-16 shrink-0 rounded-md bg-linear-60 from-amber-400 to-amber-500 sm:block"></div>
                    <div class="min-w-0">
                        <p class="truncate text-base font-medium text-white">${song.title}</p>
                        <p class="truncate text-sm text-white/60">${song.author}</p>
                    </div>
                    </div>

                    <div class="hidden justify-self-center flex-col w-full truncate text-center text-sm text-white/60 sm:flex">
                        <p class="mask-[linear-gradient(to_right,black_90%,transparent_100%)]">${song.album}</p>
                        <p class="mask-[linear-gradient(to_right,black_90%,transparent_100%)]">${song.author}</p>
                    </div>

                    <div class="flex items-center justify-end px-3">
                    <p class="mx-3 text-right text-sm text-white/60">${formatTime(song.duration)}</p>
                    <i class="bi bi-plus cursor-pointer rounded-md bg-linear-to-br from-blue-500 to-blue-400 text-4xl text-white"></i>
                    </div>

                </div>
            </div>
            `).join('<div class="mx-auto h-px w-[95%] bg-white/10"></div>');
};

function songSearch() {
    const q = searchBox.value.trim().toLowerCase();
    let songs;
    if (!q) {
        songs = tracks.slice(0,4);
    }
    else {
        songs = tracks.filter(s=>(s.title+' '+s.author+' ').toLowerCase().includes(q)).slice(0,4);
    };
    resultRender(songs);
}

searchBox.addEventListener('focus', (event) => {
    searchResults.classList.add('active');
    songSearch();
});
searchBox.addEventListener('blur', (event) => {
    searchResults.classList.remove('active');
});
searchBox.addEventListener('input', (event) => {
    songSearch(searchBox)
});

rotate();
tick(0);