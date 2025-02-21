from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from functools import wraps
import sqlalchemy.exc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Configuração do pool de conexões
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://u349037776_cascudinho:cascudinhoUI1@receitadenatal.com.br/u349037776_cascudinho')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 280,
    'pool_pre_ping': True,
    'pool_timeout': 30
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do SQLAlchemy com as novas configurações
db = SQLAlchemy(app)

# Função para reconectar ao banco
def get_db():
    if 'db' not in g:
        g.db = db.create_scoped_session()
    return g.db

@app.before_request
def before_request():
    g.db = db.session()

@app.teardown_appcontext
def teardown_db(exception=None):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Decorador para gerenciar conexões
def handle_db_connection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except sqlalchemy.exc.OperationalError as e:
            if "MySQL server has gone away" in str(e):
                db.session.rollback()
                db.session.remove()
                return f(*args, **kwargs)
            raise
    return decorated_function

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
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe.id'), nullable=False)
    registrado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    registros = db.relationship('RegistroTartaruga', backref='tartaruga', lazy=True)
    equipe = db.relationship('Equipe', backref='tartarugas')
    registrador = db.relationship('Usuario', backref='tartarugas_registradas')

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


@app.route('/')
def index():
    # Obtém estatísticas
    total_tartarugas = Tartaruga.query.count()
    total_equipes = Equipe.query.count()
    total_usuarios = Usuario.query.count()
    total_registros = RegistroTartaruga.query.count()
    
    return render_template('index.html',
                         total_tartarugas=total_tartarugas,
                         total_equipes=total_equipes,
                         total_usuarios=total_usuarios,
                         total_registros=total_registros)

@app.before_first_request
def criar_usuario_admin():
    usuario_admin = Usuario.query.filter_by(admin=True).first()
    
    if not usuario_admin:
        senha_admin = generate_password_hash('admin123', method='sha256')  
        novo_admin = Usuario(username='admin', email='admin@admin.com', senha=senha_admin, tipo='participante', admin=True)
        
        db.session.add(novo_admin)
        db.session.commit()
        
        print("Usuário administrador criado com sucesso!")

@app.route('/register', methods=['GET', 'POST'])
@handle_db_connection
def register():
    if request.method == 'POST':
        try:
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
            
            session['user_id'] = novo_usuario.id
            flash('Registrado com sucesso! Bem-vindo!', 'success')
            return redirect(url_for('pagina_inicial'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro no registro: {str(e)}")
            flash('Erro ao registrar. Tente novamente.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@handle_db_connection
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            senha = request.form.get('senha')
            
            if not email or not senha:
                flash('Por favor, preencha todos os campos.', 'danger')
                return redirect(url_for('login'))
                
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario and check_password_hash(usuario.senha, senha):
                session['user_id'] = usuario.id
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('pagina_inicial'))
            else:
                flash('Email ou senha incorretos.', 'danger')
                return redirect(url_for('login'))
                
        except Exception as e:
            app.logger.error(f"Erro no login: {str(e)}")
            flash('Erro ao fazer login. Tente novamente.', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')


@app.route('/pagina_inicial')
def pagina_inicial():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        session.clear()
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('login'))
    
    # Busca equipes que o usuário participa
    equipes_participantes = Equipe.query.join(Convite).filter(
        Convite.usuario_id == usuario.id,
        Convite.status == 'aceito'
    ).all()

    # Busca equipes que o usuário lidera
    equipes_lideradas = Equipe.query.filter_by(lider_id=usuario.id).all()
    
    # Busca convites pendentes
    convites_pendentes = Convite.query.filter_by(
        usuario_id=usuario.id,
        status='pendente'
    ).order_by(Convite.data_envio.desc()).all()
    
    return render_template('pagina_inicial.html', 
                         usuario=usuario,
                         equipes_participantes=equipes_participantes,
                         equipes_lideradas=equipes_lideradas,
                         convites_pendentes=convites_pendentes)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Deslogado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/perfil_usuario')
def perfil_usuario():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['user_id'])
    return render_template('perfil_usuario.html', usuario=usuario)

@app.route('/api/perfil_usuario', methods=['GET'])
@handle_db_connection
def api_perfil_usuario():
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
@handle_db_connection
def users():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['user_id'])
    
    if not usuario.admin:
        flash('Acesso negado: Permissões de administrador são necessárias!', 'danger')
        return render_template('users.html', usuario=usuario)
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        tipo = request.form.get('tipo')
        admin = request.form.get('admin') == 'on'
        
        try:
            usuario_alvo = Usuario.query.get(user_id)
            if usuario_alvo:
                usuario_alvo.tipo = tipo
                usuario_alvo.admin = admin
                db.session.commit()
                flash(f'Permissões de {usuario_alvo.username} atualizadas com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar permissões.', 'danger')
            app.logger.error(f"Erro ao atualizar usuário: {str(e)}")
    
    usuarios = Usuario.query.all()
    return render_template('users.html', 
                         usuarios=usuarios, 
                         usuario=usuario)

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

