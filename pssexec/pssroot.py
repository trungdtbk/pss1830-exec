"""
"""
import os
from common import PSSCommon
from common import PSSException


class PSSRoot(PSSCommon):
    """Wrapper for PSS root mode."""

    PROMPT_RE = '(root@EC1830-\d+-\d+-ACT:/root[\r\n]*# $)|(root@32EC2-\d+-\d+-ACT:[~\r\n]*# $)'
    STDBY_PROMPT_RE = '(root@EC1830-\d+-\d+-STDBY:/root[\r\n]*# $)|(root@32EC2-\d+-\d+-STDBY:[~\r\n]*# $)'
    EC_IP = '100.0.81.{EC}'
    ACT_EC = None
    STDBY_EC = None

    def open(self):
        super(PSSRoot, self).open()
        self._recv()
        self._get_prompt()
        self._get_active_ec()

    def close(self):
        self._send('exit')
        super(PSSRoot, self).close()

    def stdby_login(self):
        if self.STDBY_EC:
            stdby_ip = self.EC_IP.format(EC=self.STDBY_EC)
            self._send('telnet %s' % stdby_ip)
            for expect, response in [('login:', 'root'), ('Password:', 'ALu12#')]:
                if self._expect(expect):
                    self._send(response)
                else:
                    self._send(self.CTRL_C)
                    raise PSSException(
                        'Failed to login to STDBY EC (%s). Expected: %s but not received' 
                        % (stdby_ip, expect))
            self._get_stdby_prompt()
            if not (self.prompt and 'STDBY' in self.prompt):
                self._send(self.CTRL_C)
                raise PSSException('Failed to login to STDBY EC (%s)' % stdby_ip)

    def stdby_logout(self):
        if 'STDBY' in self.prompt:
            self._send('exit')
            self._get_prompt()
            if not (self.prompt and 'ACT' in self.prompt):
                raise PSSException('Failed to get ACT prompt when logging out of STDBY EC')

    def get_file(self, remotepath, localpath, callback=None, recursive=True):
        """Get files from the NE to the local machine
        """
        self.logger.debug('Openning SFTP')
        scp = self.client.open_sftp()
        if recursive:
            scp.chdir(remotepath)
            for fname in scp.listdir():
                remote = os.path.join(remotepath, fname)
                local = os.path.join(localpath, fname)
                self.logger.debug('Transferring: %s to %s' % (remote, local))
                scp.get(remote, local, callback)
        else:
            self.logger.debug('Transferring: %s to %s' % (remotepath, localpath))
            scp.get(remotepath, localpath, callback)
        scp.close()

    def _get_active_ec(self):
        if self.prompt:
            self.ACT_EC = int(self.prompt.split('-')[2])
            self.STDBY_EC = 1 if self.ACT_EC == 18 else 18
    
    def _get_stdby_prompt(self):
        self.logger.debug('Getting STDBY prompt')
        self._send('')
        data = self._expect(self.STDBY_PROMPT_RE)
        if data:
            self.prompt = data.group().strip()
        self.logger.debug('Got STDBY prompt: %s' % self.prompt)
        return self.prompt
