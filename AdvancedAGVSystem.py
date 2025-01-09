import sys
import qrcode
import cv2
from PIL import Image
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from datetime import datetime
import numpy as np

class AGVSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem AGV ")
        self.setGeometry(100, 100, 1200, 800)
        # Inisialisasi variabel untuk video capture
        self.capture = None
        self.timer = None
        self.initUI()
        
    def initUI(self):
        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Header dengan logo dan judul
        header_layout = QHBoxLayout()
        
        # Logo (placeholder)
        logo_label = QLabel()
        logo_label.setFixedSize(60, 60)
        logo_label.setStyleSheet("""
            background-color: #2C3E50;
            border-radius: 30px;
            color: white;
            font-weight: bold;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setText("AGV")
        header_layout.addWidget(logo_label)
        
        # Judul dengan gaya modern
        title = QLabel("Sistem AGV ")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
            margin: 10px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Jam digital
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            font-size: 20px;
            color: #2C3E50;
        """)
        self.updateTime()
        
        # Timer untuk update jam
        timer = QTimer(self)
        timer.timeout.connect(self.updateTime)
        timer.start(1000)
        
        header_layout.addWidget(self.time_label)
        layout.addLayout(header_layout)
        
        # Tab widget dengan gaya modern
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: black;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: black;
                border-bottom-color: black;
            }
        """)
        
        # Tab 1: Generator QR Code
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        
        # Form untuk generator QR dalam group box
        qr_group = QGroupBox("Generator QR Code")
        qr_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solidrgb(0, 0, 0);
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 3px;
            }
        """)
        qr_form_layout = QFormLayout()
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Masukkan lokasi tujuan")
        self.location_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
        self.speed_input = QSpinBox()
        self.speed_input.setRange(1, 100)
        self.speed_input.setValue(50)
        self.speed_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Normal", "Penting", "Darurat"])
        self.priority_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
        qr_form_layout.addRow("Lokasi Tujuan:", self.location_input)
        qr_form_layout.addRow("Kecepatan AGV (cm/s):", self.speed_input)
        qr_form_layout.addRow("Prioritas:", self.priority_combo)
        
        generate_btn = QPushButton("Buat QR Code")
        generate_btn.clicked.connect(self.generate_qr)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00000;
            }
        """)
        qr_form_layout.addRow("", generate_btn)
        
        qr_group.setLayout(qr_form_layout)
        tab1_layout.addWidget(qr_group)
        
        # Preview QR
        self.qr_preview = QLabel()
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solidrgb(0, 0, 0);
                border-radius: 4px;
                padding: 10px;
            }
        """)
        tab1_layout.addWidget(self.qr_preview)
        
        tab1.setLayout(tab1_layout)
        tabs.addTab(tab1, "Buat QR Code")
        
        # Tab 2: Scanner QR/Barcode
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        
        # Grup untuk kontrol kamera
        camera_group = QGroupBox("Scanner QR/Barcode")
        camera_layout = QVBoxLayout()
        
        # Label untuk tampilan kamera
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 2px solidrgb(0, 0, 0);
                border-radius: 4px;
                background-color:rgb(0, 0, 0);
            }
        """)
        camera_layout.addWidget(self.camera_label)
        
        # Tombol kontrol kamera
        camera_controls = QHBoxLayout()
        
        start_camera_btn = QPushButton("Mulai Kamera")
        start_camera_btn.clicked.connect(self.start_camera)
        stop_camera_btn = QPushButton("Hentikan Kamera")
        stop_camera_btn.clicked.connect(self.stop_camera)
        
        for btn in [start_camera_btn, stop_camera_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2C3E50;
                    color: white;
                    padding: 10px;
                    border: none;
                    border-radius: 4px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #34495E;
                }
            """)
        
        camera_controls.addWidget(start_camera_btn)
        camera_controls.addWidget(stop_camera_btn)
        camera_layout.addLayout(camera_controls)
        
        # Label untuk hasil scan
        self.scan_result = QLabel("Hasil Scan: -")
        self.scan_result.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 10px;
                background-color: white;
                border: 1px solidrgb(0, 0, 0);
                border-radius: 4px;
            }
        """)
        camera_layout.addWidget(self.scan_result)
        
        camera_group.setLayout(camera_layout)
        tab2_layout.addWidget(camera_group)
        tab2.setLayout(tab2_layout)
        tabs.addTab(tab2, "Scanner QR/Barcode")
        
        # Tab 3: Monitoring AGV
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        
        # Grup untuk tabel status
        status_group = QGroupBox("Status AGV Real-time")
        status_layout = QVBoxLayout()
        
        # Tabel status AGV dengan gaya modern
        self.status_table = QTableWidget(4, 5)
        self.status_table.setHorizontalHeaderLabels(["ID AGV", "Lokasi", "Status", "Baterai", "Waktu Update"])
        self.status_table.setStyleSheet("""
            QTableWidget {
                border: 1px solidrgb(0, 0, 0);
                border-radius: 4px;
                background-color: black;
            }
            QHeaderView::section {
                background-color: #2C3E50;
                color: white;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        # Atur lebar kolom
        header = self.status_table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Isi contoh data
        demo_data = [
            ("AGV-01", "Loading Bay", "Bergerak", "85%", "Just now"),
            ("AGV-02", "Warehouse", "Menunggu", "92%", "2 min ago"),
            ("AGV-03", "Assembly", "Charging", "30%", "5 min ago"),
            ("AGV-04", "Packaging", "Maintenance", "0%", "10 min ago")
        ]
        
        for i, (agv_id, loc, status, bat, time) in enumerate(demo_data):
            self.status_table.setItem(i, 0, QTableWidgetItem(agv_id))
            self.status_table.setItem(i, 1, QTableWidgetItem(loc))
            self.status_table.setItem(i, 2, QTableWidgetItem(status))
            self.status_table.setItem(i, 3, QTableWidgetItem(bat))
            self.status_table.setItem(i, 4, QTableWidgetItem(time))
        
        status_layout.addWidget(self.status_table)
        
        # Tombol refresh
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_status)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
        """)
        status_layout.addWidget(refresh_btn)
        
        status_group.setLayout(status_layout)
        tab3_layout.addWidget(status_group)
        tab3.setLayout(tab3_layout)
        tabs.addTab(tab3, "Monitor AGV")
        
        # Tab 4: Riwayat Pergerakan
        tab4 = QWidget()
        tab4_layout = QVBoxLayout()
        
        # Grup untuk riwayat
        history_group = QGroupBox("Riwayat Pergerakan AGV")
        history_layout = QVBoxLayout()
        
        # Tabel riwayat
        self.history_table = QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels([
            "Waktu", "ID AGV", "Dari", "Ke", "Status", "Durasi"
        ])
        self.history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #2C3E50;
                color: white;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        # Atur lebar kolom riwayat
        header = self.history_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        history_layout.addWidget(self.history_table)
        
        # Filter riwayat
        filter_layout = QHBoxLayout()
        
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
        self.agv_filter = QComboBox()
        self.agv_filter.addItems(["Semua AGV", "AGV-01", "AGV-02", "AGV-03", "AGV-04"])
        self.agv_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
        filter_layout.addWidget(QLabel("Tanggal:"))
        filter_layout.addWidget(self.date_filter)
        filter_layout.addWidget(QLabel("AGV:"))
        filter_layout.addWidget(self.agv_filter)
        
        filter_btn = QPushButton("Terapkan Filter")
        filter_btn.clicked.connect(self.apply_history_filter)
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
        """)
        filter_layout.addWidget(filter_btn)
        
        history_layout.addLayout(filter_layout)
        
        # Tambah tombol export
        export_btn = QPushButton("Export ke Excel")
        export_btn.clicked.connect(self.export_history)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
        """)
        history_layout.addWidget(export_btn)
        
        history_group.setLayout(history_layout)
        tab4_layout.addWidget(history_group)
        tab4.setLayout(tab4_layout)
        tabs.addTab(tab4, "Riwayat")
        
        layout.addWidget(tabs)
        main_widget.setLayout(layout)
        
        # Inisialisasi data riwayat contoh
        self.load_demo_history()
        
    def updateTime(self):
        """Update jam digital"""
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        display_text = f"{current_date.toString('dd/MM/yyyy')} {current_time.toString('HH:mm:ss')}"
        self.time_label.setText(display_text)
        
    def generate_qr(self):
        """Membuat QR Code sesuai dengan input"""
        if not self.location_input.text():
            QMessageBox.warning(self, "Peringatan", "Masukkan lokasi tujuan!")
            return
            
        # Gabungkan data
        data = f"LOC:{self.location_input.text()}|SPD:{self.speed_input.value()}|PRI:{self.priority_combo.currentText()}"
        
        # Buat QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Konversi ke gambar
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Buat direktori jika belum ada
        if not os.path.exists("qr_codes"):
            os.makedirs("qr_codes")
            
        # Simpan QR Code
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qr_codes/qr_{self.location_input.text().replace(' ', '_')}_{timestamp}.png"
        qr_image.save(filename)
        
        # Tampilkan preview
        pixmap = QPixmap(filename)
        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
        self.qr_preview.setPixmap(scaled_pixmap)
        
        QMessageBox.information(self, "Sukses", f"QR Code telah tersimpan di {filename}")
        
    def start_camera(self):
        """Memulai kamera untuk scanning"""
        if self.capture is None:
            self.capture = cv2.VideoCapture(0)
            
        if not self.capture.isOpened():
            QMessageBox.warning(self, "Error", "Tidak dapat mengakses kamera!")
            return
            
        # Mulai timer untuk update frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update setiap 30ms
        
    def stop_camera(self):
        """Menghentikan kamera"""
        if self.timer:
            self.timer.stop()
        if self.capture:
            self.capture.release()
        self.camera_label.clear()
        self.camera_label.setText("Kamera Berhenti")
        
    def update_frame(self):
        """Update frame kamera dan scan QR/barcode"""
        ret, frame = self.capture.read()
        if ret:
            # Scan QR/barcode
            decoded_objects = self.scan_codes(frame)
            
            # Gambar kotak di sekitar kode yang terdeteksi
            for obj in decoded_objects:
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    cv2.polylines(frame, [hull], True, (0, 255, 0), 2)
                else:
                    for j in range(4):
                        cv2.line(frame, tuple(points[j].astype(int)), tuple(points[(j+1) % 4].astype(int)), (0, 255, 0), 2)
                
                # Update hasil scan
                self.scan_result.setText(f"Hasil Scan: {obj.data.decode('utf-8')}")
            
            # Konversi frame untuk ditampilkan
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.camera_label.size(), Qt.KeepAspectRatio
            )
            self.camera_label.setPixmap(scaled_pixmap)
            
    def scan_codes(self, frame):
        """Scan QR code dan barcode dari frame"""
        try:
            # Konversi ke grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Scan menggunakan zbar
            scanner = cv2.QRCodeDetector()
            retval, decoded_info, points, straight_qrcode = scanner.detectAndDecodeMulti(gray)
            
            if retval:
                return [type('obj', (), {'data': info.encode(), 'polygon': points[i]}) 
                        for i, info in enumerate(decoded_info) if info]
        except Exception as e:
            print(f"Error scanning: {e}")
        return []
        
    def refresh_status(self):
        """Refresh status AGV (simulasi)"""
        statuses = ["Bergerak", "Menunggu", "Charging", "Maintenance"]
        locations = ["Loading Bay", "Warehouse", "Assembly", "Packaging", "QC Area"]
        
        for row in range(self.status_table.rowCount()):
            # Update random status
            status = statuses[np.random.randint(0, len(statuses))]
            self.status_table.setItem(row, 2, QTableWidgetItem(status))
            
            # Update lokasi random
            location = locations[np.random.randint(0, len(locations))]
            self.status_table.setItem(row, 1, QTableWidgetItem(location))
            
            # Update baterai (berkurang 1-5%)
            current_battery = int(self.status_table.item(row, 3).text().replace('%', ''))
            new_battery = max(0, current_battery - np.random.randint(1, 6))
            self.status_table.setItem(row, 3, QTableWidgetItem(f"{new_battery}%"))
            
            # Update waktu
            self.status_table.setItem(row, 4, QTableWidgetItem("Just now"))
            
        QMessageBox.information(self, "Sukses", "Data status telah diperbarui!")
        
    def load_demo_history(self):
        """Muat data riwayat contoh"""
        demo_history = [
            ("2024-01-08 08:00", "AGV-01", "Loading Bay", "Warehouse", "Selesai", "5 min"),
            ("2024-01-08 08:15", "AGV-02", "Warehouse", "Assembly", "Selesai", "8 min"),
            ("2024-01-08 08:30", "AGV-03", "Assembly", "QC Area", "Selesai", "6 min"),
            ("2024-01-08 08:45", "AGV-04", "QC Area", "Packaging", "Selesai", "7 min"),
        ]
        
        self.history_table.setRowCount(len(demo_history))
        for i, (time, agv, source, dest, status, duration) in enumerate(demo_history):
            self.history_table.setItem(i, 0, QTableWidgetItem(time))
            self.history_table.setItem(i, 1, QTableWidgetItem(agv))
            self.history_table.setItem(i, 2, QTableWidgetItem(source))
            self.history_table.setItem(i, 3, QTableWidgetItem(dest))
            self.history_table.setItem(i, 4, QTableWidgetItem(status))
            self.history_table.setItem(i, 5, QTableWidgetItem(duration))
            
    def apply_history_filter(self):
        """Terapkan filter pada riwayat"""
        selected_date = self.date_filter.date().toString("yyyy-MM-dd")
        selected_agv = self.agv_filter.currentText()
        
        # Sembunyikan semua baris
        for row in range(self.history_table.rowCount()):
            self.history_table.hideRow(row)
            
        # Tampilkan baris yang sesuai filter
        for row in range(self.history_table.rowCount()):
            date_match = selected_date in self.history_table.item(row, 0).text()
            agv_match = selected_agv == "Semua AGV" or selected_agv == self.history_table.item(row, 1).text()
            
            if date_match and agv_match:
                self.history_table.showRow(row)
                
    def export_history(self):
        """Export riwayat ke file Excel"""
        try:
            import pandas as pd
            
            # Buat direktori untuk export jika belum ada
            if not os.path.exists("exports"):
                os.makedirs("exports")
            
            # Ambil data dari tabel
            data = []
            for row in range(self.history_table.rowCount()):
                if not self.history_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.history_table.columnCount()):
                        row_data.append(self.history_table.item(row, col).text())
                    data.append(row_data)
            
            # Buat DataFrame
            df = pd.DataFrame(data, columns=[
                "Waktu", "ID AGV", "Dari", "Ke", "Status", "Durasi"
            ])
            
            # Export ke Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exports/riwayat_agv_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "Sukses", f"Data telah diekspor ke {filename}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal mengekspor data: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Set style modern
    app.setStyle("Fusion")
    
    # Terapkan dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.blue)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.black)
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