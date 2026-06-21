from app.core.pii_masking import PIIMasker
from app.core.config import settings

def test_pii_masking_enabled():
    """
    Validates regex masking replacements when setting is enabled.
    """
    settings.PII_MASKING_ENABLED = True
    
    # Email Masking
    email_text = "Please reach out to support@acadifysolution.com."
    assert PIIMasker.mask_text(email_text) == "Please reach out to [EMAIL_MASKED]."
    
    # SSN Masking
    ssn_text = "Candidate SSN is 111-22-3333."
    assert PIIMasker.mask_text(ssn_text) == "Candidate SSN is [SSN_MASKED]."
    
    # Phone Masking
    phone_text = "Call +1-555-555-5555 for inquiry."
    assert PIIMasker.mask_text(phone_text) == "Call [PHONE_MASKED] for inquiry."
    
    # Credit Card Masking
    cc_text = "Charge card number 4111222233334444."
    assert PIIMasker.mask_text(cc_text) == "Charge card number [CREDIT_CARD_MASKED]."
    
    # IP Address Masking
    ip_text = "API hosted at 10.0.0.1 ip."
    assert PIIMasker.mask_text(ip_text) == "API hosted at [IP_MASKED] ip."

def test_pii_masking_disabled():
    """
    Ensures PII information remains unredacted when settings flag is false.
    """
    settings.PII_MASKING_ENABLED = False
    raw_payload = "Send updates to engineer@acadifysolution.com."
    
    assert PIIMasker.mask_text(raw_payload) == raw_payload
    
    # Reset default state
    settings.PII_MASKING_ENABLED = True
