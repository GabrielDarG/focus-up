from django.test import TestCase
from .models.usuario import Usuario
from .models.conquista import Conquista, UsuarioConquista

class ConquistaSignalTest(TestCase):

    def setUp(self):
        """
        Cria os objetos base que serão usados em todos os testes.
        Este método roda antes de cada função de teste.
        """
        self.usuario = Usuario.objects.create_user(
            email='testuser@example.com',
            nome='Test User',
            nome_usuario='testuser',
            senha='password123'
        )
        self.conquista = Conquista.objects.create(
            nome="Primeira Conquista",
            criterio="Completar uma tarefa",
            xp_points=80
        )

    def test_ganha_xp_ao_receber_conquista(self):
        """
        Testa se o XP do usuário aumenta corretamente ao ganhar uma conquista, sem subir de nível.
        """
        self.usuario.xp_atual = 10
        self.usuario.save()

        # Ação: Atribui a conquista
        UsuarioConquista.objects.create(usuario=self.usuario, conquista=self.conquista)

        # Verificação: Recarrega o usuário e checa o XP
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.xp_atual, 90) # 10 (inicial) + 80 (conquista) = 90
        self.assertEqual(self.usuario.nivel, 1) 

    def test_sobe_de_nivel_ao_receber_conquista(self):
        """
        Testa se o usuário sobe de nível e se o XP é calculado corretamente.
        """
        # Condição inicial: Usuário está perto de subir de nível (Nível 1, precisa de 100 XP)
        self.usuario.xp_atual = 50
        self.usuario.save()

        # Ação: Atribui a conquista de 80 XP. Total deveria ser 130 XP.
        UsuarioConquista.objects.create(usuario=self.usuario, conquista=self.conquista)

        # Verificação: Recarrega o usuário e checa o nível e o XP restante
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nivel, 2) # Deve subir para o nível 2
        self.assertEqual(self.usuario.xp_atual, 30) # 130 - 100 (para subir de nível) = 30 XP restantes