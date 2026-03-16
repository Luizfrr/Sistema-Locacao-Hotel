from app import db
from decimal import Decimal

class Client(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)

class Booking(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False)
    exit_date = db.Column(db.Date, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('quartos.id'), nullable=False)

    payments = db.relationship('Payment', backref='booking', cascade='all, delete-orphan')
    checks = db.relationship('Check', backref='booking', cascade='all, delete-orphan')

class Room(db.Model):
    __tablename__ = 'quartos'
    id = db.Column(db.Integer, primary_key=True)
    availability = db.Column(db.String(3), nullable=False, default='sim')
    room_type = db.Column(db.String(10), nullable=False)
    number = db.Column(db.String(3), nullable=False)

class AvailableDates(db.Model):
    __tablename__ = 'datas_disponiveis'
    id = db.Column(db.Integer, primary_key=True)
    dates = db.Column(db.Date, nullable=False)

class Check(db.Model):
    __tablename__ = 'checkins'
    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)

    booking_id = db.Column(db.Integer, db.ForeignKey('reservas.id', ondelete='CASCADE'), nullable=False)

class Payment(db.Model):
    __tablename__ = 'pagamentos'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False, default='pendente')
    value = db.Column(db.Numeric(8,2), nullable=True)

    booking_id = db.Column(db.Integer, db.ForeignKey('reservas.id', ondelete='CASCADE'), nullable=False)
    receipts = db.relationship('Receipt', backref='payment', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        if 'value' in kwargs:
            kwargs['value'] = Decimal(str(kwargs['value']))
        super(Payment, self).__init__(**kwargs)

class Receipt(db.Model):
    __tablename__ = 'recibos'
    id = db.Column(db.Integer, primary_key=True)
    payment_form = db.Column(db.String(10), nullable=False)
    date_issue = db.Column(db.Date, nullable=False)
    payment_value = db.Column(db.Numeric(8,2), nullable=False)

    payment_id = db.Column(db.Integer, db.ForeignKey('pagamentos.id', ondelete='CASCADE'), nullable=False)

class Employee(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(15), nullable=False)
    cpf = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    hiring_date = db.Column(db.Date, nullable=False)
    job_title = db.Column(db.String(20), nullable=False)