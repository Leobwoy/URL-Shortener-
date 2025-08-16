from app import create_app, db
from app.models import URL

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell."""
    return {
        'db': db,
        'URL': URL
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
