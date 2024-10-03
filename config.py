

class Config:
    config = {
        "DEBUG": True,          # some Flask specific configs
        
        'SQLALCHEMY_DATABASE_URI':'sqlite:///blog.db',
        "UPLOAD_FOLDER" :fr'C:\Users\nata.assis\flask_exemplo_migrate\uploads',
        'CELERY_BROKER_URL' : 'amqp://localhost'
    }

    ALLOWED_EXTENSIONS = {'txt','xlsx','csv', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}    