"""
Script para criar as tabelas e popular o banco de dados com dados iniciais.
Execute com: python seed.py
"""

from app import app, db
from app.models import Room, AvailableDates, Employee
from datetime import date, timedelta

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Tabelas criadas com sucesso!")

    # Quartos
    quartos = [
        Room(number='101', room_type='solteiro', availability='sim'),
        Room(number='102', room_type='solteiro', availability='sim'),
        Room(number='201', room_type='casal',    availability='sim'),
        Room(number='202', room_type='casal',    availability='sim'),
        Room(number='301', room_type='luxo',     availability='sim'),
        Room(number='302', room_type='luxo',     availability='sim'),
    ]
    db.session.add_all(quartos)

    # Datas disponíveis: próximos 60 dias
    hoje = date.today()
    datas = [AvailableDates(dates=hoje + timedelta(days=i)) for i in range(60)]
    db.session.add_all(datas)

    # Funcionários de exemplo
    funcionarios = [
        Employee(
            name='Ana Souza',
            telephone='(71) 99999-0001',
            cpf='111.222.333-44',
            date_of_birth=date(1990, 5, 12),
            hiring_date=date(2020, 1, 15),
            job_title='Recepcionista'
        ),
        Employee(
            name='Carlos Lima',
            telephone='(71) 99999-0002',
            cpf='555.666.777-88',
            date_of_birth=date(1985, 8, 20),
            hiring_date=date(2018, 3, 1),
            job_title='Gerente'
        ),
    ]
    db.session.add_all(funcionarios)

    db.session.commit()
    print("Dados iniciais inseridos com sucesso!")
    print(f"  - {len(quartos)} quartos criados")
    print(f"  - {len(datas)} datas disponíveis (próximos 60 dias)")
    print(f"  - {len(funcionarios)} funcionários criados")
