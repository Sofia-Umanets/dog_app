// calendar_handlers.js
class CalendarHandler {
    constructor() {
        this.calendar = null;
        this.currentEventId = null;
    }

    initialize() {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl) return;

        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'ru',
            height: 'auto',
            events: window.calendarEvents || [], // события будут передаваться из шаблона
            dateClick: (info) => this.handleDateClick(info)
        });

        this.calendar.render();
        this.initializeModals();
        this.handleUrlHash();
    }

    handleDateClick(info) {
        const clickedDate = info.dateStr;
        document.getElementById('eventDate').innerText = clickedDate;

        const matched = this.calendar.getEvents().filter(e => e.startStr === clickedDate);
        let html = this.generateEventsHtml(matched);

        document.getElementById('eventList').innerHTML = html;
        document.getElementById('eventModal').style.display = 'block';
    }

    generateEventsHtml(events) {
        if (events.length === 0) return '<p>Нет событий</p>';

        return events.map(event => {
            const yearlyNote = event.extendedProps.is_yearly ? ' (Ежегодное)' : '';
            const statusClass = event.extendedProps.is_done ? 'done' : 'not-done';
            return `
                <div class="event-card ${statusClass}">
                    <b>${event.title}${yearlyNote}</b><br>
                    ${event.extendedProps.time ? `Время: ${event.extendedProps.time}<br>` : ''}
                    ${event.extendedProps.note ? `Заметка: ${event.extendedProps.note}<br>` : ''}
                    ${event.extendedProps.remind ? `<i>Напомнить: ${event.extendedProps.remind}</i><br>` : ''}
                    ${event.extendedProps.is_done ? '✅ Выполнено' : '❌ Не выполнено'}<br>
                    <div class="event-actions">
                        <a href="${event.extendedProps.edit_url}" class="btn">✏️ Редактировать</a>
                        ${!event.extendedProps.is_done ? 
                            `<a href="${event.extendedProps.done_url}" class="btn" 
                                onclick="return confirm('Отметить событие как выполненное?')">
                                ✅ Завершить
                            </a>` 
                            : ''
                        }
                        ${event.extendedProps.is_yearly ? 
                            `<a href="#" class="btn" onclick="calendarHandler.showDeleteConfirmation('${event.extendedProps.id}'); return false;">
                                🗑 Удалить
                            </a>` :
                            `<a href="${event.extendedProps.delete_url}" class="btn" 
                                onclick="return confirm('Удалить событие?')">🗑 Удалить</a>`
                        }
                    </div>
                </div>`;
        }).join('<br>');
    }

    showDeleteConfirmation(eventId) {
        this.currentEventId = eventId;
        document.getElementById('deleteEventModal').style.display = 'block';
    }

    closeDeleteModal() {
        document.getElementById('deleteEventModal').style.display = 'none';
        this.currentEventId = null;
    }

    closeEventModal() {
        document.getElementById('eventModal').style.display = 'none';
    }

    handleUrlHash() {
        if (window.location.hash) {
            const dateStr = window.location.hash.slice(1);
            try {
                const date = new Date(dateStr);
                if (!isNaN(date)) {
                    this.calendar.gotoDate(date);
                    setTimeout(() => {
                        const calendarTop = document.getElementById('calendar').getBoundingClientRect().top;
                        const offset = window.pageYOffset + calendarTop - 100;
                        window.scrollTo({
                            top: offset,
                            behavior: 'smooth'
                        });
                    }, 100);
                }
            } catch (e) {
                console.error('Invalid date in hash:', e);
            }
        }
    }

    initializeModals() {
        // Закрытие модальных окон при клике вне их области
        window.onclick = (event) => {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
                if (event.target.id === 'deleteEventModal') {
                    this.currentEventId = null;
                }
            }
        };
    }
}

// Создаем глобальный экземпляр обработчика
const calendarHandler = new CalendarHandler();

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    calendarHandler.initialize();
});