@app.route('/equipes', methods=['GET', 'POST'])
def equipes():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    
    if not usuario.admin:
        flash('Apenas líderes podem criar equipes!', 'danger')
        return redirect(url_for('pagina_inicial'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        equipe_existente = Equipe.query.filter_by(nome=nome).first()
        if equipe_existente:
            flash('Já existe uma equipe com esse nome!', 'danger')
            return redirect(url_for('equipes'))
        
        nova_equipe = Equipe(nome=nome, lider_id=usuario.id)
        db.session.add(nova_equipe)
        db.session.commit()
        
        novo_convite = Convite(usuario_id=usuario.id, equipe_id=nova_equipe.id, status='aceito')
        db.session.add(novo_convite)
        db.session.commit()
        
        flash(f'Equipe "{nome}" criada com sucesso!', 'success')
        return redirect(url_for('equipes'))
    
    equipes = Equipe.query.filter_by(lider_id=usuario.id).all()
    return render_template('equipes.html', equipes=equipes, usuario=usuario)


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

@app.route('/equipes/<int:equipe_id>/convidar', methods=['POST'])
def convidar_membro_equipe(equipe_id):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['user_id'])
    equipe = Equipe.query.get_or_404(equipe_id)
    
    if usuario.id != equipe.lider_id and not usuario.admin:
        flash('Apenas o líder pode convidar membros!', 'danger')
        return redirect(url_for('detalhes_equipe', id=equipe_id))
    
    email = request.form.get('email')
    if not email:
        flash('Email é obrigatório!', 'danger')
        return redirect(url_for('detalhes_equipe', id=equipe_id))
    
    membro = Usuario.query.filter_by(email=email).first()
    if not membro:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('detalhes_equipe', id=equipe_id))
    
    # Verifica se já existe convite pendente
    convite_existente = Convite.query.filter_by(
        equipe_id=equipe_id,
        usuario_id=membro.id,
        status='pendente'
    ).first()
    
    if convite_existente:
        flash('Já existe um convite pendente para este usuário!', 'warning')
        return redirect(url_for('detalhes_equipe', id=equipe_id))
    
    # Cria novo convite
    novo_convite = Convite(
        equipe_id=equipe_id,
        usuario_id=membro.id,
        status='pendente'
    )
    
    try:
        db.session.add(novo_convite)
        db.session.commit()
        flash('Convite enviado com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao enviar convite!', 'danger')
    
    return redirect(url_for('detalhes_equipe', id=equipe_id))

@app.route('/convites')
def convites():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
    usuario_id = session['user_id']
    convites = Convite.query.filter_by(usuario_id=usuario_id, status='pendente').all()
    return render_template('convites.html', convites=convites)

