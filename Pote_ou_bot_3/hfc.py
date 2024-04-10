from hugchat import hugchat
from hugchat.login import Login

def query_LLM(prompt: str, new_conversation: bool = False):
        # Connexion
        huggingchat_user_email = "bringuethelios@gmail.com"
        huggingchat_user_pwd = "AlainProviste1234"

        sign = Login(email=huggingchat_user_email, passwd=huggingchat_user_pwd)
        cookies = sign.login()

        # Sauvegarde des cookies
        cookie_path_dir = "./cookies"
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

        # Créer le chatbot
        if new_conversation:
            global conversation_id, chatbot
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # ou cookie_path="usercookies/<email>.json"

            chatbot.new_conversation(switch_to=True)
            conversation_id = chatbot.new_conversation()
            
        else:
            pass

        chatbot.change_conversation(conversation_id)

        return chatbot.chat(prompt)['text']