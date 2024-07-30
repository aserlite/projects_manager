import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import tkinter.simpledialog
from tkinter import ttk

class ProjectManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Manager")
        self.geometry("800x600")
        self.configure(bg="#1a2437")

        self.project_name_var = tk.StringVar()
        self.logs_visible = False
        self.loading_overlay = None
        self.create_widgets()
        self.update_sites_list()
        self.toggle_logs()
    def create_widgets(self):
        # Container frames
        left_frame = tk.Frame(self, bg="#1a2437")
        left_frame.place(relwidth=0.7, relheight=1)

        right_frame = tk.Frame(self, bg="#1a2437")
        right_frame.place(relx=0.7, relwidth=0.3, relheight=0.6)

        logs_frame = tk.Frame(self, bg="#1a2437")
        logs_frame.place(relx=0.7, rely=0.6, relwidth=0.3, relheight=0.4)

        # Left frame widgets
        tk.Button(left_frame, text="Poweroff", command=self.call_poweroff, bg="red", fg="white", font=("Helvetica", 10, "bold"),
                  bd=0, relief="flat", highlightthickness=0, width=10).pack(pady=10,padx=10, anchor="w")

        tk.Label(left_frame, text="Sites installés:", bg="#1a2437", fg="white", font=("Helvetica", 16, "bold")).pack(pady=10)
        self.canvas = tk.Canvas(left_frame, height=200, bg="#1a2437", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sites_frame = tk.Frame(self.canvas, bg="#1a2437")
        self.canvas.create_window((0, 0), window=self.sites_frame, anchor=tk.NW)
        self.sites_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Right frame widgets
        tk.Label(right_frame, text="Ajouter un projet:", bg="#1a2437", fg="white", font=("Helvetica", 12, "bold")).pack(pady=10)
        tk.Label(right_frame, text="Nom du projet:", bg="#1a2437", fg="white", font=("Helvetica", 10), width=20 , justify="left").pack(pady=1)
        tk.Entry(right_frame, textvariable=self.project_name_var,width=20 ,font=("Helvetica", 10)).pack(pady=5)
        self.loading_label = tk.Label(right_frame, text="", fg="red", bg="#1a2437")
        self.loading_label.pack(pady=10)

        for text, command in [
            ("WordPress", self.create_wordpress_project),
            ("Laravel", self.create_laravel_project),
            ("GitHub", self.create_from_github),
            ("Scratch", self.create_from_scratch)
        ]:
            tk.Button(right_frame, text=text, command=command, bg="#cdd9ea", fg="black", font=("Helvetica", 10, "bold"),
                      bd=0, relief="flat", highlightthickness=0, width=20).pack(pady=5, padx=10, ipadx=10)



        # Logs frame widgets
        self.log_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, width=40, height=15, state=tk.DISABLED)
        self.log_text.pack(pady=10)


        # Custom scrollbar style
        style = ttk.Style()
        style.configure("Vertical.TScrollbar",
                        gripcount=0,
                        background="#333333",
                        troughcolor="#666666",
                        arrowcolor="#FFFFFF",
                        bordercolor="#333333",
                        lightcolor="#666666",
                        darkcolor="#333333")
        style.map("Vertical.TScrollbar",
                  background=[("active", "#444444")])

    def toggle_logs(self):
            if self.logs_visible:
                self.log_text.pack(pady=10)
            else:
                self.log_text.pack_forget()

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def set_loading(self, is_loading):
        if self.logs_visible:
            return 0

        if is_loading:
            if not self.loading_overlay:
                self.loading_overlay = tk.Frame(self, bg='black')
                self.loading_overlay.place(relwidth=1, relheight=1, anchor=tk.NW)

                canvas = tk.Canvas(self.loading_overlay, bg='black', highlightthickness=0)
                canvas.pack(fill=tk.BOTH, expand=True)
                canvas.create_rectangle(0, 0, 1, 1, fill='black', stipple='gray25')

                loading_text = tk.Label(self.loading_overlay, text="Chargement en cours...", fg="white", bg="black", font=("Helvetica", 16, "bold"))
                loading_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

                self.loading_overlay.lift()
                self.loading_overlay.focus_set()
        else:
            if self.loading_overlay:
                self.loading_overlay.place_forget()
                self.loading_overlay = None

    def validate_project_name(self, project_name):
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
                self.run_command(f"mkdir -p sites/{project_name}")
                os.chdir(f"sites/{project_name}")
                self.run_command("curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar")
                self.run_command("chmod +x wp-cli.phar")
                self.run_command("sudo mv wp-cli.phar /usr/local/bin/wp")
                self.run_command("wp core download")
                self.run_command("wp config create --dbname=db --dbuser=db --dbpass=db --dbhost=db --skip-check")
                self.run_command("rm wp-cli.phar")
                self.ddev_init(project_name, "apache-fpm", "mysql:8.0")
                messagebox.showinfo("Succès", f"Projet WordPress créé avec succès. Accessible à l'adresse: https://{project_name}.ddev.site")
                self.update_sites_list()
            except Exception as e:
                os.chdir(f"../../")
                messagebox.showerror("Erreur", str(e))

    def create_laravel_project(self):
        self.execute_in_thread(self._create_laravel_project)

    def _create_laravel_project(self):
        project_name = self.project_name_var.get()
        if self.validate_project_name(project_name) and self.check_prerequisites():
            try:
                self.run_command(f"mkdir -p sites/{project_name}")
                os.chdir(f"sites/{project_name}")
                self.run_command("composer create-project --prefer-dist laravel/laravel .")
                self.update_laravel_env(project_name)
                self.ddev_init(project_name, "apache-fpm", "mysql:8.0")
                messagebox.showinfo("Succès", "Projet Laravel créé avec succès.")
                self.update_sites_list()
            except Exception as e:
                os.chdir(f"../../")
                messagebox.showerror("Erreur", str(e))

    def create_from_github(self):
        self.execute_in_thread(self._create_from_github)

    def _create_from_github(self):
        project_name = self.project_name_var.get()
        if self.validate_project_name(project_name) and self.check_prerequisites():
            repo_link = tk.simpledialog.askstring("Lien GitHub", "Lien vers le GitHub:")
            if repo_link:
                try:
                    self.run_command(f"mkdir -p sites/{project_name}")
                    os.chdir(f"sites/{project_name}")
                    self.run_command(f"git clone --recursive {repo_link} .")
                    self.ddev_init(project_name, "apache-fpm", "mysql:8.0")
                    messagebox.showinfo("Succès", "Projet créé depuis GitHub avec succès.")
                    self.update_sites_list()  # Mettre à jour la liste des sites
                except Exception as e:
                    os.chdir(f"../../")
                    messagebox.showerror("Erreur", str(e))

    def create_from_scratch(self):
        self.execute_in_thread(self._create_from_scratch)

    def _create_from_scratch(self):
        project_name = self.project_name_var.get()
        if self.validate_project_name(project_name) and self.check_prerequisites():
            try:
                self.run_command(f"mkdir -p sites/{project_name}")
                os.chdir(f"sites/{project_name}")
                with open("index.php", "w") as file:
                    file.write("<?php echo 'Hello World'; ?>")
                self.ddev_init(project_name, "apache-fpm", "mysql:8.0")
                messagebox.showinfo("Succès", "Projet créé from Scratch avec succès.")
                self.update_sites_list()  # Mettre à jour la liste des sites
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

    def ddev_init(self, project_name, webserver_type, database):
        self.run_command(f"pwd")
        self.run_command(f"ddev config --project-name={project_name}")
        self.run_command(f"ddev config --webserver-type={webserver_type}")
        self.run_command(f"ddev config --database={database}")
        self.run_command("ddev get ddev/ddev-phpmyadmin")
        self.run_command("ddev start")
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

    def update_sites_list(self):
        """Met à jour la liste des sites dans le Frame."""
        for widget in self.sites_frame.winfo_children():
            widget.destroy()

        sites_dir = './sites'
        if os.path.exists(sites_dir):
            for site_name in os.listdir(sites_dir):
                site_path = os.path.join(sites_dir, site_name)
                if os.path.isdir(site_path):
                    site_frame = tk.Frame(self.sites_frame, bg="#1a2437")
                    site_frame.pack(fill=tk.X, pady=5)
                    circle_color = "red"
                    status = self.get_ddev_status(site_name)
                    if status:
                        circle_color = "green"
                    circle = tk.Canvas(site_frame, width=20, height=20, bg="#1a2437", highlightthickness=0)
                    circle.create_oval(5, 5, 15, 15, fill=circle_color, outline=circle_color)
                    circle.pack(side=tk.LEFT, padx=5)

                    tk.Label(site_frame, text=site_name, bg="#1a2437", fg="white").pack(side=tk.LEFT, padx=5)

                    if status:
                        tk.Button(site_frame, text="Open on browser", command=lambda s=site_name: self.open_browser(s), bg="#cdd9ea", fg='black',bd=0, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
                        tk.Button(site_frame, text="Open PMA", command=lambda s=site_name: self.open_browser(s,True), bg="#cdd9ea", fg='black',bd=0, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
                        tk.Button(site_frame, text="Stop", command=lambda s=site_name: self.stop_site(s), bg="#660000",fg='#fff', bd=0 ,font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
                    else:
                        tk.Button(site_frame, text="Start", command=lambda s=site_name: self.start_site(s), bg="#228B22",fg='#fff', bd=0, borderwidth=0, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
                        tk.Button(site_frame, text="Delete", command=lambda s=site_name: self.delete_site(s), bg="#ff0000",fg='#fff', bd=0, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

    def get_ddev_status(self, project_name):
        try:
            command = f"ddev list | grep '{project_name}' | awk '{{print $4}}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            status = result.stdout.strip()
            self.log(status)
            if "OK" in status:
                return True

            return False
        except subprocess.CalledProcessError as e:
            self.log(e.stderr.decode())
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
                    self.run_command("ddev start")
                    self.run_command("ddev launch")
                elif action == 'stop':
                    self.run_command("ddev stop")
                os.chdir('../../')
                self.update_sites_list()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la gestion du site {site_name}: {e}")

    def _delete_site(self, site_name):
        site_path = os.path.join('./sites', site_name)
        if os.path.exists(site_path):
            if self.demande_confirmation(f"Êtes-vous sûr de vouloir supprimer le site {site_name} ?"):
                try:
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

if __name__ == "__main__":
    app = ProjectManager()
    app.mainloop()
