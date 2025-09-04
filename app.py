from datetime import datetime, time, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


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

    db.session.commit()


# Создаем таблицы и демо-данные при первом запросе
@app.before_request
def before_first_request():
    if not hasattr(app, 'has_created_tables'):
        db.create_all()
        create_demo_data()
        app.has_created_tables = True


# Маршруты
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tasks')
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
def calendar_view(view_type):
    date_str = request.args.get('date')
    if date_str:
        try:
            current_date = datetime.fromisoformat(date_str)
        except ValueError:
            current_date = datetime.utcnow()
    else:
        current_date = datetime.utcnow()

    # Получаем события для выбранной даты/недели/месяца
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


if __name__ == '__main__':
    app.run(debug=True)