# 🐢 **Projeto Casco** 🐢

Bem-vindo ao **Casco**, uma plataforma web dedicada à **conservação de tartarugas marinhas**! Este sistema foi desenvolvido para facilitar o gerenciamento dos dados relacionados às tartarugas, seus registros e equipes envolvidas na pesquisa e conservação. O objetivo é auxiliar pesquisadores e voluntários da **Associação de Proteção e Conservação Ambiental Cabo de São Roque** a organizarem suas atividades e registros.

---

## 🚀 **Como Começar** 

Para rodar o projeto localmente, siga os passos abaixo:

### **Pré-requisitos:**

- Python 3.8+  
- MySQL (ou qualquer banco de dados compatível com SQLAlchemy)
- Bibliotecas do Python:
  ```bash
  pip install -r requirements.txt
Rodando a Aplicação:
Clone o repositório:

bash
Copiar código
git clone https://github.com/seu-usuario/casco.git
cd casco
Configure o banco de dados:

Configure sua variável de ambiente DATABASE_URL no arquivo .env, ou edite diretamente no código a URL de conexão com o banco.
Crie as tabelas do banco de dados:

bash
Copiar código
python app.py
Execute o servidor:

bash
Copiar código
python app.py
Agora, acesse o http://localhost:5000 para ver o projeto em ação!

🌟 Funcionalidades
Gestão de Usuários
Cadastro e login de usuários com controle de senhas seguras.
Administração: Criação de usuários administradores e controle de permissões.
Equipes e Convites
Criação de equipes e gestão de convites para membros.
Aceitação ou rejeição de convites para equipes, com notificação de status.
Registros de Tartarugas
Cadastro de tartarugas com informações detalhadas, como espécie, nome científico e tipo de registro.
Registros de observações com dados sobre o estado da tartaruga, praia, município, e dados de ovos.
🧑‍💻 Tecnologias Usadas
Flask: Framework web utilizado para desenvolvimento da aplicação.
SQLAlchemy: ORM utilizado para interagir com o banco de dados.
MySQL: Banco de dados relacional para armazenar as informações dos usuários, equipes e tartarugas.
Werkzeug: Biblioteca para hashing de senhas.
Jinja2: Motor de templates usado para renderizar páginas HTML dinâmicas.
🔐 Segurança
A aplicação utiliza o hashing de senhas com a biblioteca werkzeug.security para garantir a segurança das senhas dos usuários. Além disso, a autenticação é feita por meio de sessões, mantendo as informações seguras enquanto o usuário navega pela plataforma.

🎨 Interface
A interface foi desenvolvida de maneira simples e intuitiva, com templates HTML que permitem a visualização de dados de maneira clara. Utilize o template base.html para reaproveitamento de código e facilidade de manutenção.

📜 Licença
Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.

📞 Contato
Se você tiver dúvidas ou sugestões sobre o projeto, entre em contato com o time de desenvolvimento ou envie um e-mail para contato@casco.

🌍 Contribua!
Este projeto é de código aberto e qualquer contribuição é bem-vinda! Se você deseja ajudar, basta fazer um fork do repositório, criar uma nova branch, e enviar um pull request.

Juntos, podemos ajudar na preservação das tartarugas marinhas!

lua
Copiar código

Este README traz uma explicação completa do seu projeto de maneira organizada, colorida e com