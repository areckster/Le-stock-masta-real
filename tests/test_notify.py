import os
import sys
import types
import unittest
from unittest.mock import patch

# Dummy discord_webhook module so notify imports cleanly
dummy_webhook = types.ModuleType("discord_webhook")
dummy_webhook.DiscordWebhook = object
sys.modules.setdefault("discord_webhook", dummy_webhook)

import notify


class DummyResponse:
    status_code = 200


class TestNotify(unittest.TestCase):
    def test_env_variable_used(self):
        with patch('signals.load_config', return_value={'discord_webhook_url': '${STOCK_SIGNAL_WEBHOOK}' }), \
             patch.dict(os.environ, {'STOCK_SIGNAL_WEBHOOK': 'https://example.com'}), \
             patch('notify.DiscordWebhook') as mock_webhook:
            mock_webhook.return_value.execute.return_value = DummyResponse()
            notify.send_discord_notification('hi')
            mock_webhook.assert_called_with(url='https://example.com', content='hi')


if __name__ == '__main__':
    unittest.main()
