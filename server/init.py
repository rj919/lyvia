__author__ = 'rcj1492'
__created__ = '2018.04'

# construct postgres url
from labpack.records.id import labID
from jsonmodel.validators import jsonModel
from labpack.records.settings import load_settings
postgres_config = load_settings('../cred/aws-postgres.yaml')
postgres_url = 'postgres://%s:%s@%s:%s/%s' % (
    postgres_config['aws_postgres_username'],
    postgres_config['aws_postgres_password'],
    postgres_config['aws_postgres_hostname'],
    postgres_config['aws_postgres_port'],
    postgres_config['aws_postgres_dbname']
)

# construct object map
object_map = {
    'users': load_settings('models/users.json'),
    'telemetry': load_settings('models/telemetry.json')
}

# construct sql tables
from labpack.databases.sql import sqlClient
sql_tables = {}
for key, value in object_map.items():
    table_name = key.replace('-','_')
    sql_kwargs = {
        'table_name': table_name,
        'database_url': 'sqlite:///../data/records.db',
        'record_schema': value
    }
    sql_tables[table_name] = sqlClient(**sql_kwargs)

# construct data object models
api_model = load_settings('models/api.json')
telemetry_model = jsonModel(load_settings('models/telemetry-post.json'))

# construct email client
from labpack.email.mailgun import mailgunClient
from labpack.handlers.requests import handle_requests
mailgun_cred = load_settings('../cred/mailgun.yaml')
mailgun_kwargs = {
    'api_key': mailgun_cred['mailgun_api_key'],
    'email_key': mailgun_cred['mailgun_email_key'],
    'account_domain': mailgun_cred['mailgun_spf_route'],
    'requests_handler': handle_requests
}
email_client = mailgunClient(**mailgun_kwargs)

if __name__ == "__main__":
    
    charlotte = load_settings('../data/users/zPpgsPmGSVculcMmCXZ4FqFW.json')
    george = load_settings('../data/users/Gn57-gGUzJJZC38LU0jYw93I.json')
    telemetry = load_settings('../data/telemetry/Xin_4Dd826qwdDmHjYR5m5Xu.json')
    for record in sql_tables['users'].list():
        print(record)
        record['email'] = 'support@collectiveacuity.com'
        sql_tables['users'].update(record)
    
    for record in sql_tables['users'].list():
        print(record)