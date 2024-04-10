from flask import Flask, request, redirect, url_for, session, render_template
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete'

# Création d'une liste pour stocker les messages
messages = []

# Liste des rôles possibles
ROLES = ["devineur", "humain", "IA"]

# Trop difficile d'empêcher que plusieurs utilisateurs prennent le même pseudo parce que :
# 1 - On veut que le site fasse des conversations "jetables", genre il sauvegarde rien.
# 2 - En même temps que ça, garder en mémoire les sessions actives c'est trop difficile.
# Donc on le fait pas.

# MESSAGE IMPORTANT POUR SAISIR LE CODE
# Chaque utilisateur contacte l'autre pour chatter.
# Ce qui est difficile c'est le référentiel à utiliser. 
# Chacun est à la fois :
# 1 - Un user pour soi
# 2 - Un contact du point de vue de l'autre
# Il faut, dans le code, réussir à séparer le tout en ayant conscience de ça.
# Le premier qui accède au chat sera devineur et doit donner l'information qu'il a déjà
# accédé au chat pour l'autre ordinateur.
# On est obligé de ne pas faire de distinction user/contact pour le rôle et de vérifier à chaque fois
# la valeur de rôle dans la session.

@app.route('/')
def index():
    global messages
    # Réinitialisation
    messages = []
    session.clear()

    return render_template('index.html')



@app.route('/recup_user', methods=['POST'])
def recup_user():
    username = request.form.get('username')
    session['username'] = username
    return redirect(url_for('enter_contact'))


@app.route('/enter_contact')
def enter_contact():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))
    
    return render_template('enter_contact.html', username=session['username'])



@app.route('/save_ordre_arrivee', methods=['POST'])
def save_ordre_arrivee():
    # Récupérer la position d'arrivée
    pos = request.form.get('pos')
    if "role" not in session:
        session["pos"] = pos

    # Attribution des rôles
    if session["pos"] == 1:
        role = ROLES[0] # devineur
        session["role"] = role
    else:
        role = random.choice(["humain", "IA"])
        session["role"] = role



# ON FAIT UN PREMIER COUP DE REQUETE POST POUR CAPTER LE CONTACT ET ON L'ENREGISTRE
# UNE FOIS QU'ON A TOUT PRÊT ON LANCE A NOUVEAU LE CHAT EN GET
# CETTE MANOEUVRE (POST PUIS GET) EST REALISEE PAR LES DEUX ORDINATEURS 
# POUR CAPTER RECIPROQUEMENT LE CONTACT
@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))

    if request.method == 'POST':
        contact_username = request.form.get('contact_username')
        session['contact_username'] = contact_username
        return redirect(url_for('chat'))

    # Définir la clé rôle
    if 'role' not in session:
        session['role'] = None

    return render_template('chat.html', 
                           username=session['username'], 
                           contact_username=session.get('contact_username')
                           )

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
