# run.py
from app import create_app, db
from app.models import User
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
     return {'db': db, 'User': User}

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)