from datetime import datetime, time, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Сессия на 24 часа
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Конфигурация пользователя
USER_CREDENTIALS = {
    'Сергей': generate_password_hash('336996')
}


# Модели БД
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat()
        }


class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.String(20), default='meeting')  # meeting, call, task, reminder
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('events', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start': self.start_time.isoformat(),
            'end': self.end_time.isoformat(),
            'type': self.event_type,
            'location': self.location,
            'status': self.status
        }


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Основная информация
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    photo = db.Column(db.String(200))  # путь к фото

    # Паспортные данные
    passport_series = db.Column(db.String(4))
    passport_number = db.Column(db.String(6))
    passport_issued_by = db.Column(db.String(200))
    passport_issue_date = db.Column(db.Date)
    passport_department_code = db.Column(db.String(7))

    # Адрес
    address_index = db.Column(db.String(10))
    address_country = db.Column(db.String(50))
    address_region = db.Column(db.String(50))
    address_city = db.Column(db.String(50))
    address_street = db.Column(db.String(100))
    address_house = db.Column(db.String(10))
    address_apartment = db.Column(db.String(10))

    # Дополнительная информация
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    category = db.Column(db.String(20), default='client')  # client, partner, supplier, etc.

    # Социальные сети
    social_telegram = db.Column(db.String(100))
    social_whatsapp = db.Column(db.String(100))
    social_vk = db.Column(db.String(100))

    # Заметки
    notes = db.Column(db.Text)

    # Системные поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('contacts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'phone': self.phone,
            'email': self.email,
            'photo': self.photo,
            'passport_series': self.passport_series,
            'passport_number': self.passport_number,
            'passport_issued_by': self.passport_issued_by,
            'passport_issue_date': self.passport_issue_date.isoformat() if self.passport_issue_date else None,
            'passport_department_code': self.passport_department_code,
            'full_address': self.get_full_address(),
            'company': self.company,
            'position': self.position,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'category': self.category,
            'social_telegram': self.social_telegram,
            'social_whatsapp': self.social_whatsapp,
            'social_vk': self.social_vk,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def get_full_address(self):
        address_parts = []
        if self.address_index:
            address_parts.append(self.address_index)
        if self.address_country:
            address_parts.append(self.address_country)
        if self.address_region:
            address_parts.append(self.address_region)
        if self.address_city:
            address_parts.append(f"г. {self.address_city}")
        if self.address_street:
            address_parts.append(f"ул. {self.address_street}")
        if self.address_house:
            address_parts.append(f"д. {self.address_house}")
        if self.address_apartment:
            address_parts.append(f"кв. {self.address_apartment}")
        return ", ".join(address_parts) if address_parts else "Адрес не указан"

    def get_full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Основная информация
    vin = db.Column(db.String(17), unique=True, nullable=False)
    license_plate = db.Column(db.String(15), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30))

    # Технические характеристики
    engine_type = db.Column(db.String(20))  # бензин, дизель, электро
    engine_volume = db.Column(db.Float)  # литры
    horsepower = db.Column(db.Integer)
    transmission = db.Column(db.String(20))  # автомат, механика
    mileage = db.Column(db.Integer)  # пробег в км

    # Финансовая информация
    purchase_price = db.Column(db.Float)
    purchase_date = db.Column(db.Date)
    sale_price = db.Column(db.Float)
    sale_date = db.Column(db.Date)
    current_value = db.Column(db.Float)

    # Состояние и статус
    status = db.Column(db.String(20), default='in_stock')  # in_stock, sold, in_service
    condition = db.Column(db.String(20))  # новый, б/у, аварийный
    description = db.Column(db.Text)

    # Затраты на содержание
    insurance_cost = db.Column(db.Float)
    maintenance_cost = db.Column(db.Float)
    fuel_cost = db.Column(db.Float)

    # Системные поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'vin': self.vin,
            'license_plate': self.license_plate,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'color': self.color,
            'engine_type': self.engine_type,
            'engine_volume': self.engine_volume,
            'horsepower': self.horsepower,
            'transmission': self.transmission,
            'mileage': self.mileage,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'sale_price': self.sale_price,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'current_value': self.current_value,
            'status': self.status,
            'condition': self.condition,
            'description': self.description,
            'insurance_cost': self.insurance_cost,
            'maintenance_cost': self.maintenance_cost,
            'fuel_cost': self.fuel_cost,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Функция для создания демо-данных
