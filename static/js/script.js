document.addEventListener('DOMContentLoaded', function() {
    // Переключение сайдбара
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Уведомления
    const notificationBtn = document.querySelector('.header-btn:nth-child(1)');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', function() {
            alert('Уведомления будут реализованы позже');
        });
    }

    // Поиск
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                alert('Поиск: ' + this.value);
                this.value = '';
            }
        });
    }

    // Переключение вкладок
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Обработка чекбоксов задач
    const taskCheckboxes = document.querySelectorAll('.task-checkbox input');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskItem = this.closest('.task-item');
            if (this.checked) {
                taskItem.style.opacity = '0.6';
                taskItem.style.textDecoration = 'line-through';
            } else {
                taskItem.style.opacity = '1';
                taskItem.style.textDecoration = 'none';
            }
        });
    });

    // Модальные окна (будет расширено)
    window.showModal = function(modalId) {
        alert('Модальное окно ' + modalId + ' будет реализовано');
    };
});

// Инициализация календаря
function initCalendar() {
    const currentTimeLine = document.querySelector('.current-time-line');
    if (currentTimeLine) {
        updateCurrentTimeLine();
        setInterval(updateCurrentTimeLine, 60000); // Обновлять каждую минуту
    }
}

function updateCurrentTimeLine() {
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();

    if (currentHour >= 8 && currentHour < 20) {
        const timeLine = document.querySelector('.current-time-line');
        const position = ((currentHour - 8) * 60 + currentMinute) * 60; // В пикселях
        timeLine.style.top = position + 'px';
        timeLine.style.display = 'block';
    }
}

// Drag and drop для событий (упрощенная версия)
function initDragAndDrop() {
    const events = document.querySelectorAll('.calendar-event');
    events.forEach(event => {
        event.addEventListener('mousedown', startDrag);
    });
}

function startDrag(e) {
    // Реализация drag and drop будет добавлена позже
    console.log('Drag started');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // ... предыдущая инициализация ...

    initCalendar();
    initDragAndDrop();
});