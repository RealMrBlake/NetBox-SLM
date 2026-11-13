# Modified by MrBlake for the NetBox-SLM fork: https://git.mrblake.cc/MrBlake/NetBox-SLM
# Based on ICTU/netbox_slm (Apache License 2.0). See the LICENSE and NOTICE files.
from .software_license import (
    SoftwareLicenseForm,
    SoftwareLicenseFilterForm,
    SoftwareLicenseBulkImportForm,
    SoftwareLicenseBulkEditForm,
)
from .software_product import (
    SoftwareProductForm,
    SoftwareProductFilterForm,
    SoftwareProductBulkImportForm,
    SoftwareProductBulkEditForm,
)
from .software_product_installation import (
    SoftwareProductInstallationForm,
    SoftwareProductInstallationFilterForm,
    SoftwareProductInstallationBulkImportForm,
    SoftwareProductInstallationBulkEditForm,
)
from .software_product_version import (
    SoftwareProductVersionForm,
    SoftwareProductVersionFilterForm,
    SoftwareProductVersionBulkImportForm,
    SoftwareProductVersionBulkEditForm,
)
from .certificate import (
    CertificateForm,
    CertificateFilterForm,
    CertificateBulkImportForm,
    CertificateBulkEditForm,
)