def create_demo_data():
    # Добавляем демо-задачи если их нет
    if Task.query.count() == 0:
        demo_tasks = [
            Task(
                title='Подписать договор с ООО "Ромашка"',
                description='Встреча в главном офисе для подписания договора о сотрудничестве',
                priority='high',
                status='pending',
                due_date=datetime.utcnow() + timedelta(days=1)
            ),
            Task(
                title='Отправить коммерческое предложение',
                description='Подготовить и отправить КП по новому проекту',
                priority='medium',
                status='in_progress',
                due_date=datetime.utcnow() + timedelta(hours=5)
            ),
            Task(
                title='Составить отчет по продажам',
                description='Еженедельный отчет по продажам за текущий период',
                priority='low',
                status='completed',
                due_date=datetime.utcnow() - timedelta(days=1),
                completed_at=datetime.utcnow() - timedelta(hours=3)
            )
        ]
        db.session.bulk_save_objects(demo_tasks)

    # Добавляем демо-события если их нет
    if CalendarEvent.query.count() == 0:
        now = datetime.utcnow()
        demo_events = [
            CalendarEvent(
                title='Встреча с клиентом',
                description='Обсуждение нового проекта',
                start_time=now.replace(hour=10, minute=0, second=0, microsecond=0),
                end_time=now.replace(hour=11, minute=30, second=0, microsecond=0),
                event_type='meeting',
                location='Конференц-зал №1',
                status='scheduled'
            ),
            CalendarEvent(
                title='Звонок поставщику',
                description='Обсуждение условий поставки',
                start_time=now.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=now.replace(hour=14, minute=30, second=0, microsecond=0),
                event_type='call',
                location='',
                status='scheduled'
            ),
            CalendarEvent(
                title='Планирование задач на неделю',
                description='Еженедельное планирование',
                start_time=now.replace(hour=16, minute=0, second=0, microsecond=0),
                end_time=now.replace(hour=17, minute=0, second=0, microsecond=0),
                event_type='task',
                location='Рабочий кабинет',
                status='scheduled'
            )
        ]
        db.session.bulk_save_objects(demo_events)

    # Добавляем демо-контакты если их нет
    if Contact.query.count() == 0:
        now = datetime.utcnow()
        demo_contacts = [
            Contact(
                first_name='Иван',
                last_name='Иванов',
                middle_name='Иванович',
                phone='+79991234567',
                email='ivanov@example.com',
                company='ООО Ромашка',
                position='Менеджер',
                birth_date=now - timedelta(days=365 * 30),
                category='client',
                address_country='Россия',
                address_city='Москва',
                address_street='Ленинская',
                address_house='10',
                address_apartment='5'
            ),
            Contact(
                first_name='Анна',
                last_name='Петрова',
                middle_name='Сергеевна',
                phone='+79997654321',
                email='petrova@example.com',
                company='ООО Лютик',
                position='Директор',
                birth_date=now - timedelta(days=365 * 28),
                category='partner',
                address_country='Россия',
                address_city='Санкт-Петербург',
                address_street='Невский',
                address_house='25'
            )
        ]
        db.session.bulk_save_objects(demo_contacts)

    # Добавляем демо-автомобили если их нет
    if Car.query.count() == 0:
        demo_cars = [
            Car(
                vin='XW8AB12B3FG123456',
                license_plate='А123АА777',
                brand='Toyota',
                model='Camry',
                year=2022,
                color='Черный',
                engine_type='бензин',
                engine_volume=2.5,
                horsepower=249,
                transmission='автомат',
                mileage=15000,
                purchase_price=2500000,
                purchase_date=datetime(2022, 5, 15).date(),
                current_value=2200000,
                status='in_stock',
                condition='used',
                description='Отличное состояние, один владелец',
                insurance_cost=30000,
                maintenance_cost=15000,
                fuel_cost=5000
            ),
            Car(
                vin='Z94CB41BAER123789',
                license_plate='В456ВВ777',
                brand='BMW',
                model='X5',
                year=2021,
                color='Белый',
                engine_type='дизель',
                engine_volume=3.0,
                horsepower=265,
                transmission='автомат',
                mileage=45000,
                purchase_price=3500000,
                purchase_date=datetime(2021, 3, 10).date(),
                sale_price=3200000,
                sale_date=datetime(2023, 8, 20).date(),
                status='sold',
                condition='used',
                description='Полная комплектация, сервисная история',
                insurance_cost=45000,
                maintenance_cost=20000,
                fuel_cost=7000
            )
        ]
        db.session.bulk_save_objects(demo_cars)

    db.session.commit()


