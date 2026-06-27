document.getElementById('avatarForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Отменяем стандартную отправку формы
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/api/change-avatar', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const data = await response.json(); // Парсим JSON ответ
        
        if (data.success) {
            // Успех - обновляем аватар на странице
            document.querySelectorAll('.currentAvatar').forEach(element => {
                element.src = data.new_avatar_url + '?t=' + Date.now();
            });
            document.getElementById('message').innerHTML = 
                '<div class="alert alert-success">' + data.message + '</div>';
            document.getElementById('avatarForm').reset(); // Очищаем форму
        } else {
            // Ошибка - показываем сообщения об ошибках
            let errorMessage = 'Ошибка загрузки:<br>';
            for (let field in data.errors) {
                errorMessage += field + ': ' + data.errors[field] + '<br>';
            }
            document.getElementById('message').innerHTML = 
                '<div class="alert alert-danger">' + errorMessage + '</div>';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('message').innerHTML = 
            '<div class="alert alert-danger">Произошла ошибка при загрузке</div>';
    }
});

document.getElementById('avatarForm').addEventListener('change', function(e) {
    if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        
        // Проверка типа файла
        if (!file.type.startsWith('image/')) {
            alert('Пожалуйста, выберите изображение');
            return;
        }
        
        const reader = new FileReader();
        
        reader.onload = function(event) {
            // Обновляем все элементы с классом 'currentAvatar'
            document.querySelectorAll('.currentAvatar').forEach(element => {
                element.src = event.target.result;
            });
        };
        
        reader.onerror = function() {
            console.error('Ошибка чтения файла');
            showMessage('Ошибка при чтении файла', 'error');
        };
        
        reader.readAsDataURL(file);
    }
});