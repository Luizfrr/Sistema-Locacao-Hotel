from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, db
from app.forms import BookingForm
from app.models import Check, Client, Booking, Employee, Payment, Room, AvailableDates
from decimal import Decimal
from datetime import datetime
import random





# ------------- RESERVA ---------------
@app.route('/', methods=['GET', 'POST'])
def home():
    form = BookingForm()
    
    dates = AvailableDates.query.order_by(AvailableDates.dates).all()
    form.entry_date.choices = [(str(d.id), d.dates.strftime('%d/%m/%Y')) for d in dates]
    form.exit_date.choices = [(str(d.id), d.dates.strftime('%d/%m/%Y')) for d in dates]

    if form.validate_on_submit():

        try:
            entry_date = AvailableDates.query.get(form.entry_date.data)
            exit_date = AvailableDates.query.get(form.exit_date.data)
            
            if not entry_date or not exit_date:
                flash('Datas inválidas', 'error')
                return redirect(url_for('home'))
            
            valor_total = Decimal(form.total_value.data)
            
            available_rooms = Room.query.filter(
                Room.room_type == form.room_type.data,
                Room.availability == 'sim',
                ~Room.id.in_(
                    db.session.query(Booking.room_id).filter(
                        Booking.entry_date <= exit_date.dates,
                        Booking.exit_date >= entry_date.dates
                    )
                )
            ).all()
        
            if not available_rooms:
                flash('Nenhum quarto disponível para o tipo selecionado', 'error')
                return redirect(url_for('home'))
            
            selected_room = random.choice(available_rooms)
            


            client = Client(
                name=form.name.data,
                telephone=form.telephone.data
            )
            db.session.add(client)
            db.session.flush()


            
            booking = Booking(
                client_id=client.id,
                room_id=selected_room.id,
                entry_date=entry_date.dates,
                exit_date=exit_date.dates,
            )
            db.session.add(booking)
            db.session.flush()



            check = Check(
                check_in=None,
                check_out=None,
                booking_id=booking.id
            )
            db.session.add(check)



            pagamento = Payment(
                status='pendente',
                value=valor_total,
                booking_id=booking.id
            )
            db.session.add(pagamento)
            

            selected_room.availability = 'não'
            
            db.session.commit()
            
            flash(f'Reserva realizada com sucesso! Quarto: {selected_room.number} - Valor Total: R$ {valor_total:,.2f}'.replace('.', ','), 'success')
            return redirect(url_for('home'))
        

            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao processar reserva: {str(e)}', 'error')
            app.logger.error(f"Erro na reserva: {str(e)}")

    return render_template('index.html', form=form)

def get_available_room_types(entry_date_id, exit_date_id):
    entry_date = AvailableDates.query.get(entry_date_id)
    exit_date = AvailableDates.query.get(exit_date_id)
    
    if not entry_date or not exit_date:
        return []
    
    tipos = db.session.query(Room.room_type).filter(
        Room.availability == 'sim',
        ~Room.id.in_(
            db.session.query(Booking.room_id).filter(
                Booking.entry_date <= exit_date.dates,
                Booking.exit_date >= entry_date.dates
            )
        )
    ).distinct().all()
    
    return [t[0] for t in tipos]



@app.route('/api/tipos_disponiveis')
def tipos_disponiveis():
    entry_date_id = request.args.get('entry_date')
    exit_date_id = request.args.get('exit_date')
    
    entry_date = AvailableDates.query.get(entry_date_id)
    exit_date = AvailableDates.query.get(exit_date_id)
    
    if not entry_date or not exit_date:
        return jsonify([])
    
    tipos_disponiveis = db.session.query(Room.room_type).filter(
        Room.availability == 'sim',
        ~Room.id.in_(
            db.session.query(Booking.room_id).filter(
                Booking.entry_date <= exit_date.dates,
                Booking.exit_date >= entry_date.dates
            )
        )
    ).distinct().all()
    
    result = [t[0] for t in tipos_disponiveis]
    return jsonify(result)





# ------------- CLLIENTE ---------------



@app.route('/manage', methods=['GET'])
def manage():
    dados = []

    clientes = Client.query.all()
    for cliente in clientes:
        booking = Booking.query.filter_by(client_id=cliente.id).first()
        quarto = Room.query.get(booking.room_id) if booking else None
        pagamento = Payment.query.filter_by(booking_id=booking.id).first() if booking else None

        dados.append({
            'cliente': cliente,
            'quarto': quarto,
            'pagamento': pagamento,
            'booking': booking
        })

    return render_template('manage.html', dados=dados)




