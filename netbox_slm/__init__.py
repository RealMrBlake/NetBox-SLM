"""
Copyright 2022-2025 ICTU

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from netbox.plugins import PluginConfig
from django.utils.translation import gettext, gettext_lazy as _

__version__ = "1.13.0"


class SLMConfig(PluginConfig):
    name = "netbox_slm"
    verbose_name = _("Licences")
    version = __version__
    description = _("Licence Management NetBox Plugin.")
    author = "ICTU"
    author_email = "open-source-projects@ictu.nl"
    base_url = "slm"
    required_settings = []
    default_settings = {
        "top_level_menu": True,
        "link_cluster_installations": "right",
        "link_device_installations": "right",
        "link_virtualmachine_installations": "right",
    }

    def ready(self):
        super().ready()

        from netbox.events import EVENT_TYPE_KIND_WARNING, EventType
        from netbox_slm.events import LICENSE_EXPIRING

        EventType(LICENSE_EXPIRING, gettext("License expiring"), kind=EVENT_TYPE_KIND_WARNING).register()

        from netbox_slm import jobs  # noqa: F401


config = SLMConfig
