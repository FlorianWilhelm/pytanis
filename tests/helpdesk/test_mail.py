import os

import pytest

from pytanis.helpdesk.api import HelpDeskAPI
from pytanis.helpdesk.mail import Mail, MailClient, Recipient


@pytest.mark.skipif(os.getenv('MAILTEST') is None, reason="people might get annoyed")
def test_sending_dummy_mail():
    test_recipients = [
        Recipient(name="Florian Wilhelm", email="Florian.Wilhelm@gmail.com", address_as="Flo", custom_stuff="X"),
    ]
    test_mail = Mail(
        subject="Pytanis API TEST: Ignore this message",
        text="""Hello {recipient.address_as},
        This is an automated test message via our helpdesk using https://florianwilhelm.info/pytanis/!
        Looks like we are getting somewhere?

        Hope it's ok to call you {recipient.address_as} and not by your full {recipient.name}.
        Have you read the email's subject '{mail.subject}'?
        Cheers!
        """,
        team_id="3f68251e-17e9-436f-90c3-c03b06a72472",  # Program
        agent_id="2d8b5727-49c8-410d-bae8-0da13a65609d",  # Program
        status="solved",
        recipients=test_recipients,
    )

    client = MailClient(HelpDeskAPI())
    tickets, errors = client.sent(test_mail)
    assert not errors
    # Now also check your inbox and tell me if it worked!
