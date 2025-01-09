import sys
import qrcode
import cv2
from PIL import Image
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os

class AGVSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem AGV Palembang")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        
    def initUI(self):
        # Bikin widget utamo
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Judul dengan gaya wong Palembang
        title = QLabel("Sistem AGV Pabrik Palembang")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)
        
        # Tab widget untuk berbagai fitur
        tabs = QTabWidget()
        
        # Tab 1: Bikin QR Code
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        
        # Kendali untuk bikin QR
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Masukke lokasi tujuan")
        tab1_layout.addWidget(QLabel("Lokasi Tujuan:"))
        tab1_layout.addWidget(self.location_input)
        
        self.speed_input = QSpinBox()
        self.speed_input.setRange(1, 100)
        self.speed_input.setValue(50)
        tab1_layout.addWidget(QLabel("Kecepatan AGV (cm/s):"))
        tab1_layout.addWidget(self.speed_input)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Normal", "Penting", "Darurat"])
        tab1_layout.addWidget(QLabel("Prioritas:"))
        tab1_layout.addWidget(self.priority_combo)
        
        generate_btn = QPushButton("Bikin QR Code")
        generate_btn.clicked.connect(self.generate_qr)
        tab1_layout.addWidget(generate_btn)
        
        # Preview QR
        self.qr_preview = QLabel()
        self.qr_preview.setAlignment(Qt.AlignCenter)
        tab1_layout.addWidget(self.qr_preview)
        
        tab1.setLayout(tab1_layout)
        tabs.addTab(tab1, "Bikin QR Code")
        
        # Tab 2: Pantau AGV
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        
        # Tabel status AGV
        self.status_table = QTableWidget(4, 4)
        self.status_table.setHorizontalHeaderLabels(["ID AGV", "Lokasi", "Status", "Baterei"])
        
        # Isi contoh data
        demo_data = [
            ("AGV-01", "Loading Bay", "Jalan", "85%"),
            ("AGV-02", "Warehouse", "Nunggu", "92%"),
            ("AGV-03", "Assembly", "Charging", "30%"),
            ("AGV-04", "Packaging", "Maintenance", "0%")
        ]
        
        for i, (agv_id, loc, status, bat) in enumerate(demo_data):
            self.status_table.setItem(i, 0, QTableWidgetItem(agv_id))
            self.status_table.setItem(i, 1, QTableWidgetItem(loc))
            self.status_table.setItem(i, 2, QTableWidgetItem(status))
            self.status_table.setItem(i, 3, QTableWidgetItem(bat))
            
        tab2_layout.addWidget(self.status_table)
        tab2.setLayout(tab2_layout)
        tabs.addTab(tab2, "Pantau AGV")
        
        layout.addWidget(tabs)
        main_widget.setLayout(layout)
        
    def generate_qr(self):
        """
        Bikin QR Code sesuai dengan input yang ado
        """
        # Gabungke semua data jadi satu string
        data = f"LOC:{self.location_input.text()}|SPD:{self.speed_input.value()}|PRI:{self.priority_combo.currentText()}"
        
        # Bikin QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Convert ke gambar
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Simpan QR Code
        if not os.path.exists("qr_code"):
            os.makedirs("qr_code")
            
        filename = f"qr_code/qr_{self.location_input.text().replace(' ', '_')}.png"
        qr_image.save(filename)
        
        # Tampilke preview
        pixmap = QPixmap(filename)
        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        self.qr_preview.setPixmap(scaled_pixmap)
        
        QMessageBox.information(self, "Sukses", f"QR Code la tersimpan di {filename}")

def main():
    app = QApplication(sys.argv)
    
    # Set style biar keliatan modern
    app.setStyle("Fusion")
    
    # Bikin dark palette untuk tampilan yang elegan
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    
    app.setPalette(palette)
    
    window = AGVSystem()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()