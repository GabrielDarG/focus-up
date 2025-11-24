# home/models/__init__.py
from .usuario import Usuario
from .tarefa import Tarefa
from .conquista import Conquista, UsuarioConquista
from .loja import ItemLoja, Compra
from .amigo import Amigo
from .grupo import Grupo, GrupoUsuario, GrupoTarefa
from .notificacao import Notificacao
from .usuario_foco import UsuarioFoco       

__all__ = [
    'Usuario',
    'Tarefa',
    'Conquista',
    'UsuarioConquista',
    'ItemLoja',
    'Compra',
    'Amigo',
    'Grupo',
    'GrupoUsuario',
    'GrupoTarefa',
    'Notificacao',
    'UsuarioFoco',  
]