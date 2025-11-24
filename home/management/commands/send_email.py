from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Envia um e-mail de teste para o endereço especificado.'

    def add_arguments(self, parser):
        parser.add_argument('email_destinatario', type=str, help='O e-mail para o qual a mensagem será enviada.')

    def handle(self, *args, **options):
        destinatario = options['email_destinatario']

        self.stdout.write(f'Preparando para enviar e-mail para {destinatario}...')

        assunto = "Teste de Notificação"
        mensagem = "Olá! Este é um e-mail de teste enviado a partir de um comando do Django."
        remetente = settings.EMAIL_HOST_USER

        try:
            send_mail(
                subject=assunto,
                message=mensagem,
                from_email=remetente,
                recipient_list=[destinatario],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'E-mail enviado com sucesso para {destinatario}!'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Falha ao enviar e-mail: {e}'))