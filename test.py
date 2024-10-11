import paramiko
import logging

# Configuration du journal
logging.basicConfig(filename="connexion.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

EXPECTED = ["joseph_d", "reboot", "root", "sys-admin"]

def examine_last(server, connection):
    command = "sudo last"
    _stdin, stdout, _stderr = connection.exec_command(command)
    lines = stdout.read().decode()
    connection.close()
    for line in lines.split("\n"):
        # Ignorer la dernière ligne du dernier rapport.
        if line.startswith("wtmp begins"):
            break
        parts = line.split()
        if parts:
            account = parts[0]
            if account not in EXPECTED:
                message = f"Entry '{line}' is a surprise on {server}."
                print(message)  # Afficher le message
                logging.error(message)  # Enregistrer le message d'erreur

def key_based_connect(server):
    host = "13.39.87.113"
    special_account = "joseph_d"
    pkey = paramiko.RSAKey.from_private_key_file("/Users/joseph_d/.ssh/joseph_d_rsa")
    client = paramiko.SSHClient()
    policy = paramiko.AutoAddPolicy()
    client.set_missing_host_key_policy(policy)
    try:
        client.connect(host, username=special_account, pkey=pkey)
        message = f"Connected to {host} as {special_account}"
        print(message)  # Afficher le message
        logging.info(message)  # Enregistrer le message d'information
        return client
    except Exception as e:
        message = f"Failed to connect to {host} as {special_account}: {e}"
        print(message)  # Afficher le message
        logging.error(message)  # Enregistrer le message d'erreur
        return None

def main():
    server_list = ["worker1", "worker2", "worker3"]
    for server in server_list:
        connection = key_based_connect(server)
        if connection:
            examine_last(server, connection)
            connection.close()

if __name__ == "__main__":
    main()
