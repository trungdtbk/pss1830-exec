from common import PSSCommon
from common import PSSException


class PSSRoot(PSSCommon):
    """Wrapper for PSS root mode."""

    PROMPT_RE = '(root@EC1830-\d+-\d+-ACT:[/~\w\r\n]*# $)|(root@32EC2-\d+-\d+-ACT:[/~\w\r\n]*# $)'

    def open(self):
        super(PSSRoot, self).open()
        self._recv()
        self._get_prompt()

    def close(self):
        self._send('exit')
        super(PSSRoot, self).close()
