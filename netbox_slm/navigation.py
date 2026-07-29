from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu, get_plugin_config
from django.utils.translation import gettext_lazy as _
from . import SLMConfig

slm_items = (
    PluginMenuItem(
        link="plugins:netbox_slm:softwareproduct_list",
        link_text=_("Software Products"),
        permissions=["netbox_slm.add_softwareproduct"],
        buttons=(
            PluginMenuButton(
                "plugins:netbox_slm:softwareproduct_add",
                _("Add"),
                "mdi mdi-plus-thick",
                permissions=["netbox_slm.add_softwareproduct"],
            ),
            PluginMenuButton(
                "plugins:netbox_slm:softwareproduct_bulk_import",
                _("Import"),
                "mdi mdi-upload",
                permissions=["netbox_slm.import_softwareproduct"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_slm:softwareproductversion_list",
        link_text=_("Versions"),
        permissions=["netbox_slm.add_softwareproductversion"],
        buttons=(
            PluginMenuButton(
                "plugins:netbox_slm:softwareproductversion_add",
                _("Add"),
                "mdi mdi-plus-thick",
                permissions=["netbox_slm.add_softwareproductversion"],
            ),
            PluginMenuButton(
                "plugins:netbox_slm:softwareproductversion_bulk_import",
                _("Import"),
                "mdi mdi-upload",
                permissions=["netbox_slm.import_softwareproductversion"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_slm:softwareproductinstallation_list",
        link_text=_("Installations"),
        permissions=["netbox_slm.add_softwareproductinstallation"],
        buttons=(
            PluginMenuButton(
                "plugins:netbox_slm:softwareproductinstallation_add",
                _("Add"),
                "mdi mdi-plus-thick",
                permissions=["netbox_slm.add_softwareproductinstallation"],
            ),
            PluginMenuButton(
                "plugins:netbox_slm:softwareproductinstallation_bulk_import",
                _("Import"),
                "mdi mdi-upload",
                permissions=["netbox_slm.import_softwareproductinstallation"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_slm:softwarelicense_list",
        link_text=_("Licenses"),
        permissions=["netbox_slm.add_softwarelicense"],
        buttons=(
            PluginMenuButton(
                "plugins:netbox_slm:softwarelicense_add",
                _("Add"),
                "mdi mdi-plus-thick",
                permissions=["netbox_slm.add_softwarelicense"],
            ),
            PluginMenuButton(
                "plugins:netbox_slm:softwarelicense_bulk_import",
                _("Import"),
                "mdi mdi-upload",
                permissions=["netbox_slm.import_softwarelicense"],
            ),
        ),
    ),
)

if get_plugin_config("netbox_slm", "top_level_menu"):
    menu = PluginMenu(
        label=_("Licences"),
        groups=((SLMConfig.verbose_name, slm_items),),
        icon_class="mdi mdi-content-save",
    )
else:
    # auto imported by default PluginConfig.menu_items = navigation.menu_items
    menu_items = slm_items
