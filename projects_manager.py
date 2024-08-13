import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk

class ProjectManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.loading_text = ctk.CTkLabel(self, text="", font=("Helvetica", 12))
        self.loading_text.pack(pady=10)

        self.title("Project Manager")
        self.geometry("1000x500")
        self.configure(bg="#2c2c2c")

        self.project_name_var = ctk.StringVar()
        self.logs_visible = True
        self.loading_overlay = None
        self.create_widgets()
        self.update_sites_list()

    def create_widgets(self):
        # Container frames
        left_frame = ctk.CTkFrame(self, fg_color="#2c2c2c")
        left_frame.place(relwidth=0.7, relheight=1)

        right_frame = ctk.CTkFrame(self, fg_color="#2c2c2c")
        right_frame.place(relx=0.7, relwidth=0.3, relheight=1)

        # Left frame widgets
        button_frame = ctk.CTkFrame(left_frame, fg_color="#2c2c2c")  # Un conteneur pour les boutons
        button_frame.pack(pady=10, padx=10, anchor="w")

        ctk.CTkButton(button_frame, text="Poweroff", command=self.call_poweroff, fg_color="red", text_color="white", width=125, font=("Helvetica", 14, "bold")).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Update", command=self.update_sites_list_btn, fg_color="green", text_color="white", width=125, font=("Helvetica", 14, "bold")).pack(side="left", padx=5)

        ctk.CTkLabel(left_frame, text="Sites installés:", fg_color="#2c2c2c", text_color="white", font=("Helvetica", 20, "bold")).pack(pady=10)

        # Use a standard Tkinter Canvas
        self.canvas = ctk.CTkCanvas(left_frame, height=200, bg="#2c2c2c", bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = ctk.CTkScrollbar(left_frame, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sites_frame = ctk.CTkFrame(self.canvas, fg_color="#2c2c2c")
        self.canvas.create_window((0, 0), window=self.sites_frame, anchor=tk.NW)
        self.sites_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Right frame widgets
        ctk.CTkLabel(right_frame, text="Ajouter un projet:", fg_color="#2c2c2c", text_color="white", font=("Helvetica", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(right_frame, text="Nom du projet:", fg_color="#2c2c2c", text_color="white", font=("Helvetica", 14), width=20).pack(pady=1)
        ctk.CTkEntry(right_frame, textvariable=self.project_name_var, width=200, font=("Helvetica", 10)).pack(pady=5)

        for text, command in [
            ("WordPress", self.create_wordpress_project),
            ("Laravel", self.create_laravel_project),
            ("GitHub", self.create_from_github),
            ("Scratch", self.create_from_scratch)
        ]:
            ctk.CTkButton(right_frame, text=text, command=command, fg_color="#161616", text_color="white", font=("Helvetica", 14, "bold")).pack(pady=5, padx=10, ipadx=10)

    def log(self, message):
        if self.logs_visible:
            print(message)

    def set_loading(self, is_loading):
        if is_loading:
            if not self.loading_overlay:
                self.loading_overlay = ctk.CTkFrame(self, fg_color='black')
                self.loading_overlay.place(relwidth=1, relheight=1, anchor=tk.NW)

                canvas = ctk.CTkCanvas(self.loading_overlay, bg='black')
                canvas.pack(fill=tk.BOTH, expand=True)
                canvas.create_rectangle(0, 0, 1, 1, fill='black', stipple='gray25')

                self.loading_text = ctk.CTkLabel(self.loading_overlay, text="Chargement en cours...", text_color="white", fg_color="black", font=("Helvetica", 16, "bold"))
                self.loading_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

                self.loading_overlay.lift()
                self.loading_overlay.focus_set()
        else:
            if self.loading_overlay:
                self.loading_overlay.place_forget()
                self.loading_overlay = None
                self.loading_text = None

    def validate_project_name(self, project_name):
        self.display_step("Validation du nom du projet")
        if not project_name:
            messagebox.showerror("Erreur", "Le nom du projet ne peut pas être vide.")
            return False
        if not all(c.isalnum() or c in "-" for c in project_name):
            messagebox.showerror(
                "Erreur",
                "Le nom du projet contient des caractères invalides. Utilisez uniquement des lettres, des chiffres et des tirets.",
            )
            return False
        if os.path.isdir(f"sites/{project_name}"):
            messagebox.showerror(
                "Erreur",
                "Un projet portant ce nom existe déjà.",
            )
            return False
        return True


    def check_prerequisites(self):
        missing_tools = []
        self.display_step("Vérification des outils")
        for tool in ["ddev", "wp", "composer", "git"]:
            if subprocess.call(f"type {tool}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
                missing_tools.append(tool)
        if missing_tools:
            messagebox.showerror(
                "Erreur",
                f"Les outils suivants ne sont pas installés : {', '.join(missing_tools)}. Veuillez les installer et réessayer."
            )
            return False
        return True

    def create_wordpress_project(self):
        self.execute_in_thread(self._create_wordpress_project)

    def _create_wordpress_project(self):
        project_name = self.project_name_var.get()
        if self.validate_project_name(project_name) and self.check_prerequisites():
            try:
                self.display_step("Création du dossier")
                self.run_command(f"mkdir -p sites/{project_name}")
                os.chdir(f"sites/{project_name}")
                self.display_step("Création du projet WordPress")
                self.run_command("../../.tools/wp-cli.phar core download")
                self.display_step("Configuration du projet WordPress")
                self.run_command("../../.tools/wp-cli.phar config create --dbname=db --dbuser=db --dbpass=db --dbhost=db --skip-check")
                self.ddev_init(project_name, "apache-fpm", "mysql:8.0")
                self.update_sites_list()
                messagebox.showinfo("Succès", f"Projet WordPress créé avec succès. Accessible à l'adresse: https://{project_name}.ddev.site")
            except Exception as e:
                os.chdir(f"../../")
                messagebox.showerror("Erreur", str(e))

    def create_laravel_project(self):
        self.execute_in_thread(self._create_laravel_project)

    def _create_laravel_project(self):
        project_name = self.project_name_var.get()
        if self.validate_project_name(project_name) and self.check_prerequisites():
            try:
                self.display_step("Création du dossier")
                self.run_command(f"mkdir -p sites/{project_name}")
                os.chdir(f"sites/{project_name}")
                self.display_step("Création du projet Laravel")
                self.run_command("composer create-project --prefer-dist laravel/laravel .")
                self.display_step("Configuration du projet Laravel")
                self.update_laravel_env(project_name)
                self.ddev_init(project_name, "apache-fpm", "mysql:8.0", True)
                self.update_sites_list()
                messagebox.showinfo("Succès", "Projet Laravel créé avec succès.")
            except Exception as e:
                os.chdir(f"../../")
                messagebox.showerror("Erreur", str(e))

    def create_from_github(self):
        self.execute_in_thread(self._create_from_github)

    def _create_from_github(self):
        project_name = self.project_name_var.get()
        if self.validate_project_name(project_name) and self.check_prerequisites():
            repo_link = ctk.simpledialog.askstring("Lien GitHub", "Lien vers le GitHub:")
            if repo_link:
                try:
                    self.display_step("Création du dossier")
                    self.run_command(f"mkdir -p sites/{project_name}")
                    os.chdir(f"sites/{project_name}")
                    self.display_step("Clonage du projet depuis Git")
                    self.run_command(f"git clone --recursive {repo_link} .")
                    self.ddev_init(project_name, "apache-fpm", "mysql:8.0")
                    self.update_sites_list()  # Mettre à jour la liste des sites
                    messagebox.showinfo("Succès", "Projet créé depuis GitHub avec succès.")
                except Exception as e:
                    os.chdir(f"../../")
                    messagebox.showerror("Erreur", str(e))

    def create_from_scratch(self):
        self.execute_in_thread(self._create_from_scratch)

    def _create_from_scratch(self):
        project_name = self.project_name_var.get()
        if self.validate_project_name(project_name) and self.check_prerequisites():
            try:
                self.display_step("Création du dossier")
                self.run_command(f"mkdir -p sites/{project_name}")
                os.chdir(f"sites/{project_name}")
                self.display_step("Ecriture du fichier index.php")
                with open("index.php", "w") as file:
                    file.write("<?php echo 'Hello World'; ?>")
                self.ddev_init(project_name, "apache-fpm", "mysql:8.0")
                self.update_sites_list()  # Mettre à jour la liste des sites
                messagebox.showinfo("Succès", "Projet créé from Scratch avec succès.")
            except Exception as e:
                os.chdir(f"../../")
                messagebox.showerror("Erreur", str(e))

    def update_laravel_env(self, project_name):
        env_path = ".env"
        with open(env_path, "r") as file:
            data = file.readlines()

        for i, line in enumerate(data):
            if line.startswith("APP_NAME="):
                data[i] = f"APP_NAME={project_name}\n"
            if line.startswith("APP_URL="):
                data[i] = f"APP_URL=https://{project_name}.ddev.site\n"
            if line.startswith("DB_CONNECTION="):
                data[i] = "DB_CONNECTION=mysql\n"
            if line.startswith("DB_HOST="):
                data[i] = "DB_HOST=db\n"
            if line.startswith("DB_DATABASE="):
                data[i] = "DB_DATABASE=db\n"
            if line.startswith("DB_USERNAME="):
                data[i] = "DB_USERNAME=db\n"
            if line.startswith("DB_PASSWORD="):
                data[i] = "DB_PASSWORD=db\n"

        with open(env_path, "w") as file:
            file.writelines(data)

    def ddev_init(self, project_name, webserver_type, database, laravel = None):
        self.display_step("Configuration de ddev")
        self.run_command(f"ddev config --project-name={project_name}")
        self.run_command(f"ddev config --webserver-type={webserver_type}")
        self.run_command(f"ddev config --database={database}")
        self.display_step("Installation de phpmyadmin")
        self.run_command("ddev get ddev/ddev-phpmyadmin")
        self.display_step("Démarrage de ddev")
        self.run_command("ddev start")
        if laravel:
            self.display_step("Migration de Laravel")
            self.run_command('ddev php artisan migrate')
        self.display_step("Lancement du site")
        self.run_command("ddev launch")
        self.project_name_var.set("")
        os.chdir(f"../../")

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log(result.stdout.decode())
            return result.stdout.decode()
        except subprocess.CalledProcessError as e:
            self.log(e.stderr.decode())
            raise Exception(e.stderr.decode())

    def update_sites_list_btn(self):
        self.execute_in_thread(self.update_sites_list)

    def update_sites_list(self):
        self.display_step("Mise à jour de la liste des sites")
        for widget in self.sites_frame.winfo_children():
            try:
                widget.destroy()
            except Exception as e:
                print(f"Erreur lors de la destruction d'un widget : {e}")
        sites_dir = './sites'
        if os.path.exists(sites_dir):
            try:
                sites_list = os.listdir(sites_dir)
                if not sites_list:
                    print("The sites directory is empty.")
                for site_name in sites_list:
                    site_path = os.path.join(sites_dir, site_name)
                    if os.path.isdir(site_path):
                        print(f"Processing site directory: {site_name}")
                        try:
                            site_frame = ctk.CTkFrame(self.sites_frame, fg_color="#2c2c2c")
                            site_frame.pack(fill=tk.X, pady=10)

                            status = self.get_ddev_status(site_name)
                            print(f"Status of {site_name}: {status}")

                            circle_color = "green" if status else "red"
                            circle = ctk.CTkCanvas(site_frame, width=20, height=20, bg="#2c2c2c", highlightthickness=0)
                            circle.create_oval(5, 5, 15, 15, fill=circle_color, outline=circle_color)
                            circle.pack(side=tk.LEFT, padx=5)

                            tk.Label(site_frame, text=site_name, bg="#2c2c2c", fg="white",
                                     font=("Helvetica", 14, "bold")).pack(side=tk.LEFT, padx=5)

                            if status:
                                ctk.CTkButton(site_frame, text="Open on browser",
                                              command=lambda s=site_name: self.open_browser(s),
                                              fg_color="#161616", text_color='white',
                                              font=("Helvetica", 12, "bold"), width=100).pack(side=tk.LEFT, padx=5)
                                ctk.CTkButton(site_frame, text="Open PMA",
                                              command=lambda s=site_name: self.open_browser(s, True),
                                              fg_color="#161616", text_color='white',
                                              font=("Helvetica", 12, "bold"), width=100).pack(side=tk.LEFT, padx=5)
                                ctk.CTkButton(site_frame, text="Open folder",
                                            command=lambda s=site_name: self.open_folder(site_name),
                                            fg_color="#161616", text_color='white',
                                            font=("Helvetica", 12, "bold"), width=100).pack(side=tk.LEFT, padx=5)
                                ctk.CTkButton(site_frame, text="Stop",
                                              command=lambda s=site_name: self.stop_site(s),
                                              fg_color="#660000", text_color='#fff',
                                              font=("Helvetica", 12, "bold"), width=50).pack(side=tk.LEFT, padx=5)
                            else:
                                ctk.CTkButton(site_frame, text="Start",
                                              command=lambda s=site_name: self.start_site(s),
                                              fg_color="#228B22", text_color='#fff',
                                              font=("Helvetica", 12, "bold"), width=50).pack(side=tk.LEFT, padx=5)
                                ctk.CTkButton(site_frame, text="Delete",
                                              command=lambda s=site_name: self.delete_site(s),
                                              fg_color="#ff0000", text_color='#fff',
                                              font=("Helvetica", 12, "bold"), width=50).pack(side=tk.LEFT, padx=5)
                        except Exception as e:
                            print(f"Error processing site {site_name}: {e}")
                    else:
                        print(f"{site_name} is not a directory.")

            except Exception as e:
                print(f"Error reading sites directory: {e}")
        else:
            print(f"The directory {sites_dir} does not exist.")


    def get_ddev_status(self, project_name):
        try:
            command = f"ddev list | grep '{project_name}' | awk '{{print $4}}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            status = result.stdout.strip()
            if "OK" in status:
                return True
            return False
        except subprocess.CalledProcessError as e:
            self.log(f"Error checking status: {e.stderr.decode()}")
            return False

    def start_site(self, site_name):
        """Démarre le site en utilisant ddev."""
        self.execute_in_thread(lambda: self._manage_site(site_name, 'start'))

    def stop_site(self, site_name):
        """Arrête le site en utilisant ddev."""
        self.execute_in_thread(lambda: self._manage_site(site_name, 'stop'))

    def delete_site(self, site_name):
        """Supprime le site et son dossier."""
        self.execute_in_thread(lambda: self._delete_site(site_name))

    def _manage_site(self, site_name, action):
        site_path = os.path.join('./sites', site_name)
        if os.path.exists(site_path):
            try:
                os.chdir(site_path)
                if action == 'start':
                    self.display_step("Démarrage du site")
                    self.run_command("ddev start")
                    self.run_command("ddev launch")
                elif action == 'stop':
                    self.display_step("Arret du site")
                    self.run_command("ddev stop")
                os.chdir('../../')
                self.update_sites_list()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la gestion du site {site_name}: {e}")

    def _delete_site(self, site_name):
        site_path = os.path.join('./sites', site_name)
        self.display_step("Suppression du site")
        if os.path.exists(site_path):
            if self.demande_confirmation(f"Êtes-vous sûr de vouloir supprimer le site {site_name} ?"):
                try:
                    print(f"Deleting site {site_name}")
                    self.run_command(f"ddev delete -O -y {site_name}")
                    print(f"Deleting folder {site_name}")
                    self.run_command(f"rm -rf {site_path}")
                    self.update_sites_list()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la suppression du site {site_name}: {e}")

    def execute_in_thread(self, func):
        """Exécute la fonction cible dans un thread séparé."""
        self.set_loading(True)
        thread = threading.Thread(target=lambda: self._thread_wrapper(func))
        thread.start()

    def _thread_wrapper(self, func):
        try:
            func()
        finally:
            self.set_loading(False)

    def on_frame_configure(self, event):
        """Appelé lorsque le frame des sites est configuré pour ajuster le canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def call_poweroff(self):
        if self.demande_confirmation("Êtes-vous sûr de vouloir arrêter ddev ?"):
            self.execute_in_thread(self.poweroff_ddev)

    def poweroff_ddev(self):
        try:
            self.display_step("Arrêt de ddev")
            self.run_command('ddev poweroff')
            self.update_sites_list()
            messagebox.showinfo("Succès", "ddev a été arrêté avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'arrêt de ddev : {e}")

    def demande_confirmation(self, message):
        return messagebox.askyesno("Confirmation", message)

    def open_browser(self, site_name, pma=False):
            """Ouvre le site dans le navigateur."""
            if pma == True:
                site_url = f"https://{site_name}.ddev.site:8037"
            else:
                site_url = f"https://{site_name}.ddev.site"

            subprocess.run(f"xdg-open {site_url}", shell=True)

    def open_folder(self, site_name):
        """Ouvre le dossier du site dans l'explorateur de fichiers."""
        site_path = os.path.join('./sites', site_name)
        subprocess.run(f"xdg-open {site_path}", shell=True)

    def display_step(self, step_message):
        if self.loading_text is not None:
            self.loading_text.configure(text=step_message)
        else:
            print(f"Loading Text not initialized: {step_message}")

if __name__ == "__main__":
    app = ProjectManager()
    app.mainloop()