@app.route('/responder_convite/<int:convite_id>/<acao>', methods=['POST'])
@handle_db_connection
def responder_convite(convite_id, acao):
    if 'user_id' not in session:
        return jsonify({"error": "Não autorizado"}), 401

    try:
        convite = Convite.query.get_or_404(convite_id)
        
        # Verifica se o convite pertence ao usuário
        if convite.usuario_id != session['user_id']:
            return jsonify({"error": "Acesso negado"}), 403
            
        # Verifica se o convite ainda está pendente
        if convite.status != 'pendente':
            return jsonify({"error": "Este convite não está mais pendente"}), 400
            
        if acao not in ['aceitar', 'rejeitar']:
            return jsonify({"error": "Ação inválida"}), 400
            
        convite.status = 'aceito' if acao == 'aceitar' else 'rejeitado'
        
        db.session.commit()
        
        mensagem = 'Convite aceito com sucesso!' if acao == 'aceitar' else 'Convite rejeitado.'
        return jsonify({"message": mensagem}), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao responder convite: {str(e)}")
        return jsonify({"error": "Erro ao processar convite"}), 500

@app.route('/equipes/<int:equipe_id>/registrar_tartaruga', methods=['GET', 'POST'])
@handle_db_connection
def registrar_tartaruga(equipe_id):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['user_id'])
    equipe = Equipe.query.get_or_404(equipe_id)
    
    # Verifica se o usuário é membro da equipe
    is_membro = Convite.query.filter_by(
        equipe_id=equipe_id,
        usuario_id=usuario.id,
        status='aceito'
    ).first() or equipe.lider_id == usuario.id
    
    if not is_membro:
        flash('Você não tem permissão para registrar tartarugas nesta equipe!', 'danger')
        return redirect(url_for('pagina_inicial'))
    
    if request.method == 'POST':
        try:
            # Cria a tartaruga
            nova_tartaruga = Tartaruga(
                sexo=request.form['sexo'],
                nome_cientifico=request.form['nome_cientifico'],
                anilha=request.form['anilha'],
                especie=request.form['especie'],
                tipo_registro=request.form['tipo_registro'],
                equipe_id=equipe_id,
                registrado_por=usuario.id
            )
            
            db.session.add(nova_tartaruga)
            db.session.flush()  # Gera o ID da tartaruga
            
            # Cria o registro inicial
            registro = RegistroTartaruga(
                tartaruga_id=nova_tartaruga.id,
                estado=request.form['estado'],
                data=datetime.now().date(),
                horario=datetime.now().time(),
                praia=request.form['praia'],
                municipio=request.form['municipio'],
                comprimento_casco=float(request.form['comprimento_casco']),
                largura_casco=float(request.form['largura_casco']),
                quantidade_ovos=int(request.form['quantidade_ovos'])
            )
            
            db.session.add(registro)
            db.session.commit()
            
            flash('Tartaruga registrada com sucesso!', 'success')
            return redirect(url_for('detalhes_tartaruga', equipe_id=equipe_id, tartaruga_id=nova_tartaruga.id))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao registrar tartaruga: {str(e)}")
            flash('Erro ao registrar tartaruga. Tente novamente.', 'danger')
            
    return render_template('registrar_tartaruga.html', equipe=equipe, usuario=usuario)

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
        return redirect(url_for('pagina_inicial'))
    
    return render_template('detalhes_tartaruga.html', tartaruga=tartaruga)

@app.route('/alterar_senha', methods=['GET', 'POST'])
@handle_db_connection
def alterar_senha():
    if 'user_id' not in session:
        flash('Você precisa estar logado para alterar a senha!', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        session.clear()
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not check_password_hash(usuario.senha, senha_atual):
            flash('Senha atual incorreta!', 'danger')
            return redirect(url_for('alterar_senha'))
            
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem!', 'danger')
            return redirect(url_for('alterar_senha'))
            
        try:
            usuario.senha = generate_password_hash(nova_senha)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('perfil_usuario'))
        except:
            db.session.rollback()
            flash('Erro ao alterar senha. Tente novamente.', 'danger')
            return redirect(url_for('alterar_senha'))
            
    return render_template('alterar_senha.html', usuario=usuario)

