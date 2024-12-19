from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Tartaruga, RegistroTartaruga, db
from datetime import datetime

tartaruga = Blueprint('tartaruga', __name__)

@tartaruga.route('/registrar_tartaruga', methods=['GET', 'POST'])
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

@tartaruga.route('/detalhes_tartaruga/<int:tartaruga_id>', methods=['GET', 'POST'])
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
