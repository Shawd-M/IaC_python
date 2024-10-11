import yaml
import logging
import subprocess
import jinja2
from ssh_client import SSHClient

# Configuration de la journalisation dans main.py
logging.basicConfig(level=logging.INFO)  # Configurez le niveau de journalisation comme vous le souhaitez

def main():
    # Charger les todos YAML (supposons que vous avez un fichier todos.yml)
    with open('todos.yml', 'r') as file:
        todos = yaml.safe_load(file)
    num_tasks = len(todos)

    logging.info(f"Nombre de tâches à exécuter : {num_tasks}")

    # Charger l'inventaire YAML (supposons que vous avez un fichier inventory.yml)
    with open('inventory.yml', 'r') as file:
        inventory = yaml.safe_load(file)

    # Charger l'état des tâches depuis un fichier de suivi
    try:
        with open('task_status.yml', 'r') as status_file:
            task_status = yaml.safe_load(status_file)
    except FileNotFoundError:
        task_status = {}

    for host, host_info in inventory['hosts'].items():
        logging.info(f"Exécution des tâches sur l'hôte {host} (IP: {host_info['ssh_address']}):")
        logging.info(f"Exécution des tâches sur l'utilisateur {host_info['ssh_username']} (IP: {host_info['ssh_username']}):")

        ssh_client = SSHClient(
            host_info['ssh_address'],
            host_info['ssh_username'],
            host_info['ssh_key_file'],
            host_info.get('ssh_port', 22)  # Utilisez le port spécifié dans l'inventaire ou 22 par défaut
        )
        ssh_client.connect()

        # ssh_client.execute_command("sudo mkdir -p /var/www/public")
        # ssh_client.execute_command("mkdir ./public")
        # sudo yum install -y est à utiliser, apt marche pas
        # Pour tester, basculer entre install et remove

        for task in todos:
            module = task['module']
            params = task['params']

            # Identifier une tâche précédemment réussie
            if module in ['copy', 'template', 'command', 'sysctl']:
                task_key = module
            else:
                task_key = f"{module}_{params['name']}_{params['state']}"

            if task_key in task_status and task_status[task_key] == "ok":
                status = "ok"
                logging.info("Tâche déjà effectuée")
            else:
                status = "changed"
                # La tâche n'a pas été exécutée ou a échoué précédemment, exécutez-la
                if module == 'apt':
                    # Installation d'un package via apt
                    command = f"sudo yum install -y {params['name']}"
                    logging.info(f"Commande à exécuter : {command}")
                elif module == 'copy':
                    # Copie de fichiers/dossiers
                    command = f"sudo cp -r {params['src']} {params['dest']}"
                    logging.info(f"Commande à éxécuter : {command}")
                elif module == 'template':
                    # Copie d'un modèle

                    src_path = params['src']  # Chemin vers le modèle Jinja2
                    dest_path = params['dest']  # Chemin de destination pour le fichier généré

                    # Charger le modèle Jinja2
                    with open(src_path, 'r') as template_file:
                        template = jinja2.Template(template_file.read())

                    # Créez un dictionnaire pour passer les variables depuis todos.yml
                    template_vars = {
                        'listen_port': params.get('vars', {}).get('listen_port', ''),
                        'server_name': params.get('vars', {}).get('server_name', ''),
                        'document_root': params.get('vars', {}).get('document_root', ''),
                    }

                    # Remplacer les variables du modèle par les valeurs spécifiques
                    nginx_config = template.render(**template_vars)

                    # Écrire la configuration générée dans le fichier de destination
                    with open(dest_path, 'w') as config_file:
                        config_file.write(nginx_config)

                    # Utilisez `sudo` pour copier le fichier généré
                    copy_command = f"sudo cp {dest_path} {params['dest']}"
                    subprocess.run(copy_command, shell=True)
                    logging.info(f"Commande à éxécuter : {copy_command}")

                elif module == 'service':
                    # Gestion des services
                    if params['state'] == 'started':
                        command = f"sudo service {params['name']} start"
                        logging.info(f"Commande à éxécuter : {command}")
                    elif params['state'] == 'enabled':
                        command = f"sudo systemctl enable {params['name']}"
                        logging.info(f"Commande à éxécuter : {command}")

                elif module == 'command':
                    # Exécution de la commande shell spécifiée
                    command = params['command']
                    result = ssh_client.execute_command(command)
                    logging.info(f"Commande éxécutée avec succès : {command}")

                elif module == 'sysctl':
                    attribute = params['attribute']
                    value = params['value']
                    permanent = params.get('permanent', False)

                    sysctl_command = f"sudo sysctl -w {attribute}={value}"
                    if permanent:
                        sysctl_command += " -p"
                    result = ssh_client.execute_command(sysctl_command)
                    logging.info(f"Commande sysctl éxécutée avec succès : {sysctl_command}")

                # Exécutez la commande sur le serveur distant
                try:
                    result = ssh_client.execute_command(command)
                    logging.info(f"Commande éxécutée avec succès : {command}")
                    # Mettez à jour le statut de la tâche
                    task_status[task_key] = "ok"
                except Exception as e:
                    logging.error(f"Erreur lors de l'éxécution de la commande : {command} - {e}")
                    # Mettez à jour le statut de la tâche en cas d'échec
                    task_status[task_key] = "failed"

            # Mettez à jour le statut de la tâche dans le fichier de suivi
            with open('task_status.yml', 'w') as status_file:
                yaml.dump(task_status, status_file)


        ssh_client.close()

if __name__ == '__main__':
    main()