@app.route('/atualizar_perfil', methods=['POST'])
@handle_db_connection
def atualizar_perfil():
    if 'user_id' not in session:
        flash('Você precisa estar logado!', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('login'))
        
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        
        # Verifica se email já existe para outro usuário
        usuario_existente = Usuario.query.filter(
            Usuario.email == email,
            Usuario.id != usuario.id
        ).first()
        
        if usuario_existente:
            flash('Este email já está em uso!', 'danger')
            return redirect(url_for('perfil_usuario'))
            
        usuario.username = username
        usuario.email = email
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar perfil. Tente novamente.', 'danger')
        
    return redirect(url_for('perfil_usuario'))

@app.route('/check_availability')
def check_availability():
    field = request.args.get('field')
    value = request.args.get('value')
    user_id = session.get('user_id')
    
    if not field or not value:
        return jsonify({'available': False})
    
    # Verifica se o valor já existe para outro usuário
    query = Usuario.query.filter(
        getattr(Usuario, field) == value,
        Usuario.id != user_id
    ).first()
    
    return jsonify({'available': not bool(query)})

@app.route('/api/equipes', methods=['GET'])
@handle_db_connection
def get_equipes():
    if 'user_id' not in session:
        return jsonify({"error": "Não autorizado"}), 401
        
    usuario = Usuario.query.get(session['user_id'])
    
    # Busca equipes que o usuário lidera
    equipes_lider = Equipe.query.filter_by(lider_id=usuario.id).all()
    
    # Busca equipes que o usuário participa
    equipes_membro = Equipe.query.join(Convite).filter(
        Convite.usuario_id == usuario.id,
        Convite.status == 'aceito'
    ).all()
    
    # Combina as equipes sem duplicatas
    todas_equipes = list(set(equipes_lider + equipes_membro))
    
    return jsonify([{
        'id': equipe.id,
        'nome': equipe.nome,
        'lider': equipe.lider.username,
        'membros': [convite.usuario.username for convite in equipe.convites if convite.status == 'aceito']
    } for equipe in todas_equipes])

