import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QTextEdit, QCheckBox, QLineEdit, 
                             QLabel, QGroupBox, QRadioButton, QFileDialog, QMessageBox, 
                             QFrame, QSplitter, QAbstractItemView, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal

class ModernRenamer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(".: Yeniden Adlandırıcı [Renamer] :.")
        self.setMinimumSize(1000, 750)
        
        # Stylesheet (Modern Light Theme)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                color: #212121;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 12px;
            }
            QGroupBox {
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                background-color: #ffffff;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #1976D2;
                top: 5px;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 12px;
                color: #212121;
            }
            QPushButton:hover {
                background-color: #d5d5d5;
                border-color: #1976D2;
            }
            QPushButton#primaryBtn {
                background-color: #1976D2;
                border-color: #1565C0;
                font-weight: bold;
                color: white;
            }
            QPushButton#primaryBtn:hover {
                background-color: #1E88E5;
            }
            QPushButton#dangerBtn {
                background-color: #d32f2f;
                border-color: #b71c1c;
                font-weight: bold;
                color: white;
            }
            QPushButton#dangerBtn:hover {
                background-color: #e53935;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                color: #212121;
            }
            QLineEdit:focus {
                border-color: #1976D2;
            }
            QListWidget, QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 5px;
                selection-background-color: #bbdefb;
                selection-color: #0d47a1;
            }
            QCheckBox, QRadioButton {
                color: #212121;
                padding: 2px 8px;
                min-height: 24px;
                spacing: 10px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #9e9e9e;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 3px solid #ffffff;
            }
            QRadioButton::indicator:checked {
                background-color: #1976D2;
                border: 5px solid #ffffff;
            }
            QCheckBox:hover, QRadioButton:hover {
                background-color: #f0f0f0;
                border-radius: 6px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Splitting Left (List) and Right (Settings)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- LEFT PANEL: File Lists ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        file_list_label = QLabel("Adlandırılacak Dosyalar")
        file_list_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        left_layout.addWidget(file_list_label)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setAcceptDrops(True)
        
        # Override drag & drop events
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dragMoveEvent = self.dragMoveEvent
        self.file_list.dropEvent = self.dropEvent
        
        left_layout.addWidget(self.file_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Dosya Ekle")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove = QPushButton("Seçiliyi Çıkar")
        self.btn_remove.setObjectName("dangerBtn")
        self.btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_up = QPushButton("↑ Yukarı")
        self.btn_up.setFixedWidth(80)
        self.btn_up.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_down = QPushButton("↓ Aşağı")
        self.btn_down.setFixedWidth(80)
        self.btn_down.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_reverse = QPushButton("⇆ Ters Çevir")
        self.btn_reverse.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        btn_layout.addWidget(self.btn_reverse)
        btn_layout.addWidget(self.btn_remove)
        left_layout.addLayout(btn_layout)
        
        preview_label = QLabel("Yeni İsim Önizleme")
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 10px;")
        left_layout.addWidget(preview_label)
        
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("Yapılan Değişiklikler Otomatik Olarak Önizleme Ekranında Görünecektir.")
        left_layout.addWidget(self.preview_area)
        
        # --- RIGHT PANEL: Settings with ScrollArea ---
        right_container = QWidget()
        right_main_layout = QVBoxLayout(right_container)
        right_container.setMinimumWidth(400)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        right_layout = QVBoxLayout(scroll_content)
        right_layout.setSpacing(8) 
        
        # Settings Title & About Button
        header_layout = QHBoxLayout()
        settings_title = QLabel("Yeniden Adlandırma Ayarları")
        settings_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        
        self.btn_about = QPushButton("Hakkında")
        self.btn_about.setFixedSize(80, 30)
        self.btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about.setStyleSheet("font-size: 11px; background-color: #f0f0f0; color: #666666;")
        
        header_layout.addWidget(settings_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_about)
        right_layout.addLayout(header_layout)

        # 1. Sıfırdan Adlandır
        self.group_scratch = QGroupBox("Sıfırdan Adlandır")
        self.group_scratch.setCheckable(True)
        self.group_scratch.setChecked(False)
        scratch_layout = QVBoxLayout()
        self.txt_scratch_name = QLineEdit()
        self.txt_scratch_name.setPlaceholderText("Yeni dosya adı...")
        scratch_layout.addWidget(QLabel("Yeni İsim:"))
        scratch_layout.addWidget(self.txt_scratch_name)
        self.group_scratch.setLayout(scratch_layout)
        right_layout.addWidget(self.group_scratch)

        # 2. Sıralı Numaralandır
        self.group_sequence = QGroupBox("Sıralı Numaralandır")
        self.group_sequence.setCheckable(True)
        self.group_sequence.setChecked(False)
        seq_layout = QHBoxLayout()
        self.txt_seq_start = QLineEdit("1")
        self.txt_seq_start.setFixedWidth(50)
        self.txt_seq_start.setFixedHeight(25)
        seq_layout.addWidget(QLabel("Başlangıç:"))
        seq_layout.addWidget(self.txt_seq_start)
        seq_layout.addStretch()
        self.group_sequence.setLayout(seq_layout)
        right_layout.addWidget(self.group_sequence)

        # 3. Değiştir / Yerine Koy
        self.group_replace = QGroupBox("Değiştir / Yerine Koy")
        self.group_replace.setCheckable(True)
        self.group_replace.setChecked(False)
        replace_layout = QVBoxLayout()
        self.txt_find = QLineEdit()
        self.txt_find.setPlaceholderText("Aranan Değer...")
        self.txt_replace = QLineEdit()
        self.txt_replace.setPlaceholderText("Yeni Değer...")
        replace_layout.addWidget(QLabel("Bul:"))
        replace_layout.addWidget(self.txt_find)
        replace_layout.addWidget(QLabel("Yerine Koy:"))
        replace_layout.addWidget(self.txt_replace)
        self.group_replace.setLayout(replace_layout)
        right_layout.addWidget(self.group_replace)

        # 4. Karakter Sil
        self.group_delete = QGroupBox("Karakter / Kelime Sil")
        self.group_delete.setCheckable(True)
        self.group_delete.setChecked(False)
        delete_layout = QVBoxLayout()
        self.txt_delete = QLineEdit()
        self.txt_delete.setPlaceholderText("Silinecek metin...")
        self.chk_each_char = QCheckBox("Yazılan karakterleri tek tek sil")
        delete_layout.addWidget(self.txt_delete)
        delete_layout.addWidget(self.chk_each_char)
        self.group_delete.setLayout(delete_layout)
        right_layout.addWidget(self.group_delete)

        # 5. Harf Durumu (Radio)
        harf_group = QGroupBox("Metin Manipülasyonu")
        harf_layout = QVBoxLayout()
        harf_layout.setSpacing(0) # Radio butonlar arası mesafe minimuma indirildi
        harf_layout.setContentsMargins(15, 15, 15, 5) 
        self.radio_none = QRadioButton("Değiştirme (Varsayılan)")
        self.radio_none.setChecked(True)
        self.radio_lower = QRadioButton("küçük harf")
        self.radio_upper = QRadioButton("BÜYÜK HARF")
        self.radio_title = QRadioButton("Kelimelerin Baş Harfleri Büyük")
        self.radio_swap = QRadioButton("hARFLERİ tERS çEVİR")
        self.radio_reverse = QRadioButton("İsmi Ters Çevir (Örn: 123.jpg -> 321.jpg)")
        
        harf_layout.addWidget(self.radio_none)
        harf_layout.addWidget(self.radio_lower)
        harf_layout.addWidget(self.radio_upper)
        harf_layout.addWidget(self.radio_title)
        harf_layout.addWidget(self.radio_swap)
        harf_layout.addWidget(self.radio_reverse)
        harf_group.setLayout(harf_layout)
        right_layout.addWidget(harf_group)

        # 6. Ön Ek / Son Ek
        ek_group = QGroupBox("Eklentiler")
        ek_layout = QVBoxLayout()
        ek_layout.setSpacing(5)
        ek_layout.setContentsMargins(15, 20, 15, 10)
        self.chk_prefix = QCheckBox("Ön Ek Ekle:")
        self.txt_prefix = QLineEdit()
        self.txt_prefix.setPlaceholderText("Ör: Proje_")
        self.txt_prefix.setEnabled(False)
        self.chk_suffix = QCheckBox("Son Ek Ekle:")
        self.txt_suffix = QLineEdit()
        self.txt_suffix.setPlaceholderText("Ör: _v1")
        self.txt_suffix.setEnabled(False)
        
        ek_layout.addWidget(self.chk_prefix)
        ek_layout.addWidget(self.txt_prefix)
        ek_layout.addWidget(self.chk_suffix)
        ek_layout.addWidget(self.txt_suffix)
        ek_group.setLayout(ek_layout)
        right_layout.addWidget(ek_group)

        right_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        right_main_layout.addWidget(scroll)

        # Action Buttons (Fixed at bottom)
        action_layout = QHBoxLayout()
        self.btn_preview = QPushButton("ÖNİZLE")
        self.btn_preview.setFixedHeight(45)
        self.btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preview.setVisible(False) # Butonu sakla, artık otomatik önizleme var
        self.btn_apply = QPushButton("UYGULA")
        self.btn_apply.setObjectName("primaryBtn")
        self.btn_apply.setFixedHeight(45)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        
        action_layout.addWidget(self.btn_preview)
        action_layout.addWidget(self.btn_apply)
        right_main_layout.addLayout(action_layout)

        # Splitter add
        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)

    def connect_signals(self):
        # Butonlar
        self.btn_add.clicked.connect(self.add_files)
        self.btn_remove.clicked.connect(self.remove_files)
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        self.btn_reverse.clicked.connect(self.reverse_list)
        self.btn_preview.clicked.connect(self.on_preview)
        self.btn_apply.clicked.connect(self.on_apply)
        self.btn_about.clicked.connect(self.show_about)
        
        # Otomatik Önizleme Bağlantıları
        # 1. Text Değişimleri
        self.txt_find.textChanged.connect(self.on_preview)
        self.txt_replace.textChanged.connect(self.on_preview)
        self.txt_delete.textChanged.connect(self.on_preview)
        self.chk_each_char.toggled.connect(self.on_preview)
        self.txt_prefix.textChanged.connect(self.on_preview)
        self.txt_suffix.textChanged.connect(self.on_preview)
        self.txt_seq_start.textChanged.connect(self.on_preview)
        
        # 2. Checkbox ve GroupBox Değişimleri
        self.group_replace.toggled.connect(self.on_preview)
        self.group_delete.toggled.connect(self.on_preview)
        self.group_sequence.toggled.connect(self.ensure_sequence_if_scratch)
        self.group_sequence.toggled.connect(self.on_preview)
        self.group_scratch.toggled.connect(self.handle_scratch_dependency)
        self.group_scratch.toggled.connect(self.on_preview)
        self.txt_scratch_name.textChanged.connect(self.on_preview)
        
        self.chk_prefix.toggled.connect(self.txt_prefix.setEnabled)
        self.chk_prefix.toggled.connect(self.on_preview)
        
        self.chk_suffix.toggled.connect(self.txt_suffix.setEnabled)
        self.chk_suffix.toggled.connect(self.on_preview)
        
        # 3. Radio Buton Değişimleri
        self.radio_none.toggled.connect(self.on_preview)
        self.radio_lower.toggled.connect(self.on_preview)
        self.radio_upper.toggled.connect(self.on_preview)
        self.radio_title.toggled.connect(self.on_preview)
        self.radio_swap.toggled.connect(self.on_preview)
        self.radio_reverse.toggled.connect(self.on_preview)

    # --- Drag & Drop Support ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        mevcut_dosyalar = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        for f in files:
            if os.path.exists(f) and f not in mevcut_dosyalar:
                self.file_list.addItem(f)
                mevcut_dosyalar.append(f)
        self.on_preview() # Yeni dosyalar gelince önizle

    # --- LOGIC ---
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Dosyaları Seçin")
        if files:
            mevcut_dosyalar = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            for f in files:
                if f not in mevcut_dosyalar:
                    self.file_list.addItem(f)
                    mevcut_dosyalar.append(f)
            self.on_preview() # Dosyalar eklenince önizle

    def remove_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self.on_preview() # Dosyalar silinince önizle

    def move_up(self):
        selected_rows = [self.file_list.row(item) for item in self.file_list.selectedItems()]
        selected_rows.sort()
        
        for row in selected_rows:
            if row > 0:
                item = self.file_list.takeItem(row)
                self.file_list.insertItem(row - 1, item)
                item.setSelected(True)
        self.on_preview()

    def move_down(self):
        selected_rows = [self.file_list.row(item) for item in self.file_list.selectedItems()]
        selected_rows.sort(reverse=True)
        
        for row in selected_rows:
            if row < self.file_list.count() - 1:
                item = self.file_list.takeItem(row)
                self.file_list.insertItem(row + 1, item)
                item.setSelected(True)
        self.on_preview()

    def reverse_list(self):
        items = []
        for i in range(self.file_list.count()):
            items.append(self.file_list.takeItem(0))
        
        for item in reversed(items):
            self.file_list.addItem(item)
        self.on_preview()

    def handle_scratch_dependency(self, checked):
        if checked:
            self.group_sequence.setChecked(True)
        self.on_preview()

    def ensure_sequence_if_scratch(self, checked):
        if not checked and self.group_scratch.isChecked():
            self.group_sequence.setChecked(True)
        self.on_preview()

    def isim_donustur(self, eski_tam_yol, sira=0):
        dizin, eski_isim = os.path.split(eski_tam_yol)
        isim, uzanti = os.path.splitext(eski_isim)
        
        # 0. Sıfırdan Adlandır
        if self.group_scratch.isChecked():
            yeni_isim = self.txt_scratch_name.text()
            if not yeni_isim:
                yeni_isim = "dosya" # Varsayılan isim
        else:
            yeni_isim = isim

        # 1. Değiştir / Yerine Koy
        if self.group_replace.isChecked():
            find_str = self.txt_find.text()
            replace_str = self.txt_replace.text()
            if find_str:
                yeni_isim = yeni_isim.replace(find_str, replace_str)

        # 2. Karakter Sil
        if self.group_delete.isChecked():
            del_str = self.txt_delete.text()
            if del_str:
                if self.chk_each_char.isChecked():
                    # Karakterleri tek tek sil
                    for char in del_str:
                        yeni_isim = yeni_isim.replace(char, "")
                else:
                    # Metni blok olarak sil
                    yeni_isim = yeni_isim.replace(del_str, "")

        # 3. Harf Durumu
        if self.radio_lower.isChecked():
            yeni_isim = yeni_isim.lower()
        elif self.radio_upper.isChecked():
            yeni_isim = yeni_isim.upper()
        elif self.radio_title.isChecked():
            yeni_isim = yeni_isim.title()
        elif self.radio_swap.isChecked():
            yeni_isim = yeni_isim.swapcase()
        elif self.radio_reverse.isChecked():
            yeni_isim = yeni_isim[::-1]

        # 4. Ön Ek
        if self.chk_prefix.isChecked():
            yeni_isim = self.txt_prefix.text() + yeni_isim

        # 5. Son Ek
        if self.chk_suffix.isChecked():
            yeni_isim = yeni_isim + self.txt_suffix.text()

        # 6. Sıralı Numaralandır
        if self.group_sequence.isChecked():
            try:
                start_val = int(self.txt_seq_start.text())
            except:
                start_val = 1
            yeni_isim = f"{yeni_isim}_{start_val + sira}"

        return yeni_isim + uzanti

    def on_preview(self):
        self.preview_area.clear()
        for i in range(self.file_list.count()):
            file_path = self.file_list.item(i).text()
            new_name = self.isim_donustur(file_path, i)
            self.preview_area.append(new_name)

    def on_apply(self):
        count = self.file_list.count()
        if count == 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce dosya ekleyin.")
            return

        reply = QMessageBox.question(self, "Onay", f"{count} dosya yeniden adlandırılacak. Emin misiniz?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            success = 0
            errors = 0
            for i in range(count):
                old_path = self.file_list.item(i).text()
                dizin = os.path.dirname(old_path)
                new_name = self.isim_donustur(old_path, i)
                new_path = os.path.join(dizin, new_name)
                
                try:
                    os.rename(old_path, new_path)
                    self.file_list.item(i).setText(new_path) # Listeyi güncelle
                    success += 1
                except Exception as e:
                    print(f"Hata: {e}")
                    errors += 1
                    QMessageBox.critical(self, "Hata", f"Yeniden adlandırma sırasında hata oluştu:\n{str(e)}")
            
            self.on_preview() # Yeni yollara göre önizlemeyi yenile
            QMessageBox.information(self, "Bitti", f"İşlem tamamlandı.\nBaşarılı: {success}\nHata: {errors}")

    def show_about(self):
        about_text = """
        <h3>Yeniden Adlandırıcı [ Renamer ] v2.2</h3>
        <p>Dosyalarınızı hızlı ve güvenli bir şekilde toplu olarak yeniden adlandırabileceğiniz modern bir araçtır.</p>
        <p><b>Temel Özellikler:</b></p>
        <ul>
            <li>Sıfırdan Adlandırma</li>
            <li>Sıralı Numaralandırma</li>
            <li>Bul ve Değiştir</li>
            <li>Karakter/Kelime Silme</li>
            <li>Metin Manipülasyonu (küçük / BÜYÜK harf dönüşümü, ...vb</li>
            <li>Ön Ek ve Son Ek Ekleme</li>
			<li>Dosya Eklemede Sürükle-Bırak Desteği</li>
			<li>Eklenen Dosyaları CTRL ile tek tek ya da SHIFT ile bir aralıkta Seçme</li>
            <li>Dosya Sıralamasını Değiştirme (Yukarı/Aşağı/Ters)</li>
            <li>Anlık Dinamik Önizleme</li>
        </ul>
        <p><b>Geliştirici Bilgileri:</b></p>
        <ul>
        <li>Geliştirici: Mustafa Halil GÖRENTAŞ</li>
		<li>E-Posta: <a href='mailto:halil.mustafa@gmail.com' style='color: #2563eb; text-decoration: none;'>halil.mustafa@gmail.com</a></li>
        <li>Kaynak Kod: <a href=https://github.com/mhalil/YenidenAdlandir_Renamer>github.com/mhalil/YenidenAdlandir_Renamer</a></li>
        </ul>
        <p><b>Teknik Bilgiler:</b></p>
        <ul>
            <li>Platform: Google Antigravity</li>
            <li>Metodoloji: Vibe Coding</li>
            <li>Teknoloji: Python 3.12.4, PyQt6 (Riverbank Computing) ve Qt Framework (The Qt Company).</li>
        </ul>
        GPL Lisansı Altında Dağıtılmaktadır. | 2026
        </p>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Uygulama Hakkında")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernRenamer()
    window.show()
    sys.exit(app.exec())
