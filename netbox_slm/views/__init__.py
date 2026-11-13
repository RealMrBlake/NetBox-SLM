# Modified by MrBlake for the NetBox-SLM fork: https://git.mrblake.cc/MrBlake/NetBox-SLM
# Based on ICTU/netbox_slm (Apache License 2.0). See the LICENSE and NOTICE files.
from .software_license import (
    SoftwareLicenseListView,
    SoftwareLicenseView,
    SoftwareLicenseEditView,
    SoftwareLicenseDeleteView,
    SoftwareLicenseBulkDeleteView,
    SoftwareLicenseBulkImportView,
)
from .software_product import (
    SoftwareProductListView,
    SoftwareProductView,
    SoftwareProductEditView,
    SoftwareProductDeleteView,
    SoftwareProductBulkDeleteView,
    SoftwareProductBulkImportView,
)
from .software_product_installation import (
    SoftwareProductInstallationListView,
    SoftwareProductInstallationView,
    SoftwareProductInstallationEditView,
    SoftwareProductInstallationDeleteView,
    SoftwareProductInstallationBulkDeleteView,
    SoftwareProductInstallationBulkImportView,
)
from .software_product_version import (
    SoftwareProductVersionListView,
    SoftwareProductVersionView,
    SoftwareProductVersionEditView,
    SoftwareProductVersionDeleteView,
    SoftwareProductVersionBulkDeleteView,
    SoftwareProductVersionBulkImportView,
)
from .certificate import (
    CertificateListView,
    CertificateView,
    CertificateEditView,
    CertificateDeleteView,
    CertificateBulkDeleteView,
    CertificateBulkImportView,
)
