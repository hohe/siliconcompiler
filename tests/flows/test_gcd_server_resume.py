import os
import subprocess

import pytest

###########################
@pytest.mark.skip(reason=
    "Need to figure out how to handle check_manifest() call which fails on "
    "local import step since setup for tools running remotely hasn't been "
    "performed")
@pytest.mark.eda
def test_gcd_server(gcd_chip):
    '''Basic sc-server test: Run a local instance of a server, and build the GCD
       example using loopback network calls to that server.
    '''

    # Start running an sc-server instance.
    os.mkdir('local_server_work')
    with open('../test.log', 'w') as f:
        srv_proc = subprocess.Popen(['sc-server',
                                     '-nfs_mount', './local_server_work',
                                     '-cluster', 'local',
                                     '-port', '8082'],
                                    stdout = f)

    # Ensure that klayout doesn't open its GUI after results are retrieved.
    os.environ['DISPLAY'] = ''

    # Run an 'sc' step which stops at the 'floorplan' step.
    gcd_chip.add('steplist', 'import')
    gcd_chip.add('steplist', 'syn')
    gcd_chip.add('steplist', 'floorplan')
    gcd_chip.set('remote', 'addr', 'localhost')
    gcd_chip.set('remote', 'port', 8082)
    gcd_chip.run()

    # Run another 'sc' step to resume, complete, and delete the prior job run.
    sproc = subprocess.run(['sc',
                            '-cfg', 'build/gcd/job0/floorplan0/sc_manifest.json',
                            '-dir', 'build/',
                            '-steplist', 'synopt',
                            '-steplist', 'place',
                            '-steplist', 'route',
                            '-steplist', 'dfm',
                            '-steplist', 'export',
                            '-remote_addr', 'localhost',
                            '-remote_port', '8082',
                            '-loglevel', 'NOTSET'],
                           stdout = subprocess.PIPE)

    # Kill the server process.
    srv_proc.kill()

    # Verify that GDS and SVG files were generated and returned.
    assert os.path.isfile('build/gcd/job0/export0/outputs/gcd.gds')
