from flask import Flask, request, redirect, url_for, session, render_template
from random import choice

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete'

# Liste des rôles possibles
ROLES = ["devineur", "humain", "IA"]

# Initialisation des variables globales
CONVERSATIONS = {}

@app.route('/')
def index():
    global CONVERSATIONS
    # Réinitialisation
    CONVERSATIONS = {}
    session.clear()

    return render_template('index.html')

@app.route('/user_contact', methods=['POST'])
def user_contact():
    username = request.form.get('username')
    session['username'] = username
    return redirect(url_for('enter_contact'))

@app.route('/enter_contact')
def enter_contact():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('user_contact.html', username=session['username'])


@app.route('/start_chat', methods=['POST'])
def start_chat():
    contact_username = request.form.get('contact_username')
    session['contact_username'] = contact_username

    # Le premier joueur est toujours le devineur
    player_role = "devineur"
    other_role = choice(["IA", "humain"])

    # Sauvegarde des rôles dans la session
    session['player_role'] = player_role
    session['other_role'] = other_role

    # Initialisation de la conversation
    CONVERSATIONS[session['username']] = {
        'role': player_role,
        'messages': []
    }
    CONVERSATIONS[session['contact_username']] = {
        'role': other_role,
        'messages': []
    }

    return redirect(url_for('chat'))


@app.route('/chat')
def chat():
    if 'username' not in session or 'contact_username' not in session:
        return redirect(url_for('index'))

    return render_template('chat.html',
                           username=session['username'],
                           contact_username=session['contact_username'],
                           player_role=session['player_role'])

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session or 'contact_username' not in session:
        return redirect(url_for('index'))

    message = request.form.get('message')
    if message.strip():
        sender = session['username']
        receiver = session['contact_username']
        CONVERSATIONS[sender]['messages'].append({'sender': sender, 'message': message})
        CONVERSATIONS[receiver]['messages'].append({'sender': sender, 'message': message})

    return redirect(url_for('chat'))

@app.route('/get_messages', methods=['POST', 'GET'])
def get_messages():
    if 'username' not in session or 'contact_username' not in session:
        return redirect(url_for('index'))

    sender = session['username']
    receiver = session['contact_username']
    return {'messages': CONVERSATIONS[receiver]['messages']}

if __name__ == "__main__":
    app.run(debug=True)
