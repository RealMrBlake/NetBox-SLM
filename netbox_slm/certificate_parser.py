"""Extract metadata from uploaded X.509 certificate files (PEM or DER)."""

from dataclasses import dataclass, field
from datetime import date

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from django.utils.translation import gettext_lazy as _


class CertificateParseError(ValueError):
    pass


@dataclass
class CertificateInfo:
    common_name: str = ""
    subject_alternative_names: list[str] = field(default_factory=list)
    issuer: str = ""
    serial_number: str = ""
    fingerprint: str = ""
    start_date: date | None = None
    expiration_date: date | None = None
    type: str = ""


def _common_name(name):
    attributes = name.get_attributes_for_oid(NameOID.COMMON_NAME)
    return str(attributes[0].value) if attributes else ""


def _format_hex(data):
    return ":".join(f"{byte:02X}" for byte in data)


def _serial_bytes(serial):
    return serial.to_bytes((serial.bit_length() + 7) // 8 or 1, "big")


def _guess_type(certificate):
    # Values match netbox_slm.models.CertificateTypes
    try:
        if certificate.extensions.get_extension_for_class(x509.BasicConstraints).value.ca:
            return "ca"
    except x509.ExtensionNotFound:
        pass
    try:
        usages = set(certificate.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value)
    except x509.ExtensionNotFound:
        return ""
    for oid, value in (
        (ExtendedKeyUsageOID.SERVER_AUTH, "server"),
        (ExtendedKeyUsageOID.CODE_SIGNING, "code_signing"),
        (ExtendedKeyUsageOID.EMAIL_PROTECTION, "email"),
        (ExtendedKeyUsageOID.CLIENT_AUTH, "client"),
    ):
        if oid in usages:
            return value
    return ""


def parse_certificate(data: bytes) -> CertificateInfo:
    """Parse the first certificate of a PEM or DER file. Files containing private keys are rejected."""
    if b"PRIVATE KEY" in data:
        raise CertificateParseError(
            _("The file contains a private key. Please upload only the certificate without its private key.")
        )
    try:
        if b"-----BEGIN CERTIFICATE-----" in data:
            certificate = x509.load_pem_x509_certificates(data)[0]
        else:
            certificate = x509.load_der_x509_certificate(data)
    except ValueError as error:
        raise CertificateParseError(
            _("The file is not a valid PEM or DER encoded X.509 certificate.")
        ) from error

    sans = []
    try:
        extension = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        sans += extension.get_values_for_type(x509.DNSName)
        sans += [str(address) for address in extension.get_values_for_type(x509.IPAddress)]
    except x509.ExtensionNotFound:
        pass

    issuer = _common_name(certificate.issuer) or certificate.issuer.rfc4514_string()
    return CertificateInfo(
        common_name=_common_name(certificate.subject),
        subject_alternative_names=sans,
        issuer=issuer[:255],
        serial_number=_format_hex(_serial_bytes(certificate.serial_number)),
        fingerprint=_format_hex(certificate.fingerprint(hashes.SHA256())),
        start_date=certificate.not_valid_before_utc.date(),
        expiration_date=certificate.not_valid_after_utc.date(),
        type=_guess_type(certificate),
    )


def apply_certificate_file(values: dict, uploaded_file) -> None:
    """
    Fill certificate fields in ``values`` (form cleaned_data or serializer attrs) from an uploaded file.

    Fields derived from the certificate are overwritten so they always match the uploaded file. Name and type
    are only set when they were left empty.
    """
    uploaded_file.seek(0)
    info = parse_certificate(uploaded_file.read())
    uploaded_file.seek(0)

    values["common_name"] = info.common_name
    values["subject_alternative_names"] = "\n".join(info.subject_alternative_names)
    values["issuer"] = info.issuer
    values["serial_number"] = info.serial_number
    values["fingerprint"] = info.fingerprint
    values["start_date"] = info.start_date
    values["expiration_date"] = info.expiration_date
    if not values.get("name"):
        values["name"] = info.common_name or info.fingerprint[:23]
    if not values.get("type") and info.type:
        values["type"] = info.type
