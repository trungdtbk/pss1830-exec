"""
"""
import time
import re
import logging
import paramiko


class PSSException(Exception):
    """Exception wrapper."""
    pass


class PSSCommon(object):
    """Common class for 1830PSS SSH session to root and CLI.
    """

    TIMEOUT = 30
    PROMPT_RE = None
    CTRL_C = '\x03'

    logger = logging.getLogger(__name__)

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = False
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.channel = None
        self.prompt = None

    def open(self):
        self.logger.debug('Opening SSH connection')
        if self.connected:
            return
        self.client.connect(self.host, self.port, self.username, self.password)
        self.channel = self.client.invoke_shell()
        self.channel.settimeout(self.TIMEOUT)
        self.connected = True
        self.logger.debug('Opened SSH connection')

    def close(self):
        self.logger.debug('Closing SSH connection')
        if self.connected:
            self.connected = False
            self.channel.close()
            self.client.close()
        self.logger.debug('Closed SSH connection')

    def execute(self, command):
        self.logger.debug('Executing command: %s' % command)
        if not self.connected:
            raise PSSException('Not connected')
        self._send(command)
        return self._recv_all()

    def _expect(self, expect):
        sleep = 0.25
        for _ in range(int(self.TIMEOUT/sleep)):
            data = self._recv()
            match = self._match(expect, data)
            if match:
                return match
            else:
                time.sleep(sleep)
        return None

    def _get_prompt(self):
        self.logger.debug('Getting prompt')
        self._send('')
        data = self._expect(self.PROMPT_RE)
        if data:
            self.prompt = data.group().strip()
        self.logger.debug('Got prompt: %s' % self.prompt)
        return self.prompt

    def _check_prompt(self, data):
        return self._match(self.prompt, data)

    def _match(self, match, data):
        result = None
        if match and data:
            result = re.search(match, data, re.DOTALL)
        return result

    def _send(self, command):
        if not self.connected:
            raise PSSException('Not connected')
        self.channel.sendall(command + '\n')

    def _recv(self):
        if not self.connected:
            raise PSSException('Not connected')
        data = ''
        while self.channel.recv_ready():
            new_data = self.channel.recv(1024)
            if new_data:
                data += new_data
        return data

    def _recv_all(self):
        retries = 0
        sleep = 0.25
        while retries < self.TIMEOUT/sleep:
            data = self._recv()
            if data:
                yield data
                retries = 0
                if self._check_prompt(data):
                    break
            else:
                time.sleep(sleep)
                retries += 1
        raise StopIteration()
