# Modified by MrBlake for the NetBox-SLM fork: https://git.mrblake.cc/MrBlake/NetBox-SLM
# Based on ICTU/netbox_slm (Apache License 2.0). See the LICENSE and NOTICE files.
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

certificate_items = (
    PluginMenuItem(
        link="plugins:netbox_slm:certificate_list",
        link_text=_("Certificates"),
        permissions=["netbox_slm.view_certificate"],
        buttons=(
            PluginMenuButton(
                "plugins:netbox_slm:certificate_add",
                _("Add"),
                "mdi mdi-plus-thick",
                permissions=["netbox_slm.add_certificate"],
            ),
            PluginMenuButton(
                "plugins:netbox_slm:certificate_bulk_import",
                _("Import"),
                "mdi mdi-upload",
                permissions=["netbox_slm.add_certificate"],
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
    # NetBox loads only one menu per plugin; this one is registered in SLMConfig.ready()
    certificate_menu = PluginMenu(
        label=_("Certificates"),
        groups=((_("Certificates"), certificate_items),),
        icon_class="mdi mdi-certificate",
    )
else:
    # auto imported by default PluginConfig.menu_items = navigation.menu_items
    menu_items = slm_items + certificate_items
