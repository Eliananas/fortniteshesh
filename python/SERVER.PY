from flask import Flask, request

app = Flask(__name__)

@app.route('/callback/')
def callback():
    # Remove the line of code that assigns the value of `request.args.get('code')` to the variable `code`
    # Vous pouvez maintenant utiliser ce code pour obtenir un token d'accès
    return "Authentification réussie, vous pouvez fermer cette fenêtre."

if __name__ == '__main__':
    app.run(port=8888)
