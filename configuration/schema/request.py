from dataclasses import dataclass


@dataclass(frozen=True)
class MailgunEmailRequest:
    """
    # MailgunEmailRequest

    These take some of the attributes you would send to mailgun to send a request.

    See https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/messages

    ###  Attributes:

        - sender: str - The sender of the email
        - to: List[str] - The recipients of the email
        - subject: str - The subject of the email
        - text: Optional[str] - The text of the email
        - html: Optional[str] - The html of the email
        - bcc: Optional[str] - The bcc of the email
        - cc: Optional[str] - The cc of the email

    """

    sender: str
    to: list[str]
    subject: str
    cc: list[str] | None
    bcc: list[str] | None
    text: str | None
    html: str | None