@app.route('/api/equipes', methods=['POST'])
@handle_db_connection
def criar_equipe():
    if 'user_id' not in session:
        return jsonify({"error": "Não autorizado"}), 401
        
    usuario = Usuario.query.get(session['user_id'])
    if not usuario.admin:
        return jsonify({"error": "Apenas administradores podem criar equipes"}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
            
        nome = data.get('nome')
        if not nome:
            return jsonify({"error": "Nome da equipe é obrigatório"}), 400
            
        if Equipe.query.filter_by(nome=nome).first():
            return jsonify({"error": "Já existe uma equipe com este nome"}), 400
        
        nova_equipe = Equipe(nome=nome, lider_id=usuario.id)
        db.session.add(nova_equipe)
        db.session.flush()  # Para obter o ID da equipe
        
        # Adiciona o líder como membro automaticamente
        novo_convite = Convite(
            equipe_id=nova_equipe.id,
            usuario_id=usuario.id,
            status='aceito'
        )
        db.session.add(novo_convite)
        
        db.session.commit()
        return jsonify({
            "message": "Equipe criada com sucesso",
            "id": nova_equipe.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao criar equipe: {str(e)}")
        return jsonify({"error": "Erro ao criar equipe"}), 500

@app.route('/api/equipes/<int:id>', methods=['DELETE'])
@handle_db_connection
def deletar_equipe(id):
    if 'user_id' not in session:
        return jsonify({"error": "Não autorizado"}), 401
        
    usuario = Usuario.query.get(session['user_id'])
    equipe = Equipe.query.get_or_404(id)
    
    if equipe.lider_id != usuario.id and not usuario.admin:
        return jsonify({"error": "Apenas o líder ou admin pode deletar a equipe"}), 403
    
    try:
        # Primeiro remove todos os convites associados à equipe
        Convite.query.filter_by(equipe_id=id).delete()
        
        # Depois remove a equipe
        db.session.delete(equipe)
        db.session.commit()
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao deletar equipe: {str(e)}")
        return jsonify({"error": "Erro ao deletar equipe"}), 500

@app.route('/equipes/<int:id>')
def detalhes_equipe(id):
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro!', 'warning')
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['user_id'])
    equipe = Equipe.query.get_or_404(id)
    
    # Busca todos os membros ativos da equipe
    membros = Usuario.query.join(Convite).filter(
        Convite.equipe_id == id,
        Convite.status == 'aceito'
    ).all()
    
    # Adiciona o líder se ele não estiver na lista
    if equipe.lider not in membros:
        membros.append(equipe.lider)
    
    # Busca convites pendentes
    convites_pendentes = Convite.query.filter_by(
        equipe_id=id,
        status='pendente'
    ).order_by(Convite.data_envio.desc()).all()
    
    return render_template('detalhes_equipe.html', 
                         equipe=equipe, 
                         membros=membros,
                         convites_pendentes=convites_pendentes,
                         usuario=usuario)

@app.route('/api/equipes/<int:equipe_id>/membros/<int:membro_id>', methods=['DELETE'])
def remover_membro(equipe_id, membro_id):
    if 'user_id' not in session:
        return jsonify({"error": "Não autorizado"}), 401
        
    usuario = Usuario.query.get(session['user_id'])
    equipe = Equipe.query.get_or_404(equipe_id)
    
    if usuario.id != equipe.lider_id and not usuario.admin:
        return jsonify({"error": "Apenas o líder pode remover membros"}), 403
    
    if membro_id == equipe.lider_id:
        return jsonify({"error": "Não é possível remover o líder da equipe"}), 400
    
    try:
        Convite.query.filter_by(
            equipe_id=equipe_id,
            usuario_id=membro_id
        ).delete()
        
        db.session.commit()
        return '', 204
    except:
        db.session.rollback()
        return jsonify({"error": "Erro ao remover membro"}), 500

@app.route('/api/equipes/<int:equipe_id>/convites/<int:convite_id>', methods=['DELETE'])
def cancelar_convite(equipe_id, convite_id):
    if 'user_id' not in session:
        return jsonify({"error": "Não autorizado"}), 401
        
    usuario = Usuario.query.get(session['user_id'])
    equipe = Equipe.query.get_or_404(equipe_id)
    
    if usuario.id != equipe.lider_id and not usuario.admin:
        return jsonify({"error": "Apenas o líder pode cancelar convites"}), 403
    
    try:
        convite = Convite.query.get_or_404(convite_id)
        if convite.equipe_id != equipe_id:
            return jsonify({"error": "Convite não pertence a esta equipe"}), 400
            
        db.session.delete(convite)
        db.session.commit()
        return '', 204
    except:
        db.session.rollback()
        return jsonify({"error": "Erro ao cancelar convite"}), 500

@app.route('/api/contributors/stats')
def get_contributor_stats():
    """
    Retorna estatísticas dos contribuidores do sistema
    """
    try:
        # Busca todos os usuários e suas estatísticas
        stats = db.session.query(
            Usuario.username,
            db.func.count(Tartaruga.id).label('registros')
        ).outerjoin(
            Tartaruga, 
            Tartaruga.registrado_por == Usuario.id
        ).group_by(
            Usuario.id
        ).all()
        
        return jsonify([{
            'username': stat.username,
            'registros': stat.registros
        } for stat in stats])
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({"error": "Erro ao buscar estatísticas"}), 500

if __name__ == '__main__':
    app.run(debug=True)
