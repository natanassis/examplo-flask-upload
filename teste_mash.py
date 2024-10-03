from marshmallow import Schema,fields,ValidationError

data ={'pasta': 'proc - 21514',
    'nome': 'Teste Ged 18_09 2',
    'responsavel': 'Natan', 
    'id_tarefa':0, 
    'id_relacionamento':0,
    'tp_relacionamento': 'exemplo-ged',
    'descricao': 'teste para verificar serealizacao',
    'filename': 'Custas_18_09.txt'}

def validate_int_or_default_one(value):
    if (value is None)  or (value == "") or (value == 0):
        return 100
    if not isinstance(value, int):
        raise ValidationError("O valor deve ser um inteiro, None ou NaN.")
    return value

class SalveFileSchema(Schema):
    
    pasta = fields.Str(required=True)
    
    nome = fields.Str(required=True)
    
    responsavel = fields.Str(required=True)
    
    id_tarefa = fields.Int(validate=validate_int_or_default_one,allow_none=True)
    
    id_relacionamento = fields.Int(validate=validate_int_or_default_one,allow_none=True)

    tp_relacionamento = fields.Str()
    
    descricao = fields.Str(required=True)
    
    filename = fields.Str(required=True)
    

schema = SalveFileSchema()
result  = schema.load(data)
print(result)
