import pytest
import threading

import psssim
from pssexec import pssexec

WELCOME = '\nWelcome\n'
RESULT1 = 'result1'
RESULT2 = 'result2'
COMMAND1 = 'command1'
COMMAND2 = 'command2'

CONFIG = {
    'host': 'localhost',
    'port': 1234,
    'username': 'test',
    'password': 'test123',
    'commands': [COMMAND1, COMMAND2],
    'timeout': 3,    
    'mode': None
}

@pytest.fixture(name="mock_psscli")
def setup_psscli(mocker):
    mocker.patch.object(pssexec, 'PSSCli')
    mock_pss = mocker.Mock()
    mock_pss.recv_all.return_value = [WELCOME]
    mock_pss.execute.return_value = [RESULT1, RESULT2]
    pssexec.PSSCli.return_value = mock_pss
    return mock_pss, pssexec.PSSCli

@pytest.fixture(name="mock_pssroot")
def setup_pssroot(mocker):
    mocker.patch.object(pssexec, 'PSSRoot')
    mock_pss = mocker.Mock()
    mock_pss.recv_all.return_value = [WELCOME]
    mock_pss.execute.return_value = [RESULT1, RESULT2]
    pssexec.PSSRoot.return_value = mock_pss
    return mock_pss, pssexec.PSSRoot

@pytest.mark.parametrize('mode', ['root', 'cli'])
def test_config(mode):
    test_config = dict(CONFIG)
    test_config['mode'] = mode    
    test_config['commands'] = [COMMAND1, COMMAND2, COMMAND2]
    parser = pssexec.get_parser()    
    args = parser.parse_args(
        [
            '-m', test_config['mode'],
            '--host', test_config['host'],
            '-w', str(test_config['timeout']),
            '--port', str(test_config['port']),
            '-u', test_config['username'],
            '-p', test_config['password'],
            '-c', test_config['commands'][0], test_config['commands'][1],
            '-c', test_config['commands'][2]
        ])
    config = pssexec.get_config(args)
    for k, v in test_config.iteritems():
        assert config[k] == v

@pytest.mark.parametrize('mode', ['root', 'cli'])
def test_run_with_success(mode, capfd, mock_psscli, mock_pssroot):
    mock_pss, mock_exec = mock_psscli if mode == 'cli' else mock_pssroot
    CONFIG['mode'] = mode    
    pssexec.run(CONFIG)

    mock_pss.open.assert_called_once()
    mock_exec.assert_called_once_with(
        CONFIG['host'], CONFIG['port'], CONFIG['username'], CONFIG['password'])
    mock_pss.execute.has_calls(
        [COMMAND1], [COMMAND2])
    
    output = capfd.readouterr()    
    assert RESULT1 in output.out
    assert RESULT2 in output.out


@pytest.fixture(name="pss_sim")
def setup_pss_sim():
    pss_ne = psssim.server
    return pss_ne

@pytest.fixture(name="setup_teardown")
def setup_teardown(pss_sim):
    print(pss_sim, pss_sim.port)
    t = threading.Thread(target=pss_sim.run)
    t.start()
    yield
    pss_sim.stop()
    t.join()

def test_run_cli(pss_sim, setup_teardown, capfd):    
    config = dict(CONFIG)
    config['port'] = pss_sim.port
    config['mode'] = 'cli'
    config['commands'] = ['show version', 'show sof up st']
    pssexec.run(config)
    output = capfd.readouterr()
    assert '1830PSSECX-11.0-1' in output.out
    assert '/1830PSS32M/EC/' in output.out