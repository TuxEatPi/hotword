import logging
import os
import sys
import time

import pytest
from click.testing import CliRunner


class TestCli(object):

    @pytest.mark.order1
    def test_help(self, capsys):
        # --help
        runner = CliRunner()
        sys.argv = ['fakedaemon', '-I', 'intents/', '-w', 'tests/badworkdir/', '-D', 'dialogs']
        with pytest.raises(SystemExit):
            from tuxeatpi_hotword_kittai.common import cli
