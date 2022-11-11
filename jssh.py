from ensurepip import version
import io
import os
import sys
from base64 import b64encode
from paramiko import SSHConfig

__version__ = '0.1.0'


def log(msg, level='o'):
    """
    Prints log messages to different streams defined by the given log level:
        o = stdout (default)
        e = stderr
        d = stdout (only when debug is True)
    """

    if level == 'o':
        print(msg)

    elif level == 'e':
        print(msg, file=sys.stderr)

    elif level == 'd' and debug is True:
        print("DEBUG: {}".format(msg))


def initiate_connection(host):

    # Read ssh config file
    try:
        log('Reading ssh config file', 'd')

        global ssh_config
        ssh_config = SSHConfig()
        ssh_config.parse(
            open("{}/.ssh/config".format(os.path.expanduser("~"))))

    except:
        log('Failed to read ssh config file', 'e')
        exit(1)

    # Get information about host to connect to
    try:
        log("Getting required information for host: {}".format(host), 'd')

        host_address = ssh_config.lookup(host)['hostname']
        host_user = ssh_config.lookup(host)['user']
        jump_host = ssh_config.lookup(host)['jumphost']

    except:
        log("Configuration for {} is missing HostName, User, or JumpHost".format(host), 'e')
        exit(1)

    # Set hosts port
    try:
        host_port = ssh_config.lookup(host)['port']
        log("{} port is: {}".format(host, host_port), 'd')

    except:
        # Explicitly fallback to default port of 22 so connection string is valid later
        log("{} port not specified in ssh config. Defaulting to 22".format(host), 'd')
        host_port = 22

    # Get ssh key path for endpoint host if it exists
    try:
        host_id_file = ssh_config.lookup(host)['identityfile'][0]
        log("Found identity file {} found for {}".format(
            host_id_file, host), 'd')

    except:
        log('No identity file found for {}'.format(host), 'd')

    # If host_id_file exists, get its content, convert to base64, and build connection string
    if host_id_file is not None:
        log('Reading id file for host {}'.format(host), 'd')

        try:
            with io.open(host_id_file, newline='\r') as f:
                host_key = f.read()
                f.close()

        except:
            log("Failed to read key for {}".format(host), 'e')
            exit(1)

        # Encode to base64 to mitigate line ending issues on ssh command
        host_key = b64encode(host_key.encode('utf-8'))

        # Build connection string
        log('Building host connection string with id file', 'd')
        connection_string = "set +m; \
                            temp_path=$(mktemp --directory); \
                            echo '{host_key}' | base64 -d > $temp_path/key; \
                            chmod 600 $temp_path/key; \
                            (( sleep 1 && rm -rf \"$temp_path\" )&); \
                            ssh -i $temp_path/key {host_user}@{host_address} -p {host_port}".format(
            host_key=host_key.decode('utf-8'),
            host_user=host_user,
            host_address=host_address,
            host_port=host_port)

    else:
        # If no ssh key is found, build connection string without the -i argument
        log('Building connection string without id file', 'd')
        connection_string = "ssh {host_user}@{host_address} -p {host_port}".format(
            host_user=host_user,
            host_address=host_address,
            host_port=host_port)

    # Initiate connection
    try:
        log('Initiating connection...', 'd')
        os.system(
            "ssh {jump_host} -t \"{connection_string}\"".format(
                jump_host=jump_host,
                connection_string=connection_string))

    except:
        log('Failed to complete seemless connection to {} via {}'.format(
            host, jump_host), 'e')

# Very simple arg parsing. Not using argpass or alternatives as
# there are not enough commands to worry about currently. If the
# tool gains more features, then this will be readdressed.


if len(sys.argv) >= 4:
    log('Too many arguments passed', 'e')
    exit(1)

# Set debugging messages on/off
try:
    if sys.argv[2] == 'debug':
        debug = True
    else:
        debug = False
        log("Unknown positional argument '{}' ignoried".format(
            sys.argv[2]), 'e')

except:
    debug = False

# Print version or start connection
if len(sys.argv) == 1:
    print(__version__)

elif len(sys.argv) == 2 or 3:
    initiate_connection(sys.argv[1])
