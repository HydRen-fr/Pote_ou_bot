from hugchat import hugchat
from hugchat.login import Login

def query_LLM(prompt: str, new_conversation: bool = False):
        # Connexion
        huggingchat_user_email = "bringuethelios@gmail.com"
        huggingchat_user_pwd = "AlainProviste1234"

        sign = Login(email=huggingchat_user_email, passwd=huggingchat_user_pwd)
        cookies = sign.login()

        # Sauvegarde des cookies
        cookie_path_dir = "./cookies/"
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

        # Créer le chatbot
        if new_conversation:
            global conversation_id, chatbot
            chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # ou cookie_path="usercookies/<email>.json"
            chatbot.delete_all_conversations()
            chatbot.switch_llm(1)
            chatbot.new_conversation(switch_to=True)
            conversation_id = chatbot.new_conversation()
            
        else:
            pass

        chatbot.change_conversation(conversation_id)

        return chatbot.chat(prompt)['text']

# Parfois besoin de relancer deux fois pour que ça marche


'''

CohereForAI/c4ai-command-r-plus
meta-llama/Meta-Llama-3-70B-Instruct LE MEILLEUR
HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1
mistralai/Mixtral-8x7B-Instruct-v0.1
NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
google/gemma-1.1-7b-it
mistralai/Mistral-7B-Instruct-v0.2
microsoft/Phi-3-mini-4k-instruct

'''
