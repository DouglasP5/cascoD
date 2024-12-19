from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import Usuario, Equipe, Convite

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def dashboard_view():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('login'))
    
    equipes_participantes = Equipe.query.join(Convite).filter(
        (Convite.usuario_id == usuario.id) & (Convite.status == 'aceito')
    ).all()

    equipes_lideradas = Equipe.query.filter_by(lider_id=usuario.id).all()
    
    return render_template('dashboard.html', usuario=usuario, 
                           equipes_participantes=equipes_participantes,
                           equipes_lideradas=equipes_lideradas)

@dashboard.route('/me')
def me():
    if 'user_id' not in session:
        flash('Você precisa estar logado para ver seus dados!', 'warning')
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('login'))
    return render_template('me.html', usuario=usuario)

@dashboard.route('/api/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({"error": "Você precisa estar logado para ver seus dados!"}), 403
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        return jsonify({"error": "Usuário não encontrado!"}), 404
    return jsonify({
        "username": usuario.username,
        "email": usuario.email,
        "id": usuario.id
    })
