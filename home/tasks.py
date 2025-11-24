# home/tasks.py

from django.core.mail import send_mail
from django.conf import settings

def email_cadastro(nome_usuario, email_usuario):
    
    print(f"TAREFA RECEBIDA: Enviando e-mail para {email_usuario}...")

    assunto = f"Bem-vindo(a) ao FocusUp, {nome_usuario}!"
    mensagem = (
        f"Olá, {nome_usuario}!\n\n"
        "Seu cadastro no FocusUp foi realizado com sucesso.\n\n"
        "Estamos muito felizes em ter você conosco. Comece agora a organizar suas tarefas e conquistar seus objetivos!\n\n"
        "Atenciosamente,\nA Equipe FocusUp"
    )
    remetente = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=remetente,
            recipient_list=[email_usuario],
            fail_silently=False,
        )
        print(f"SUCESSO: E-mail para {email_usuario} foi enviado.")
    except Exception as e:
        print(f"ERRO: Falha ao enviar e-mail para {email_usuario}. Erro: {e}")