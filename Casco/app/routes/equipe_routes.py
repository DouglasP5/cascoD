from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Equipe, Usuario, Convite, db

equipe = Blueprint('equipe', __name__)

@equipe.route('/criar_equipe', methods=['GET', 'POST'])
def criar_equipe():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    
    if not usuario.admin:
        flash('Apenas líderes podem criar equipes!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        equipe_existente = Equipe.query.filter_by(nome=nome).first()
        if equipe_existente:
            flash('Já existe uma equipe com esse nome!', 'danger')
            return redirect(url_for('criar_equipe'))
        
        nova_equipe = Equipe(nome=nome, lider_id=usuario.id)
        db.session.add(nova_equipe)
        db.session.commit()
        
        novo_convite = Convite(usuario_id=usuario.id, equipe_id=nova_equipe.id, status='aceito')
        db.session.add(novo_convite)
        db.session.commit()
        
        flash(f'Equipe "{nome}" criada com sucesso!', 'success')
        return redirect(url_for('equipes'))
    
    return render_template('criar_equipe.html')

@equipe.route('/equipes', methods=['GET', 'POST'])
def equipes():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['user_id'])
    if not usuario.admin:
        flash('Apenas líderes podem acessar essa página!', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        nome = request.form['nome']
        equipe_existente = Equipe.query.filter_by(nome=nome).first()
        if equipe_existente:
            flash('Já existe uma equipe com esse nome!', 'danger')
        else:
            nova_equipe = Equipe(nome=nome, lider_id=usuario.id)
            db.session.add(nova_equipe)
            db.session.commit()
            flash(f'Equipe "{nome}" criada com sucesso!', 'success')
    equipes = Equipe.query.filter_by(lider_id=usuario.id).all()
    return render_template('equipes.html', equipes=equipes)

@equipe.route('/ver_equipe/<int:equipe_id>')
def ver_equipe(equipe_id):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    equipe = Equipe.query.get_or_404(equipe_id)
    usuario = Usuario.query.get(session['user_id'])
    
    integrantes = Usuario.query.join(Convite).filter(
        Convite.equipe_id == equipe_id, Convite.status == 'aceito'
    ).all()
    
    if usuario.id == equipe.lider_id and usuario not in integrantes:
        integrantes.append(usuario)

    is_lider = usuario.id == equipe.lider_id

    return render_template('ver_equipe.html', equipe=equipe, integrantes=integrantes, is_lider=is_lider)
