from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/casco'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='participante')
    admin = db.Column(db.Boolean, default=False)

class Equipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    lider_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    lider = db.relationship('Usuario', backref='equipes')

class Convite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe.id'), nullable=False)
    equipe = db.relationship('Equipe', backref='convites')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='convites')
    status = db.Column(db.String(20), nullable=False, default='pendente')
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

class Tartaruga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sexo = db.Column(db.String(20), nullable=False)
    nome_cientifico = db.Column(db.String(150), nullable=False)
    anilha = db.Column(db.String(100), unique=True, nullable=False)
    especie = db.Column(db.String(150), nullable=False)
    tipo_registro = db.Column(db.String(50), nullable=False)
    registros = db.relationship('RegistroTartaruga', backref='tartaruga', lazy=True)

class RegistroTartaruga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tartaruga_id = db.Column(db.Integer, db.ForeignKey('tartaruga.id'), nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    praia = db.Column(db.String(150), nullable=False)
    municipio = db.Column(db.String(150), nullable=False)
    comprimento_casco = db.Column(db.Float, nullable=False)
    largura_casco = db.Column(db.Float, nullable=False)
    quantidade_ovos = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
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

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/dashboard')
def dashboard():
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

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Deslogado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/me')
def me():
    if 'user_id' not in session:
        flash('Você precisa estar logado para ver seus dados!', 'warning')
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('login'))
    return render_template('me.html', usuario=usuario)

@app.route('/api/me', methods=['GET'])
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

@app.route('/users', methods=['GET', 'POST'])
def users():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    usuario_logado = Usuario.query.get(session['user_id'])
    if not usuario_logado.admin:
        flash('Acesso negado: Permissões de administrador são necessárias!', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user_id = request.form['user_id']
        tipo = request.form['tipo']
        admin = True if request.form.get('admin') == 'on' else False
        usuario = Usuario.query.get(user_id)
        if usuario:
            usuario.tipo = tipo
            usuario.admin = admin
            db.session.commit()
            flash(f'Permissões de {usuario.username} atualizadas com sucesso!', 'success')
    usuarios = Usuario.query.all()
    return render_template('users.html', usuarios=usuarios)

@app.route('/deletar_usuario/<int:id>', methods=['POST'])
def deletar_usuario(id):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    usuario = Usuario.query.get(id)
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('users'))
    db.session.delete(usuario)
    db.session.commit()
    flash(f'Usuário {usuario.username} foi deletado com sucesso!', 'success')
    return redirect(url_for('users'))

@app.route('/criar_equipe', methods=['GET', 'POST'])
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

@app.route('/equipes', methods=['GET', 'POST'])
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

@app.route('/ver_equipe/<int:equipe_id>')
def ver_equipe(equipe_id):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    equipe = Equipe.query.get_or_404(equipe_id)
    usuario = Usuario.query.get(session['user_id'])
    
    # Obter todos os integrantes da equipe, incluindo o líder
    integrantes = Usuario.query.join(Convite).filter(
        Convite.equipe_id == equipe_id, Convite.status == 'aceito'
    ).all()
    
    # Incluir o líder na lista de integrantes, se ainda não estiver
    if usuario.id == equipe.lider_id and usuario not in integrantes:
        integrantes.append(usuario)

    # Verificar se o usuário logado é o líder
    is_lider = usuario.id == equipe.lider_id

    return render_template('ver_equipe.html', equipe=equipe, integrantes=integrantes, is_lider=is_lider)

@app.route('/convidar_membro/<int:equipe_id>', methods=['POST'])
def convidar_membro(equipe_id):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    email = request.form['email']
    usuario = Usuario.query.filter_by(email=email).first()
    equipe = Equipe.query.get(equipe_id)
    if not usuario:
        flash('Usuário com esse email não encontrado!', 'danger')
        return redirect(url_for('ver_equipe', id=equipe.id))
    convite = Convite(equipe_id=equipe.id, usuario_id=usuario.id)
    db.session.add(convite)
    db.session.commit()
    flash(f'Convite enviado para {email} com sucesso!', 'success')
    return redirect(url_for('ver_equipe', id=equipe.id))

@app.route('/convites')
def convites():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    usuario_id = session['user_id']
    convites = Convite.query.filter_by(usuario_id=usuario_id, status='pendente').all()
    return render_template('convites.html', convites=convites)

@app.route('/responder_convite/<int:convite_id>/<acao>', methods=['POST'])
def responder_convite(convite_id, acao):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    convite = Convite.query.get(convite_id)
    if not convite or convite.usuario_id != session['user_id']:
        flash('Convite não encontrado ou acesso negado!', 'danger')
        return redirect(url_for('convites'))
    if acao == 'aceitar':
        convite.status = 'aceito'
        db.session.commit()
        flash('Você aceitou o convite para a equipe!', 'success')
    elif acao == 'rejeitar':
        convite.status = 'rejeitado'
        db.session.commit()
        flash('Você rejeitou o convite para a equipe.', 'info')
    return redirect(url_for('convites'))

@app.route('/registrar_tartaruga', methods=['GET', 'POST'])
def registrar_tartaruga():
    if request.method == 'POST':
        sexo = request.form['sexo']
        nome_cientifico = request.form['nome_cientifico']
        anilha = request.form['anilha']
        especie = request.form['especie']
        tipo_registro = request.form['tipo_registro']
        
        nova_tartaruga = Tartaruga(
            sexo=sexo,
            nome_cientifico=nome_cientifico,
            anilha=anilha,
            especie=especie,
            tipo_registro=tipo_registro
        )
        db.session.add(nova_tartaruga)
        db.session.commit()
        
        return redirect(url_for('detalhes_tartaruga', tartaruga_id=nova_tartaruga.id))
    
    return render_template('registrar_tartaruga.html')

@app.route('/detalhes_tartaruga/<int:tartaruga_id>', methods=['GET', 'POST'])
def detalhes_tartaruga(tartaruga_id):
    tartaruga = Tartaruga.query.get_or_404(tartaruga_id)
    
    if request.method == 'POST':
        estado = request.form['estado']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
        horario = datetime.strptime(request.form['horario'], '%H:%M').time()
        praia = request.form['praia']
        municipio = request.form['municipio']
        comprimento_casco = float(request.form['comprimento_casco'])
        largura_casco = float(request.form['largura_casco'])
        quantidade_ovos = int(request.form['quantidade_ovos'])
        
        novo_registro = RegistroTartaruga(
            tartaruga_id=tartaruga_id,
            estado=estado,
            data=data,
            horario=horario,
            praia=praia,
            municipio=municipio,
            comprimento_casco=comprimento_casco,
            largura_casco=largura_casco,
            quantidade_ovos=quantidade_ovos
        )
        db.session.add(novo_registro)
        db.session.commit()
        
        flash('Registro concluído com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('detalhes_tartaruga.html', tartaruga=tartaruga)
    
if __name__ == '__main__':
    app.run(debug=True)
