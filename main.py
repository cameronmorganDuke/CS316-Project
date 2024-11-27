from website import create_app
import os

app = create_app()

if __name__ == '__main__':
    if os.environ["FLASK_ENVIRONMENT"]=="production":    
        app.run(host="0.0.0.0", port=8000)
    else:
        app.run(debug=True)

