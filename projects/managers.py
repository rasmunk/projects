from projects_base.base.forms import FormManager
from projects.conf import config_class, config_module

form_manager = FormManager(
    default_class=config_class, default_module=config_module, custom_key="default_form"
)
