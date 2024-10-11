import paramiko
import logging

# Configuration du journal
logging.basicConfig(filename="connexion.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

EXPECTED = ["joseph_d", "reboot", "root", "sys-admin"]

class SSHClient:
    def __init__(self, ssh_address, ssh_username, ssh_key_file, ssh_port=22):
        self.ssh_address = ssh_address
        self.ssh_username = ssh_username
        self.ssh_key_file = ssh_key_file
        self.ssh_port = ssh_port  # Ajoutez le port comme argument avec une valeur par défaut
        self.client = None

    def examine_last(self):
        if not self.client:
            raise Exception("SSH client is not connected.")
        command = "sudo last"
        stdin, stdout, stderr = self.client.exec_command(command)
        lines = stdout.read().decode()
        for line in lines.split("\n"):
            # Ignorer la dernière ligne du dernier rapport.
            if line.startswith("wtmp begins"):
                break
            parts = line.split()
            if parts:
                account = parts[0]
                if account not in EXPECTED:
                    message = f"Entry '{line}' is a surprise on {self.ssh_address}."
                    print(message)  # Afficher le message
                    logging.error(message)  # Enregistrer le message d'erreur

    def connect(self):
        pkey = paramiko.RSAKey.from_private_key_file(self.ssh_key_file)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.ssh_address, username=self.ssh_username, pkey=pkey)
            message = f"Connected to {self.ssh_address} as {self.ssh_username}"
            print(message)  # Afficher le message
            logging.info(message)  # Enregistrer le message d'information
        except Exception as e:
            message = f"Failed to connect to {self.ssh_address} as {self.ssh_username}: {e}"
            print(message)  # Afficher le message
            logging.error(message)  # Enregistrer le message d'erreur

    def close(self):
        if self.client:
            self.client.close()

    def execute_command(self, command):
        if self.client.get_transport() is None or not self.client.get_transport().is_active():
            self.connect()
        stdin, stdout, stderr = self.client.exec_command(command)
        print(stdout.read())
