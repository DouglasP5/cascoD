from app import db

# Primeiro fazemos backup do banco atual
# Depois executamos as alterações

def update_database():
    try:
        # Adiciona as novas colunas na tabela tartaruga
        db.engine.execute('''
            ALTER TABLE tartaruga 
            ADD COLUMN equipe_id INTEGER,
            ADD COLUMN registrado_por INTEGER,
            ADD COLUMN data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            ADD CONSTRAINT fk_tartaruga_equipe 
                FOREIGN KEY (equipe_id) REFERENCES equipe(id),
            ADD CONSTRAINT fk_tartaruga_usuario 
                FOREIGN KEY (registrado_por) REFERENCES usuario(id)
        ''')
        
        # Adiciona as novas colunas na tabela registro_tartaruga
        db.engine.execute('''
            ALTER TABLE registro_tartaruga
            MODIFY COLUMN data DATE NOT NULL,
            MODIFY COLUMN horario TIME NOT NULL,
            MODIFY COLUMN comprimento_casco FLOAT NOT NULL,
            MODIFY COLUMN largura_casco FLOAT NOT NULL,
            MODIFY COLUMN quantidade_ovos INTEGER NOT NULL
        ''')
        
        print("Banco de dados atualizado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao atualizar banco de dados: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    update_database() 