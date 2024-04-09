from flask import Flask, request, redirect, url_for, session, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete'

# Création d'une liste pour stocker les messages
messages = []

# Trop difficile d'empêcher que plusieurs utilisateurs prennent le même pseudo parce que :
# 1 - On veut que le site fasse des conversations "jetables", genre il sauvegarde rien.
# 2 - En même temps que ça, garder en mémoire les sessions actives c'est trop dur.
# Donc on le fait pas.

@app.route('/')
def index():
    global messages
    # Réinitialisation
    messages = []
    session.clear()
    return render_template('index.html')

@app.route('/user_contact', methods=['POST'])
def user_contact():
    session['username'] = request.form['username']
    return redirect(url_for('enter_contact'))

@app.route('/enter_contact')
def enter_contact():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))
    return render_template('user_contact.html', username=session['username'])

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))

    if request.method == 'POST':
        contact_username = request.form.get('contact_username')
        session['contact_username'] = contact_username
        return redirect(url_for('chat'))

    return render_template('chat.html', username=session['username'], contact_username=session.get('contact_username'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))
    message = request.form.get('message')
    if message:
        messages.append({'author': session['username'], 'content': message})
    return 'OK'

@app.route('/get_messages')
def get_messages():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))
    return {'messages': messages}

if __name__ == "__main__":
    app.run(debug=True)
