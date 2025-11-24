
from .models.amigo import PedidoAmizade 
def pending_requests_count(request):
    """
    Retorna a contagem de pedidos de amizade pendentes para o usuário logado.
    """
    count = 0
    if request.user.is_authenticated:
        count = PedidoAmizade.objects.filter(
            para_usuario=request.user,
            status='pendente' 
        ).count()
    return {'pending_requests_count': count}