# Создаем таблицы и демо-данные при первом запросе
@app.before_request
def before_first_request():
    if not hasattr(app, 'has_created_tables'):
        db.create_all()
        create_demo_data()
        app.has_created_tables = True


# Проверка аутентификации
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# Маршрут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USER_CREDENTIALS and check_password_hash(USER_CREDENTIALS[username], password):
            session['username'] = username
            session.permanent = True

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль')

    return render_template('login.html')


# Маршрут для выхода
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Маршруты
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/car_catalog')
def car_catalog():
    return render_template('car_catalog.html')



@app.route('/tasks')
@login_required
def tasks():
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')

    tasks_query = Task.query

    if status_filter != 'all':
        tasks_query = tasks_query.filter_by(status=status_filter)
    if priority_filter != 'all':
        tasks_query = tasks_query.filter_by(priority=priority_filter)

    tasks = tasks_query.order_by(Task.due_date.asc()).all()
    return render_template('modules/tasks.html', tasks=tasks,
                           status_filter=status_filter, priority_filter=priority_filter)


@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    if request.method == 'POST':
        data = request.get_json()
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
@login_required
def api_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'PUT':
        data = request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.priority = data.get('priority', task.priority)
        task.status = data.get('status', task.status)

        if data.get('due_date'):
            task.due_date = datetime.fromisoformat(data['due_date'])

        if data.get('status') == 'completed' and task.status != 'completed':
            task.completed_at = datetime.utcnow()

        db.session.commit()
        return jsonify(task.to_dict())

    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return '', 204


@app.route('/calendar/<view_type>')
@login_required
def calendar_view(view_type):
    date_str = request.args.get('date')
    if date_str:
        try:
            current_date = datetime.fromisoformat(date_str)
        except ValueError:
            current_date = datetime.utcnow()
    else:
        current_date = datetime.utcnow()

    # Получаем события для выбранной дата/недели/месяца
    if view_type == 'day':
        start_of_day = datetime.combine(current_date, time.min)
        end_of_day = datetime.combine(current_date, time.max)
        events = CalendarEvent.query.filter(
            CalendarEvent.start_time.between(start_of_day, end_of_day)
        ).all()
    elif view_type == 'week':
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        events = CalendarEvent.query.filter(
            CalendarEvent.start_time.between(start_of_week, end_of_week)
        ).all()
    else:  # month
        start_of_month = current_date.replace(day=1)
        if start_of_month.month == 12:
            next_month = start_of_month.replace(year=start_of_month.year + 1, month=1)
        else:
            next_month = start_of_month.replace(month=start_of_month.month + 1)
        end_of_month = next_month - timedelta(days=1)
        events = CalendarEvent.query.filter(
            CalendarEvent.start_time.between(start_of_month, end_of_month)
        ).all()

    return render_template(f'calendar/view_{view_type}.html',
                           events=events,
                           current_date=current_date,
                           view_type=view_type)