@app.route('/delete/<int:id>', methods=['POST'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    client = Client.query.get_or_404(booking.client_id)
    pagamento = Payment.query.filter_by(booking_id=id).first()

    room = Room.query.get(booking.room_id)
    if room:
        room.availability = 'sim'

    if pagamento:
        db.session.delete(pagamento)

    db.session.delete(booking)
    db.session.delete(client)

    db.session.commit()

    return redirect(url_for('manage'))



@app.route('/cliente/<int:id>', methods=['GET', 'POST'])
def client_view(id):
    cliente = Client.query.get_or_404(id)
    booking = Booking.query.filter_by(client_id=cliente.id).first()
    quarto = Room.query.get(booking.room_id) if booking else None
    pagamento = Payment.query.filter_by(booking_id=booking.id).first() if booking else None
    check = Check.query.filter_by(booking_id=booking.id).first() if booking else None


    if booking:
        if isinstance(booking.entry_date, str):
            booking.entry_date = datetime.strptime(booking.entry_date, '%Y-%m-%d')
        if isinstance(booking.exit_date, str):
            booking.exit_date = datetime.strptime(booking.exit_date, '%Y-%m-%d')


    dados = {
        'cliente': cliente,
        'quarto': quarto,
        'pagamento': pagamento,
        'booking': booking,
        'check': check
    }

    return render_template('client.html', dados=dados, cliente=cliente)



@app.route('/cliente/update/<int:id>', methods=['POST'])
def client_update(id):
    cliente = Client.query.get(id)
    if not cliente:
        return "Cliente não encontrado", 404

    novo_nome = request.form.get('name')
    novo_telefone = request.form.get('telephone')

    cliente.name = novo_nome
    cliente.telephone = novo_telefone

    db.session.commit()

    return "Cliente atualizado com sucesso"



@app.route('/cliente/check/<int:booking_id>', methods=['POST'])
def update_check(booking_id):
    check = Check.query.filter_by(booking_id=booking_id).first_or_404()

    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')

    try:
        check.check_in = datetime.strptime(check_in_str, '%Y-%m-%dT%H:%M') if check_in_str else None
        check.check_out = datetime.strptime(check_out_str, '%Y-%m-%dT%H:%M') if check_out_str else None

        db.session.commit()
        flash('Check-in/Check-out atualizados com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar check-in/out: {str(e)}', 'error')

    return redirect(url_for('client_view', id=check.booking.client_id))





# ------------- FUNCIONÁRIO ---------------

@app.route('/manage_emp', methods=['GET'])
def listar_funcionarios():
    funcionarios = Employee.query.all()
    return render_template('manage_emp.html', funcionarios=funcionarios)



@app.route('/funcionario/edit/<int:id>', methods=['GET'])
def funcionario_edit(id):
    funcionario = Employee.query.get_or_404(id)
    return render_template('employee.html', funcionario=funcionario)



@app.route('/funcionario/update/<int:id>', methods=['POST'])
def funcionario_update(id):
    funcionario = Employee.query.get_or_404(id)

    novo_nome = request.form.get('name')
    novo_telefone = request.form.get('telephone')
    novo_cpf = request.form.get('cpf')
    nova_data_nascimento = request.form.get('date_of_birth')
    nova_data_contratacao = request.form.get('hiring_date')
    novo_cargo = request.form.get('job_title')

    funcionario.name = novo_nome
    funcionario.telephone = novo_telefone
    funcionario.cpf = novo_cpf
    if nova_data_nascimento:
        funcionario.date_of_birth = datetime.strptime(nova_data_nascimento, '%Y-%m-%d').date()
    if nova_data_contratacao:
        funcionario.hiring_date = datetime.strptime(nova_data_contratacao, '%Y-%m-%d').date()
    funcionario.job_title = novo_cargo

    db.session.commit()

    return redirect(url_for('listar_funcionarios'))



@app.route('/funcionario/delete/<int:id>', methods=['POST'])
def funcionario_delete(id):
    funcionario = Employee.query.get_or_404(id)

    db.session.delete(funcionario)
    db.session.commit()

    return redirect(url_for('listar_funcionarios'))