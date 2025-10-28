class AjaxHandler {
    constructor() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async sendRequest(url, method = 'GET', data = null, contentType = 'application/json') {
        const headers = {
            'X-CSRFToken': this.getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        };

        if (contentType) {
            headers['Content-Type'] = contentType;
        }

        const options = {
            method: method,
            headers: headers,
            credentials: 'same-origin'
        };

        if (data) {
            options.body = contentType === 'application/json' ? JSON.stringify(data) : data;
        }

        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentTypeHeader = response.headers.get('content-type');
            if (contentTypeHeader && contentTypeHeader.includes('application/json')) {
                return await response.json();
            }
            return await response.text();
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }

    async rateLesson(lessonId, rating, petId) {
        const formData = new FormData();
        formData.append('rating', rating);
        if (petId) formData.append('pet_id', petId);
        
        return this.sendRequest(
            `/training/rate/${lessonId}/`,
            'POST',
            formData,
            null
        );
    }

    async toggleLessonStatus(petId, lessonId, newStatus) {
        return this.sendRequest(
            `/training/status/${petId}/${lessonId}/${newStatus}/`,
            'POST'
        );
    }

    async getLessonStatus(lessonId, petId) {
        return this.sendRequest(
            `/training/lesson/${lessonId}/?pet=${petId}`,
            'GET'
        );
    }
}

const ajaxHandler = new AjaxHandler();

// Обработчики событий
async function handlePetChange(petId) {
    if (!petId) return;

    try {
        const lessonId = document.querySelector('[name="lesson_id"]').value;
        const response = await ajaxHandler.getLessonStatus(lessonId, petId);
        
        const statusContainer = document.getElementById('lesson-status-container');
        if (statusContainer && response.status_html) {
            statusContainer.innerHTML = response.status_html;
            statusContainer.style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Ошибка при обновлении статуса урока');
    }
}

async function handleRatingSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const lessonId = form.querySelector('[name="lesson_id"]').value;
    const rating = form.querySelector('input[name="rating"]:checked')?.value;
    const petId = form.querySelector('[name="pet_id"]')?.value;

    if (!rating) {
        showError('Пожалуйста, выберите оценку');
        return;
    }

    try {
        const response = await ajaxHandler.rateLesson(lessonId, rating, petId);
        updateRatingUI(response);
    } catch (error) {
        console.error('Error:', error);
        showError('Ошибка при сохранении оценки');
    }
}

async function handleLessonStatus(petId, lessonId, newStatus) {
    try {
        const response = await ajaxHandler.toggleLessonStatus(petId, lessonId, newStatus);
        updateLessonStatusUI(response);
    } catch (error) {
        console.error('Error:', error);
        showError('Ошибка при изменении статуса урока');
    }
}

// Функции обновления UI
function updateRatingUI(data) {
    const averageContainer = document.querySelector('.circle-average');
    if (averageContainer) {
        const mainSpan = averageContainer.querySelector('.circle-main');
        const countSpan = averageContainer.querySelector('.rating-count');
        
        if (data.average_rating) {
            mainSpan.textContent = data.average_rating.toFixed(1);
            mainSpan.classList.remove('empty');
        } else {
            mainSpan.textContent = '—';
            mainSpan.classList.add('empty');
        }
        
        countSpan.textContent = `(${data.ratings_count} оценок)`;
    }

    const userRatingDisplay = document.getElementById('user-rating-display');
    if (userRatingDisplay) {
        userRatingDisplay.innerHTML = `<p>Ваша оценка: <b>${data.user_rating}</b></p>`;
    }

    // Обновляем выбранную звезду
    const ratingInputs = document.querySelectorAll('.rating-stars input');
    ratingInputs.forEach(input => {
        if (input.value === data.user_rating.toString()) {
            input.checked = true;
            input.nextElementSibling.classList.add('active');
        } else {
            input.nextElementSibling.classList.remove('active');
        }
    });
}

function updateLessonStatusUI(data) {
    const statusContainer = document.getElementById('lesson-status-container');
    if (statusContainer) {
        if (data.status_html) {
            statusContainer.innerHTML = data.status_html;
        } else {
            let statusHTML = '';
            if (data.new_status === 'completed') {
                statusHTML = `
                    <span class="status-completed">✅ Завершено</span>
                    <a href="#" onclick="handleLessonStatus('${data.pet_id}', '${data.lesson_id}', 'in_progress'); return false;" 
                       class="status-action-link">Вернуть в процесс</a>
                `;
            } else if (data.new_status === 'in_progress') {
                statusHTML = `
                    <span class="status-in-progress">⏳ В процессе</span>
                    <a href="#" onclick="handleLessonStatus('${data.pet_id}', '${data.lesson_id}', 'completed'); return false;" 
                       class="status-action-link">Завершить</a>
                `;
            } else {
                statusHTML = `
                    <span class="status-not-started">❌ Не начат</span>
                    <a href="#" onclick="handleLessonStatus('${data.pet_id}', '${data.lesson_id}', 'in_progress'); return false;" 
                       class="status-action-link">Начать</a>
                `;
            }
            statusContainer.innerHTML = statusHTML;
        }
    }
}

function showError(message) {
    alert(message);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeHandlers();
    initializeRatingStars();
});

