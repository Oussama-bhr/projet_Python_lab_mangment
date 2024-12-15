import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QListWidget, QHBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt

UPLOAD_DIR = "./uploads"  # Dossier contenant les fichiers téléversés

class AdminInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student_Repertory")
        self.setGeometry(300, 300, 600, 400)

        # Interface
        self.initUI()

    def initUI(self):
        # Layout principal
        self.layout = QVBoxLayout()

        # Label pour le titre
        self.title_label = QLabel("Gestion des fichiers téléversés")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Liste des fichiers téléversés
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        # Boutons pour les actions
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.clicked.connect(self.refresh_file_list)
        button_layout.addWidget(self.refresh_button)

        self.delete_button = QPushButton("Supprimer le fichier")
        self.delete_button.clicked.connect(self.delete_file)
        button_layout.addWidget(self.delete_button)

        self.download_button = QPushButton("Télécharger le fichier")
        self.download_button.clicked.connect(self.download_file)
        button_layout.addWidget(self.download_button)

        self.layout.addLayout(button_layout)

        # Conteneur principal
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Charger la liste des fichiers au démarrage
        self.refresh_file_list()

    def refresh_file_list(self):
        """Rafraîchir la liste des fichiers téléversés."""
        self.file_list.clear()
        if os.path.exists(UPLOAD_DIR):
            files = os.listdir(UPLOAD_DIR)
            self.file_list.addItems(files)
        else:
            QMessageBox.warning(self, "Erreur", f"Le dossier {UPLOAD_DIR} n'existe pas.")

    def delete_file(self):
        """Supprimer le fichier sélectionné."""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_name = selected_item.text()
            file_path = os.path.join(UPLOAD_DIR, file_name)

            try:
                os.remove(file_path)
                QMessageBox.information(self, "Succès", f"Le fichier '{file_name}' a été supprimé.")
                self.refresh_file_list()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le fichier : {e}")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un fichier à supprimer.")

    def download_file(self):
        """Télécharger le fichier sélectionné (copie locale)."""
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_name = selected_item.text()
            file_path = os.path.join(UPLOAD_DIR, file_name)

            # Définir l'endroit où sauvegarder le fichier
            save_path = os.path.join(os.getcwd(), f"Copie_{file_name}")

            try:
                with open(file_path, "rb") as source, open(save_path, "wb") as destination:
                    destination.write(source.read())

                QMessageBox.information(self, "Succès", f"Le fichier '{file_name}' a été copié en tant que '{save_path}'.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de télécharger le fichier : {e}")
        else:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un fichier à télécharger.")

if __name__ == "__main__":
    app = QApplication([])
    admin_interface = AdminInterface()
    admin_interface.show()
    app.exec_()
