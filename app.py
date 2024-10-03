from flask import Flask,render_template,jsonify,request,make_response,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from celery import Celery
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta,timezone
import secrets
import string
from uuid import uuid4
import os
from pathlib import Path
import shutil

from config import Config


setup = Config()
#cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
app = Flask(__name__)
app.config.from_mapping(setup.config)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in setup.ALLOWED_EXTENSIONS


def gerar_id_unico():
        """Gera um ID único com o tamanho especificado.

        Args:
            tamanho: O número de caracteres do ID.

        Returns:
            str: O ID único gerado.
        """
        caracteres = string.ascii_letters + string.digits
        id_unico = ''.join(secrets.choice(caracteres) for _ in range(10))
        return str(id_unico)



class Ged(db.Model):
    
    __tablename__ = 'tbl_api_files_tools'
    
    id = db.Column(db.String(), primary_key=True,default=str(uuid4()))
    pasta = db.Column(db.String(255), nullable=False)
    npj = db.Column(db.String(255),nullable=False)
    cnj = db.Column(db.String(255),nullable=False)
    file_name = db.Column(db.Text)
    _file_ = db.Column(db.Text,unique=True)
    id_download = db.Column(db.Text,unique=True)
    link_download = db.Column(db.Text)
    data_cricao = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return '<INFO {}>'.format(self.pasta)

    @classmethod
    def get_title_post(cls,id_download):
        return cls.query.filter_by(id_download=id_download).first()
    
    def to_json(self):
        to_dict = {  
            "pasta":self.pasta,
            "cnj":self.cnj,
            "npj":self.npj,
            "info_file":{
                "filename" : self.file_name,
                "id_download":self.id_download,
                "link_download":self.link_download,
                "_file_":self._file_
            },
        "status" : "success" }
        return to_dict
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    
def renomear_arquivo(caminho_antigo, novo_nome):
    try:
        os.rename(caminho_antigo, novo_nome)
        print("Arquivo renomeado com sucesso!")
    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except OSError as err:
        print(f"Ocorreu um erro ao renomear o arquivo: {err}")

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    @classmethod
    def get_title_post(cls,title):
        return cls.query.filter_by(title=title).first()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()

@app.route('/posts',methods=['GET'])
def index():
    posts = Post.query.all()
    lista_de_posts = []
    for post in posts:
        post_atual = {
            'id': post.id,
            'publicacao':{
                'title': post.title,
                'body': post.body,
                'timestamp': post.timestamp
            }   
        }
        
        lista_de_posts.append(post_atual)
            
    return jsonify({'posts':lista_de_posts},200)
    
@app.route('/post',methods=['POST'])
def create_post():
    data = request.json
    
    title = data.get('title')
    body = data.get('body')
    #if request.method == 'POST':
    consulta_title = Post.get_title_post(title=title)
    
    if consulta_title is not None:
        return jsonify({'error':"User already exists"}), 409
    
    new_post = Post(
        title = title,
        body = body
        )
    new_post.save()
            
    return make_response(
            {'message': "Post created"},
            201
        )

@app.route('/list-all',methods=['GET'])
def list_all():
    
    arquivos = Ged.query.order_by(Ged.data_cricao).all()
    
    return jsonify([arquivo.to_json() for arquivo in arquivos])


@app.route('/file/<string:id>',methods=['DELETE'])
def get_file(id):

    #file_id = request.args.get('id')
    #print("file_id: ",file_id)
    try:
        arquivo = Ged.get_title_post(id_download=id)
        if not arquivo:
            return jsonify({'mensagem':'Credencial not exist'},401)
        
        file = Ged(
            id_download= id
        )
        status = file.delete()
        if status:
            return jsonify({'message':"sucessfully deleted"},201)
    except Exception as e:
        return jsonify({'message':f"{e}"})

@app.route('/file/salve', methods=['GET', 'POST']) 
def info_file():
    try:
        data = request.get_json()
        _pasta = data['pasta']
        _titulo = data['npj']
        _cnj = data['cnj']
        _filename = data['filename']
        
        raiz, extensao = os.path.splitext(_filename)
        
        novo_file_name_unique = str(uuid4())+extensao
        print(novo_file_name_unique)

            
        # Caminho completo do arquivo antigo e novo
        pasta = f"{Path(os.getcwd()) / 'uploads'}"
        arquivo_antigo = _filename
        novo_nome = novo_file_name_unique

        caminho_antigo = os.path.join(pasta, arquivo_antigo)
        caminho_novo = os.path.join(pasta, novo_nome)

        
        
        #path_filename_original = f"{Path(os.getcwd()) / 'uploads' / _filename}" 
        os.rename(caminho_antigo, caminho_novo)
            
            

        unique_id_download = gerar_id_unico()
        
        info = f"/tools/operations/download?id={unique_id_download}"
                                
        new_ged = Ged(
            pasta =_pasta,
            cnj= _cnj,
            npj=_titulo,
            file_name = _filename,
            _file_ =novo_file_name_unique,
            id_download = unique_id_download,
            link_download = info
            )
            
        new_ged.save()
        
        renomear_arquivo(caminho_antigo, caminho_novo)
        
        #path_filename_original = f"{Path(os.getcwd())  / novo_file_name_unique}" 
        #path_filename_original_uplods = f"{Path(os.getcwd()) / 'uploads' / novo_file_name_unique}" 
        #shutil.move(path_filename_original,path_filename_original_uplods)
        
        return jsonify({  
                        "pasta":_pasta,
                        "cnj":_cnj,
                        "npj":_titulo,
                        "info_file":{
                            "filename" : _filename,
                            "id_download":unique_id_download,
                            "link_download":info,
                            "_file_":novo_file_name_unique
                        },
                        "status" : "success" },200)
    except Exception as error:
        
        return jsonify({ 'message' : error }, 401)  