function initializeHandlers() {
    // Инициализация формы рейтинга
    const ratingForm = document.getElementById('rating-form');
    if (ratingForm) {
        ratingForm.addEventListener('submit', handleRatingSubmit);
    }

    // Обработчик выбора питомца
    const petSelect = document.getElementById('pet');
    if (petSelect) {
        petSelect.addEventListener('change', function() {
            const selectedPetId = this.value;
            if (selectedPetId) {
                handlePetChange(selectedPetId);
            }
        });
    }

    // Обработчик кнопки "Назад"
    const backLink = document.querySelector('.back-link');
    if (backLink) {
        backLink.addEventListener('click', function(e) {
            this.style.transform = 'translateY(0)';
            setTimeout(() => {
                this.style.transform = 'translateY(-2px)';
            }, 100);
        });
    }
}

function initializeRatingStars() {
    const ratingStars = document.querySelector('.rating-stars');
    if (ratingStars) {
        const labels = ratingStars.querySelectorAll('label');
        
        // Добавляем обработчики для звезд
        labels.forEach(label => {
            label.addEventListener('click', function() {
                labels.forEach(lbl => lbl.classList.remove('active'));
                this.classList.add('active');
            });

            // Добавляем эффект при наведении
            label.addEventListener('mouseover', function() {
                const rating = this.previousElementSibling.value;
                labels.forEach(lbl => {
                    if (lbl.previousElementSibling.value <= rating) {
                        lbl.classList.add('hover');
                    }
                });
            });

            label.addEventListener('mouseout', function() {
                labels.forEach(lbl => lbl.classList.remove('hover'));
            });
        });

        // Устанавливаем активную звезду при загрузке
        const checkedRadio = ratingStars.querySelector('input[type="radio"]:checked');
        if (checkedRadio) {
            checkedRadio.nextElementSibling.classList.add('active');
        }
    }
}

// Добавляем вспомогательные функции для анимаций и визуальных эффектов
function animateElement(element, className, duration = 300) {
    element.classList.add(className);
    setTimeout(() => {
        element.classList.remove(className);
    }, duration);
}

function showSuccessMessage(message) {
    const messageContainer = document.createElement('div');
    messageContainer.className = 'success-message';
    messageContainer.textContent = message;
    document.body.appendChild(messageContainer);

    setTimeout(() => {
        messageContainer.classList.add('show');
    }, 100);

    setTimeout(() => {
        messageContainer.classList.remove('show');
        setTimeout(() => {
            messageContainer.remove();
        }, 300);
    }, 3000);
}

// Добавляем обработку ошибок и логирование
function logError(error, context) {
    console.error(`Error in ${context}:`, error);
    // Здесь можно добавить отправку ошибок в систему мониторинга
}

// Функция для проверки состояния сети
function checkOnline() {
    if (!navigator.onLine) {
        showError('Отсутствует подключение к интернету');
        return false;
    }
    return true;
}

// Обновленная функция показа ошибок
function showError(message) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'error-message';
    errorContainer.textContent = message;
    document.body.appendChild(errorContainer);

    setTimeout(() => {
        errorContainer.classList.add('show');
    }, 100);

    setTimeout(() => {
        errorContainer.classList.remove('show');
        setTimeout(() => {
            errorContainer.remove();
        }, 300);
    }, 3000);
}

// Добавляем стили для сообщений
const styles = `
    .success-message, .error-message {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 5px;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 1000;
    }

    .success-message {
        background-color: #4CAF50;
        color: white;
    }

    .error-message {
        background-color: #f44336;
        color: white;
    }

    .success-message.show, .error-message.show {
        opacity: 1;
    }

    .rating-stars label.hover {
        color: #ffd700;
        transform: scale(1.1);
    }
`;

// Добавляем стили на страницу
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);

function submitRating() {
    const form = document.getElementById('rating-form');
    const rating = form.querySelector('input[name="rating"]:checked')?.value;
    const lessonId = form.querySelector('[name="lesson_id"]').value;
    const petId = form.querySelector('[name="pet_id"]')?.value;
    const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;

    if (!rating) {
        showError('Пожалуйста, выберите оценку');
        return;
    }

    const formData = new FormData();
    formData.append('rating', rating);
    if (petId) formData.append('pet_id', petId);

    fetch(`/training/rate/${lessonId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateRatingUI(data);
            showSuccess(data.message);
        } else {
            showError(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Произошла ошибка при сохранении оценки');
    });
}

function updateRatingUI(data) {
    const averageContainer = document.querySelector('.circle-average');
    if (averageContainer) {
        const mainSpan = averageContainer.querySelector('.circle-main');
        const countSpan = averageContainer.querySelector('.rating-count');
        
        if (data.average_rating) {
            mainSpan.textContent = data.average_rating.toFixed(1);
            mainSpan.classList.remove('empty');
        } else {
            mainSpan.textContent = '—';
            mainSpan.classList.add('empty');
        }
        
        countSpan.textContent = `(${data.ratings_count} оценок)`;
    }

    const userRatingDisplay = document.getElementById('user-rating-display');
    if (userRatingDisplay) {
        userRatingDisplay.innerHTML = `<p>Ваша оценка: <b>${data.user_rating}</b></p>`;
    }
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.style.position = 'fixed';
    successDiv.style.top = '20px';
    successDiv.style.right = '20px';
    successDiv.style.zIndex = '1000';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);

    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.style.position = 'fixed';
    errorDiv.style.top = '20px';
    errorDiv.style.right = '20px';
    errorDiv.style.zIndex = '1000';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

