# Sistema de Locação de Hotel

Sistema web para gerenciamento de reservas de hotel, desenvolvido com Flask e SQLite.

## Funcionalidades

- Reserva de quartos (solteiro, casal, luxo)
- Cálculo automático do valor total por período
- Gerenciamento de clientes e reservas
- Check-in e check-out
- Cadastro e gerenciamento de funcionários

## Tecnologias

- Python / Flask
- SQLAlchemy + Flask-Migrate
- SQLite
- Tailwind CSS

## Como executar

**1. Instalar dependências**
```bash
pip install -r requirements.txt
```

**2. Criar o banco de dados**
```bash
python seed.py
```

**3. Rodar o projeto**
```bash
python main.py
```

**4. Acessar no navegador**
```
http://localhost:5000
```

## Rotas

| Rota | Descrição |
|------|-----------|
| `/` | Formulário de reserva |
| `/manage` | Gerenciamento de reservas e clientes |
| `/manage_emp` | Gerenciamento de funcionários |
