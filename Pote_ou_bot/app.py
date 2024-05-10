from flask import Flask, request, redirect, url_for, session, render_template
import random
from flask import jsonify
import hfc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc123'

# Création d'une liste pour stocker les messages
messages = []

# Liste des rôles possibles
ROLES = ["devineur", "pote", "bot"]

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
# la valeur de role dans la session.

@app.route('/')
def index():
    global messages
    # Réinitialisation
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




# On fait un premier coup de requete post pour capter le contact et on l'enregistre.
# Une fois qu'on a tout prêt on lance a nouveau le chat en get.
# Cette manoeuvre (post puis get) est realisée par les deux ordinateurs pour capter reciproquement le contact.
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



@app.route('/save_ordre_arrivee', methods=['POST'])
def save_ordre_arrivee():
    pos = int(request.form.get('pos'))
    if "pos" not in session:
        session["pos"] = pos

    if session["pos"] == 1:
        role = ROLES[0] # devineur
        session["role"] = role
    else:
        role = random.choice(["pote", "bot"])
        session["role"] = role

    return role

# Incrementer une variable à chaque appel d'une fonction javascript n'est pas fiable car les piles d'appel sont trop
# importantes pour être sûr d'éviter une double incrémentation.
# Concrètement il n'y a que un message dans le chat mais il y aura peut-être eu 5 appels à messageFlow pour ce message.
# Donc la variable fiable est len(messages). Il faut faire une fonction qui renvoie simplement len(messages).

@app.route('/get_len_messages', methods=['POST'])
def get_len_messages():
    if messages:
        return {'len': len(messages)}
    else:
        return 0
    
def get_last_message():
    if messages:
        return (messages[-1], len(messages))
    else:
        return ({'author': "", 'content': ""}, 0)

@app.route('/check_new_messages', methods=['POST'])
def check_new_messages():
    if 'last_message' not in session:
        session['last_message'] = get_last_message()

    # Récupère le dernier message
    new_last_message = get_last_message()

    # Si nouveau message de l'autre
    if (session['last_message'] != new_last_message) and (new_last_message[0]['author'] not in (session['username'], "Système")):
        session['last_message'] = new_last_message
        return jsonify({'newMessagesReceived': True})
    else:
        return jsonify({'newMessagesReceived': False})

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))
    message = request.form.get('message')
    if message:
        if message == "LE_MESSAGE_DU_BOT":
            if "preparation_ia" not in session:
                hfc.query_LLM('''Dans cette discussion tu feras comme si on était dans une discussion SMS et que on écrivait mal. 
                              Tu as un vocabulaire très peu développé. Enlève les apostrophes, les points de fin de phrase et les accents. Ecris des 
                              messages courts et négligés.''', True)
                session["preparation_ia"] = True
            mess_devineur = get_last_message()
            prompt = mess_devineur[0]['content']
            reponse_IA = hfc.query_LLM(prompt, False)
            messages.append({'author': session['username'], 'content': reponse_IA})
        elif message == "LE_MESSAGE_DU_SYSTEME":
            messages.append({'author': "Système", 'content': "Envoyez BOT si vous pensez avoir parlé à un bot ou POTE si vous pensez avoir parlé à votre pote."})
        elif message == "REVELATION_ROLE":
            messages.append({'author': session['username'], 'content': session['role']})
        else:
            messages.append({'author': session['username'], 'content': message})
    return 'OK'




@app.route('/get_messages')
def get_messages():
    if 'username' not in session: # Si quelqu'un a voulu brûler les étapes sans mettre de username
        return redirect(url_for('index'))
    return {'messages': messages}




if __name__ == "__main__":
    app.run(debug=True)