@app.route('/api/events', methods=['GET', 'POST'])
@login_required
def api_events():
    if request.method == 'POST':
        data = request.get_json()
        event = CalendarEvent(
            title=data['title'],
            description=data.get('description', ''),
            start_time=datetime.fromisoformat(data['start']),
            end_time=datetime.fromisoformat(data['end']),
            event_type=data.get('type', 'meeting'),
            location=data.get('location', '')
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(event.to_dict()), 201

    start = request.args.get('start')
    end = request.args.get('end')

    if start and end:
        try:
            events = CalendarEvent.query.filter(
                CalendarEvent.start_time.between(
                    datetime.fromisoformat(start),
                    datetime.fromisoformat(end)
                )
            ).all()
        except ValueError:
            events = CalendarEvent.query.all()
    else:
        events = CalendarEvent.query.all()

    return jsonify([event.to_dict() for event in events])


@app.route('/api/events/<int:event_id>', methods=['PUT', 'DELETE'])
@login_required
def api_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)

    if request.method == 'PUT':
        data = request.get_json()
        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        event.start_time = datetime.fromisoformat(data['start'])
        event.end_time = datetime.fromisoformat(data['end'])
        event.event_type = data.get('type', event.event_type)
        event.location = data.get('location', event.location)
        event.status = data.get('status', event.status)

        db.session.commit()
        return jsonify(event.to_dict())

    elif request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return '', 204


@app.route('/contacts')
@login_required
def contacts():
    category_filter = request.args.get('category', 'all')
    contacts_query = Contact.query

    if category_filter != 'all':
        contacts_query = contacts_query.filter_by(category=category_filter)

    contacts = contacts_query.order_by(Contact.last_name.asc()).all()
    return render_template('contacts.html', contacts=contacts, category_filter=category_filter)


