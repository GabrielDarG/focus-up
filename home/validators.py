import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class StrongPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 6:
            raise ValidationError(
                _("A senha deve ter pelo menos 6 caracteres."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra maiúscula."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra minúscula."),
                code='password_no_lower',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um número."),
                code='password_no_number',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um caractere especial (!@#$ etc)."),
                code='password_no_special',
            )
        
        if re.search(r'(\d)\1{2,}', password):
            raise ValidationError(
                _("A senha não pode conter sequências numéricas repetidas."),
                code='password_sequence',
    )


    def get_help_text(self):
        return _(
            "Sua senha deve ter pelo menos 6 caracteres, incluindo uma letra maiúscula, "
            "uma minúscula, um número e um caractere especial."
        )