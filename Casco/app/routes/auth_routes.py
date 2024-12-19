from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Usuario, db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        senha = request.form['senha']
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Email já registrado! Tente outro.', 'danger')
            return redirect(url_for('register'))
        hashed_senha = generate_password_hash(senha, method='sha256')
        novo_usuario = Usuario(username=username, email=email, senha=hashed_senha, tipo='participante', admin=False)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Registrado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
    pass

@auth.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['user_id'] = usuario.id
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    return render_template('login.html')
    pass

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Deslogado com sucesso!', 'success')
    return redirect(url_for('login'))
    pass
