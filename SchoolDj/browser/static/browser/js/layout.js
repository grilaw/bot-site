import { analyzeImageColor } from "https://cdn.jsdelivr.net/npm/get-some-pixel-colors@1.0.0/dist/index.js";

// Ключ для хранения кеша
const CACHE_KEY = 'image-colors-cache';

// Загрузка кеша из localStorage
function loadColorCache() {
    const cached = localStorage.getItem(CACHE_KEY);
    return cached ? JSON.parse(cached) : {};
}

// Сохранение кеша в localStorage
function saveColorCache(cache) {
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
}

// Функция для форматирования времени
function formatTimeStrings() {
    const timeStrings = document.querySelectorAll('.format-time');
    timeStrings.forEach(element => {
        const seconds = parseInt(element.innerHTML);
        const formatted = new Date(seconds * 1000).toISOString().substring(14, 19);
        element.innerHTML = formatted;
    });
}

// Асинхронная функция для обработки цветов с кешированием
async function processColors() {
    const coloredBackground = document.querySelectorAll('.colored-back');
    const colorCache = loadColorCache();
    let cacheUpdated = false;
    
    for (const container of coloredBackground) {
        const cover = container.querySelector('img');
        if (!cover) continue;
        
        const imageUrl = cover.src;
        
        // Проверяем кеш
        if (colorCache[imageUrl]) {
            const color = colorCache[imageUrl];
            container.style.background = `rgb(${color.r}, ${color.g}, ${color.b})`;
            continue;
        }
        
        // Ждём загрузки изображения
        await new Promise((resolve) => {
            if (cover.complete) {
                resolve();
            } else {
                cover.onload = resolve;
                cover.onerror = resolve;
            }
        });
        
        try {
            const color = await analyzeImageColor(cover, "dominant");
            container.style.background = `rgb(${color.r}, ${color.g}, ${color.b})`;
            
            // Сохраняем в кеш
            colorCache[imageUrl] = color;
            cacheUpdated = true;
        } catch (error) {
            console.error('Ошибка анализа цвета:', error);
            container.style.background = 'rgba(255, 255, 255, 0.1)';
        }
    }
    
    // Сохраняем кеш только если были изменения
    if (cacheUpdated) {
        saveColorCache(colorCache);
    }
}

// Функция для установки контрастного цвета с использованием data-атрибутов
function setContrastColor() {
    const paragraphs = document.querySelectorAll('.adaptive-text');
    
    paragraphs.forEach(paragraph => {
        const trackCard = paragraph.closest('.track-card');
        
        if (trackCard) {
            // Используем сохранённый цвет или вычисляем новый
            let cardBg = trackCard.style.background;
            
            if (!cardBg || cardBg === '') {
                cardBg = getComputedStyle(trackCard).backgroundColor;
            }
            
            const rgb = cardBg.match(/\d+/g);
            
            if (rgb) {
                const brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
                const textColor = brightness > 128 ? '#000000' : '#FFFFFF';
                paragraph.style.color = textColor;
                
                // Сохраняем цвет текста в data-атрибут для будущих использований
                paragraph.dataset.contrastColor = textColor;
            }
        }
    });
}

// Запускаем всё после загрузки DOM
document.addEventListener('DOMContentLoaded', async () => {
    formatTimeStrings();
    await processColors();
    setContrastColor();
});