@app.route('/upload', methods=['GET', 'POST']) 
def upload_arquivo(): 
    
    # Obter dados do JSON
    try:
        if request.method == 'POST' : 
            file = request.files.getlist( 'files' ) 
            filename = "" 
            print (request.files, "...." ) 
            for f in file: 
                print (f.filename) 
                
                filename = secure_filename(f.filename) 
                print (allowed_file(filename)) 
                if allowed_file(filename): 
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
                else : 
                    return jsonify({ 'message' : 'Tipo de arquivo não permitido' },400)
            return jsonify({ "name" : filename, "status" : "success" },200) 
        else :
            return jsonify({ "status" : "Carregar solicitação GET da API em execução" })
    except Exception as e :
        print(e)
        return jsonify({ 'message' : f'{e}' }, 404) 


@app.route('/download')
def download_file():
    """
    Esta função é responsável por baixar um arquivo baseado no ID fornecido.

    1. Obtém o ID do arquivo a partir dos parâmetros da requisição.
    2. Busca o arquivo no banco de dados usando o ID.
    3. Se o arquivo for encontrado, baixa o arquivo do armazenamento em nuvem (Azure Blob Storage).
    4. Retorna o arquivo para o cliente.
    5. Caso contrário, retorna uma mensagem de erro indicando que o arquivo não foi encontrado.
    """
    try:
        file_id = request.args.get('id')
        print("file_id: ",file_id)
        # Lógica para encontrar o arquivo baseado no ID
        # ... (Exemplo simplificado)
        #file_path = f'arquivos/{file_id}.pdf'  # Substitua por sua lógica real
        arquivo = Ged.get_title_post(id_download=file_id)
        
        if arquivo:
            # Logica do Azure Blob aqui
            _file_name = arquivo.file_name 
            print(f"Nome atual: {arquivo._file_}")
            print(f"Nome original: {arquivo.file_name}")
            print()
            
            raiz, extensao = os.path.splitext(arquivo._file_)
            nome_arquivo_orginal = arquivo.file_name 
            
            # caminho do arquivo com nome atual
            path_filename_atual = f"{Path(os.getcwd()) / 'uploads' / str(arquivo._file_)}" 
            
            # caminho do arquivo com nome atual
            path_file_original = f"{Path(os.getcwd()) / 'uploads' / str(arquivo._file_)}" 
            
            #caminho do arquivo com novo nome
            path_filename_original = f"{Path(os.getcwd()) / 'uploads' / str(nome_arquivo_orginal)}" 
            try:
                if os.path.exists(path_filename_atual):
                    print("O arquivo existe!")
                    
                    # renomia o arquivo para o nome original
                    os.rename(path_file_original, path_filename_original)
                    
                    print("Arquivo renomeado com sucesso!")

                    # caminho do arquivo que via ser copiado
                    path_filename_destino = f"{Path(os.getcwd()) / 'uploads' / str(arquivo._file_)}"
                    
                    # copia e renomea o arquivo com o nome com id_unico
                    shutil.copy2(path_filename_original, path_filename_destino)
                    #download_blob_ = blob.download_blob_storage(_file_name)
                    
                    #if download_blob_:
                    # envia o arquivo com o nome original
                    
                    # Configurando o cache para 1 hora
                    expires = datetime.now(timezone.utc) + timedelta(hours=1)
                    response =  send_from_directory(app.config['UPLOAD_FOLDER'],_file_name, as_attachment=True)
                    response.headers['Cache-Control'] = 'public, max-age=3600'
                    response.headers['Expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
                    return response
                
                else:
                    print("O arquivo não existe.")
                    return jsonify({ 'message' : f'file not found' }, 401) 
            except OSError as error:
                print(f"Erro ao renomear o arquivo: {error}")
            
                
        else:
            return jsonify({ 'message' : f'file not found' }, 401)  
    except Exception as e:
        print(e)
        return jsonify({ 'message' : f'{e}' }, 404)  
        


if __name__ == "__main__":
    app.run(debug=True)