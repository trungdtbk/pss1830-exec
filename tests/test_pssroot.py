import pytest

from pssexec.pssroot import PSSRoot
from pssexec.common import PSSException

@pytest.fixture(name="mocked_pssroot")
def create_mocked_pssroot(mocker):
    pss = PSSRoot('localhost', 1234, 'root', 'testpass')
    pss.TIMEOUT = 1
    mock_client = mocker.patch.object(pss, 'client')
    mock_channel = mocker.patch.object(pss, 'channel')
    mock_client.invoke_shell.return_value = mock_channel
    mock_channel.recv_ready.side_effect = [True, False, True, False]
    mock_channel.recv.side_effect = ['Welcome', '\r\nroot@EC1830-81-18-ACT:/root# ']
    pss.open()
    return pss, mock_channel

def test_exec_command(mocked_pssroot):
    pss, mock_channel = mocked_pssroot
    recv_data = pss.execute('hello')
    mock_channel.sendall.assert_called_with('hello\n')

def test_close(mocked_pssroot):
    pss, channel = mocked_pssroot
    pss.close()
    channel.sendall.assert_called_with('exit\n')