@app.route('/api/contacts', methods=['GET', 'POST'])
@login_required
def api_contacts():
    if request.method == 'POST':
        data = request.get_json()
        contact = Contact(
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data.get('middle_name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            passport_series=data.get('passport_series', ''),
            passport_number=data.get('passport_number', ''),
            passport_issued_by=data.get('passport_issued_by', ''),
            passport_issue_date=datetime.fromisoformat(data['passport_issue_date']) if data.get(
                'passport_issue_date') else None,
            passport_department_code=data.get('passport_department_code', ''),
            address_index=data.get('address_index', ''),
            address_country=data.get('address_country', ''),
            address_region=data.get('address_region', ''),
            address_city=data.get('address_city', ''),
            address_street=data.get('address_street', ''),
            address_house=data.get('address_house', ''),
            address_apartment=data.get('address_apartment', ''),
            company=data.get('company', ''),
            position=data.get('position', ''),
            birth_date=datetime.fromisoformat(data['birth_date']) if data.get('birth_date') else None,
            category=data.get('category', 'client'),
            social_telegram=data.get('social_telegram', ''),
            social_whatsapp=data.get('social_whatsapp', ''),
            social_vk=data.get('social_vk', ''),
            notes=data.get('notes', '')
        )
        db.session.add(contact)
        db.session.commit()
        return jsonify(contact.to_dict()), 201

    contacts = Contact.query.all()
    return jsonify([contact.to_dict() for contact in contacts])


@app.route('/api/contacts/<int:contact_id>', methods=['PUT', 'DELETE'])
@login_required
def api_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    if request.method == 'PUT':
        data = request.get_json()
        contact.first_name = data.get('first_name', contact.first_name)
        contact.last_name = data.get('last_name', contact.last_name)
        contact.middle_name = data.get('middle_name', contact.middle_name)
        contact.phone = data.get('phone', contact.phone)
        contact.email = data.get('email', contact.email)
        contact.passport_series = data.get('passport_series', contact.passport_series)
        contact.passport_number = data.get('passport_number', contact.passport_number)
        contact.passport_issued_by = data.get('passport_issued_by', contact.passport_issued_by)
        contact.passport_issue_date = datetime.fromisoformat(data['passport_issue_date']) if data.get(
            'passport_issue_date') else contact.passport_issue_date
        contact.passport_department_code = data.get('passport_department_code', contact.passport_department_code)
        contact.address_index = data.get('address_index', contact.address_index)
        contact.address_country = data.get('address_country', contact.address_country)
        contact.address_region = data.get('address_region', contact.address_region)
        contact.address_city = data.get('address_city', contact.address_city)
        contact.address_street = data.get('address_street', contact.address_street)
        contact.address_house = data.get('address_house', contact.address_house)
        contact.address_apartment = data.get('address_apartment', contact.address_apartment)
        contact.company = data.get('company', contact.company)
        contact.position = data.get('position', contact.position)
        contact.birth_date = datetime.fromisoformat(data['birth_date']) if data.get(
            'birth_date') else contact.birth_date
        contact.category = data.get('category', contact.category)
        contact.social_telegram = data.get('social_telegram', contact.social_telegram)
        contact.social_whatsapp = data.get('social_whatsapp', contact.social_whatsapp)
        contact.social_vk = data.get('social_vk', contact.social_vk)
        contact.notes = data.get('notes', contact.notes)

        db.session.commit()
        return jsonify(contact.to_dict())

    elif request.method == 'DELETE':
        db.session.delete(contact)
        db.session.commit()
        return '', 204


@app.route('/warehouse')
@login_required
def warehouse():
    status_filter = request.args.get('status', 'all')
    cars_query = Car.query

    if status_filter != 'all':
        cars_query = cars_query.filter_by(status=status_filter)

    cars = cars_query.order_by(Car.brand.asc(), Car.model.asc()).all()
    return render_template('warehouse.html', cars=cars, status_filter=status_filter)


@app.route('/api/cars', methods=['GET', 'POST'])
@login_required
def api_cars():
    if request.method == 'POST':
        data = request.get_json()
        car = Car(
            vin=data['vin'],
            license_plate=data['license_plate'],
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            color=data.get('color'),
            engine_type=data.get('engine_type'),
            engine_volume=data.get('engine_volume'),
            horsepower=data.get('horsepower'),
            transmission=data.get('transmission'),
            mileage=data.get('mileage', 0),
            purchase_price=data.get('purchase_price'),
            purchase_date=datetime.fromisoformat(data['purchase_date']) if data.get('purchase_date') else None,
            sale_price=data.get('sale_price'),
            sale_date=datetime.fromisoformat(data['sale_date']) if data.get('sale_date') else None,
            current_value=data.get('current_value'),
            status=data.get('status', 'in_stock'),
            condition=data.get('condition'),
            description=data.get('description'),
            insurance_cost=data.get('insurance_cost'),
            maintenance_cost=data.get('maintenance_cost'),
            fuel_cost=data.get('fuel_cost')
        )
        db.session.add(car)
        db.session.commit()
        return jsonify(car.to_dict()), 201

    cars = Car.query.all()
    return jsonify([car.to_dict() for car in cars])


@app.route('/api/cars/<int:car_id>', methods=['PUT', 'DELETE'])
@login_required
def api_car(car_id):
    car = Car.query.get_or_404(car_id)

    if request.method == 'PUT':
        data = request.get_json()
        car.vin = data.get('vin', car.vin)
        car.license_plate = data.get('license_plate', car.license_plate)
        car.brand = data.get('brand', car.brand)
        car.model = data.get('model', car.model)
        car.year = data.get('year', car.year)
        car.color = data.get('color', car.color)
        car.engine_type = data.get('engine_type', car.engine_type)
        car.engine_volume = data.get('engine_volume', car.engine_volume)
        car.horsepower = data.get('horsepower', car.horsepower)
        car.transmission = data.get('transmission', car.transmission)
        car.mileage = data.get('mileage', car.mileage)
        car.purchase_price = data.get('purchase_price', car.purchase_price)
        car.purchase_date = datetime.fromisoformat(data['purchase_date']) if data.get(
            'purchase_date') else car.purchase_date
        car.sale_price = data.get('sale_price', car.sale_price)
        car.sale_date = datetime.fromisoformat(data['sale_date']) if data.get('sale_date') else car.sale_date
        car.current_value = data.get('current_value', car.current_value)
        car.status = data.get('status', car.status)
        car.condition = data.get('condition', car.condition)
        car.description = data.get('description', car.description)
        car.insurance_cost = data.get('insurance_cost', car.insurance_cost)
        car.maintenance_cost = data.get('maintenance_cost', car.maintenance_cost)
        car.fuel_cost = data.get('fuel_cost', car.fuel_cost)

        db.session.commit()
        return jsonify(car.to_dict())

    elif request.method == 'DELETE':
        db.session.delete(car)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)