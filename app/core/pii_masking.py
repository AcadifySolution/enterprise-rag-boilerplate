import re
from app.core.config import settings
from app.core.logging import logger

class PIIMasker:
    # Compile regexes for PII patterns
    EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
    SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    PHONE_REGEX = re.compile(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b')
    # Matches common card splits (xxxx-xxxx-xxxx-xxxx or continuous)
    CREDIT_CARD_REGEX = re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b|\b\d{13,16}\b')
    IPv4_REGEX = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    @classmethod
    def mask_text(cls, text: str) -> str:
        """
        Sanitizes text by replacing PII with placeholders if PII masking is enabled.
        """
        if not settings.PII_MASKING_ENABLED or not text:
            return text

        masked = text
        masked = cls.EMAIL_REGEX.sub("[EMAIL_MASKED]", masked)
        masked = cls.SSN_REGEX.sub("[SSN_MASKED]", masked)
        masked = cls.PHONE_REGEX.sub("[PHONE_MASKED]", masked)
        masked = cls.CREDIT_CARD_REGEX.sub("[CREDIT_CARD_MASKED]", masked)
        masked = cls.IPv4_REGEX.sub("[IP_MASKED]", masked)

        if masked != text:
            logger.info("PII detected and redacted from text segment.")
            
        return masked
