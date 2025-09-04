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


function handleCarSubmit(event) {
    event.preventDefault();

    const carId = document.getElementById('carId').value;
    const method = carId ? 'PUT' : 'POST';
    const url = carId ? `/api/cars/${carId}` : '/api/cars';

    const formData = {
        brand: document.getElementById('brand').value,
        model: document.getElementById('model').value,
        year: parseInt(document.getElementById('year').value),
        vin: document.getElementById('vin').value,
        license_plate: document.getElementById('license_plate').value,
        color: document.getElementById('color').value,
        status: document.getElementById('status').value,
        condition: document.getElementById('condition').value,
        engine_type: document.getElementById('engine_type').value,
        engine_volume: parseFloat(document.getElementById('engine_volume').value) || null,
        horsepower: parseInt(document.getElementById('horsepower').value) || null,
        transmission: document.getElementById('transmission').value,
        mileage: parseInt(document.getElementById('mileage').value) || 0,
        purchase_price: parseFloat(document.getElementById('purchase_price').value) || null,
        purchase_date: document.getElementById('purchase_date').value || null,
        sale_price: parseFloat(document.getElementById('sale_price').value) || null,
        sale_date: document.getElementById('sale_date').value || null,
        current_value: parseFloat(document.getElementById('current_value').value) || null,
        insurance_cost: parseFloat(document.getElementById('insurance_cost').value) || null,
        maintenance_cost: parseFloat(document.getElementById('maintenance_cost').value) || null,
        fuel_cost: parseFloat(document.getElementById('fuel_cost').value) || null,
        description: document.getElementById('description').value
    };

    // Удаляем пустые поля
    Object.keys(formData).forEach(key => {
        if (formData[key] === null || formData[key] === '') {
            delete formData[key];
        }
    });

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.ok) {
            closeCarModal();
            window.location.reload();
        } else {
            alert('Ошибка при сохранении');
        }
    });
}
