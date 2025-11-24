# home/models/usuario.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone 
from datetime import date, time, datetime, timedelta

import logging
logger = logging.getLogger(__name__)


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, nome_usuario, senha=None, **extra_fields):
        if not email: raise ValueError("O usuário precisa de um email")
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, nome_usuario=nome_usuario, **extra_fields)
        user.set_password(senha)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nome, nome_usuario, senha=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, nome, nome_usuario, senha, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    sexo_choices =[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')]
    email = models.EmailField(primary_key=True, unique=True, verbose_name='E-mail do usuário')
    nome = models.CharField(max_length=100, verbose_name='Nome completo do usuário')
    nome_usuario = models.CharField(max_length=50, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=sexo_choices, null=True, blank=True, verbose_name='Sexo (M/F/O)')
    foco = models.CharField(max_length=50, null=True, blank=True, verbose_name='Área de foco')
    
    nivel = models.IntegerField(default=1)
    xp_atual = models.IntegerField(default=0)
    xp_proximo_nivel = models.IntegerField(default=100, verbose_name='XP para o próximo nível')
    moedas = models.IntegerField(default=0, verbose_name="Moedas de Ouro")
    
    ofensiva = models.IntegerField(null=True, blank=True, verbose_name='Poder de ataque do avatar')
    avatar = models.ImageField(upload_to='avatares/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    dias_foco = models.IntegerField(default=0, verbose_name='Dias de Foco (Streak)')
    ultimo_resgate_foco = models.DateTimeField(null=True, blank=True, verbose_name='Último Resgate de Foco')
    
    slots_tarefas_pessoais_usados = models.IntegerField(default=0, verbose_name="Slots de tarefas pessoais (Manual) usados hoje")
    slots_tarefas_ia_usados = models.IntegerField(default=0, verbose_name="Slots de tarefas (IA) usados hoje")
    data_reset_slots = models.DateField(default=date.today, verbose_name="Último dia que os slots foram resetados")
    
    tarefas_concluidas_prazo_count = models.IntegerField(default=0, verbose_name="Contador de tarefas concluídas (no prazo)")
    tarefas_concluidas_atrasadas_count = models.IntegerField(default=0, verbose_name="Contador de tarefas concluídas (atrasadas)")
    tarefas_descartadas_count = models.IntegerField(default=0, verbose_name="Contador de tarefas descartadas")
    
    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "nome_usuario"]

    XP_BASE_PARA_NIVEL_2 = 100
    XP_MULTIPLICADOR = 1.5
    LIMITE_SLOTS_PESSOAIS_BASE = 3 
    LIMITE_SLOTS_IA = 6
    HORA_CORTE_RESET = time(22, 0, 0)

    # --- Função para pegar a MOLDURA ativa (Formato) ---
    def get_moldura_ativa(self):
        from .loja import InventarioUsuario
        moldura_ativa = InventarioUsuario.objects.filter(
            usuario=self, item__tipo_efeito='MOLDURA', esta_ativo=True
        ).first()
        if moldura_ativa and moldura_ativa.item.classe_css:
            return moldura_ativa.item.classe_css
        return "moldura-padrao"

    # --- Função para pegar a COR ativa (Pintura) ---
    def get_cor_ativa(self):
        from .loja import InventarioUsuario
        cor_ativa = InventarioUsuario.objects.filter(
            usuario=self, item__tipo_efeito='COR_BORDA', esta_ativo=True
        ).first()
        if cor_ativa and cor_ativa.item.classe_css:
            return cor_ativa.item.classe_css
        return "" 

    def get_limite_tarefas_pessoais(self):
        from .loja import InventarioUsuario 
        slot_extra_inv = InventarioUsuario.objects.filter(
            usuario=self, item__tipo_efeito='SLOT_EXTRA'
        ).first()
        extras = slot_extra_inv.quantidade if slot_extra_inv else 0
        extras = min(extras, 3)
        return self.LIMITE_SLOTS_PESSOAIS_BASE + extras

    def adicionar_xp(self, quantidade):
        if quantidade <= 0: return False
        from .loja import InventarioUsuario 
        boost_ativo = InventarioUsuario.objects.filter(
            usuario=self, item__tipo_efeito='XP_BOOST', esta_ativo=True,
            data_expiracao_efeito__gt=timezone.now()
        ).exists()
        if boost_ativo:
            quantidade = quantidade * 2 
            logger.info(f"XP DOBRADO para {self.email}! Ganhou {quantidade} XP.")
        self.xp_atual += quantidade
        logger.debug(f"Usuário {self.email} ganhou {quantidade} XP. Total agora: {self.xp_atual}")
        self.save(update_fields=['xp_atual'])
        return self.verificar_level_up()
    
    def adicionar_moedas(self, quantidade):
        if quantidade == 0: return
        self.moedas += quantidade
        if self.moedas < 0: self.moedas = 0
        self.save(update_fields=['moedas'])
        logger.debug(f"Usuário {self.email} alterou moedas em {quantidade}. Total: {self.moedas}")

    def verificar_level_up(self):
        upou = False 
        while self.xp_atual >= self.xp_proximo_nivel:
            upou = True
            self.nivel += 1
            xp_excedente = self.xp_atual - self.xp_proximo_nivel
            novo_xp_necessario = int(self.XP_BASE_PARA_NIVEL_2 * (self.XP_MULTIPLICADOR ** (self.nivel - 1)))
            self.xp_atual = xp_excedente
            self.xp_proximo_nivel = novo_xp_necessario
            self.save(update_fields=['xp_atual', 'xp_proximo_nivel', 'nivel'])
            logger.info(f"Usuário {self.email} UPOU! Nível: {self.nivel}. XP atual: {self.xp_atual}. Próximo nível: {self.xp_proximo_nivel} XP.")
        return upou
    
    def get_inicio_dia_de_jogo_atual(self):
        agora = timezone.localtime(timezone.now())
        hora_corte_dt = timezone.make_aware(
            datetime.combine(agora.date(), self.HORA_CORTE_RESET),
            timezone.get_current_timezone()
        )
        if agora < hora_corte_dt:
            inicio_dia = hora_corte_dt - timezone.timedelta(days=1)
        else:
            inicio_dia = hora_corte_dt
        return inicio_dia

    def verificar_e_resetar_slots_diarios(self):
        data_do_dia_de_jogo_atual = self.get_inicio_dia_de_jogo_atual().date()
        slots_foram_resetados = False
        
        if self.data_reset_slots < data_do_dia_de_jogo_atual:
            logger.info(f"Resetando Slots para {self.email}.")
            self.slots_tarefas_pessoais_usados = 0
            self.slots_tarefas_ia_usados = 0
            self.data_reset_slots = data_do_dia_de_jogo_atual 
            
            self.save(update_fields=[
                'slots_tarefas_pessoais_usados', 
                'slots_tarefas_ia_usados', 
                'data_reset_slots'
            ])
            slots_foram_resetados = True
        
        return slots_foram_resetados

    def verificar_manutencao_ofensiva(self):
        if not self.ultimo_resgate_foco:
            return 
            
        data_hoje = self.get_inicio_dia_de_jogo_atual().date()
        data_ultimo_jogo = timezone.localtime(self.ultimo_resgate_foco).date()
        diferenca = (data_hoje - data_ultimo_jogo).days
        
        if diferenca > 1:
            from .loja import InventarioUsuario
            
            congelador = InventarioUsuario.objects.filter(
                usuario=self, 
                item__tipo_efeito='CONGELADOR', 
                quantidade__gt=0
            ).first()

            if congelador:
                congelador.quantidade -= 1
                congelador.save()
                ontem_fake = timezone.now() - timedelta(days=1)
                self.ultimo_resgate_foco = ontem_fake
                self.save(update_fields=['ultimo_resgate_foco'])
                logger.info(f"CONGELADOR USADO! Streak salvo.")
            else:
                self.dias_foco = 0
                self.save(update_fields=['dias_foco'])
                logger.info(f"OFENSIVA ZERADA para {self.email}.")

    def __str__(self):
        return self.email