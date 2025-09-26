from dataclasses import dataclass


@dataclass(frozen=True)
class MailgunEmail:
    """
    # Mailgun email configuration
    ### Attributes:

        - api_key: str   - The api key for the given account. This is needed to send emails.
        - base_url: str  - The base url. For accounts in the US, the value is 'https://api.mailgun.net/' and
        for EU 'https://api.eu.mailgun.net/'
        - username: str  - The username for the given account. Typically api or your choosen username.

    """

    api_key: str
    base_url: str | None = "https://api.mailgun.net/"
    username: str | None = "api"
