import os
try:
    os.path.append('/Users/mazeyu/NewEra/DraftSculptor')
except:
    pass
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QLineEdit, QVBoxLayout, QHBoxLayout, QWidget,
                             QScrollArea, QGridLayout, QSizePolicy, QFileDialog)
from PyQt5.QtGui import (QPixmap, QFont, QImage)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PIL import Image, ImageDraw, ImageFont
from utils import *



class ImageLabel(QLabel):
    imageChanged = pyqtSignal()
    sizeChanged = pyqtSignal()
    
    def __init__(self, coord_label, _imgp=None, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.coord_label = coord_label
        self._imgp = _imgp
        self.set_attr()
        
        self.imageChanged.connect(self.update_img)
        self.sizeChanged.connect(self.update_img)
    
    @property
    def imgp(self):
        return self._imgp
    
    def _load_img(self):
        try:
            return Image.open(self.imgp)
        except:
            return None
    
    @imgp.setter
    def imgp(self, new_imgp):
        try:
            self._imgp = new_imgp
            self.img = self._load_img()
            self.imageChanged.emit()
        except:
            self._imgp = None
            self.img = None
    

    
    @pyqtSlot()
    def update_img(self):
        if self._if_load():
            self.pixmap = QPixmap(self.imgp)
            self.scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(self.scaled_pixmap)
            self.setAlignment(Qt.AlignCenter)
            self.set_attr()
        else:
            pass
    
    def set_attr(self):
        if self._if_load():
            self._cal_ratio()
            self._check_case()
        
    def _if_load(self):
        return True if self.imgp else False
    
    def _cal_ratio(self):
        self.w_gt, self.h_gt = self.img.size
        self.r_gt = self.w_gt / self.h_gt  # w_gt / h_gt
        self.w_b, self.h_b = self.width(), self.height()
        self.r_b = self.w_b / self.h_b
    
    def _check_case(self):
        if self.r_gt >= self.r_b:  
            self.case = True    
            self.ox = 0             
            self.oy = (self.h_b - self.w_b / self.r_gt) / 2
            self.r_img = self.w_gt / self.w_b
        else:
            self.case = False
            self.ox = (self.w_b - self.h_b * self.r_gt) / 2
            self.oy = 0
            self.r_img = self.h_gt / self.h_b
    
    def _check_oob(self, x, y):
        if self.case:
            if y >= self.oy and y <= self.h_b - self.oy:
                return True
            else:
                return False
        else:
            if x >= self.ox and x <= self.w_b - self.ox:
                return True
            else:
                return False
    
    def _get_coord(self, x, y):
        if self._if_load():
            if self._check_oob(x, y):
                if self.case:
                    self.x_star = x
                    self.y_star = y - self.oy
                else:
                    self.x_star = x - self.ox
                    self.y_star = y
                self.x_final = self.x_star * self.r_img
                self.y_final = self.y_star * self.r_img
            else:
                self.x_final = -1
                self.y_final = -1
        else:
            self.x_final = -1
            self.y_final = -1
            
    # def update_scaled_pixmap(self):
    #     # 根据标签大小重新调整pixmap
    #     self.scaled_pixmap = self.original_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #     self.setPixmap(self.scaled_pixmap)

    def mouseMoveEvent(self, event):
        mouse_position = event.pos()
        x = mouse_position.x()
        y = mouse_position.y()
        self._get_coord(x, y)
        self.coord_label.setText(f"X: {self.x_final}, Y: {self.y_final}")


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.conf = None
        self.img = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("DraftSculptor")
        self.setGeometry(100, 100, 1100, 700)  # Set size



        # =======================Main Layout=======================
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)  # Main layout space



        # =======================Left Layout=======================
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5) 
        left_layout.setContentsMargins(0, 0, 0, 0)  # No space


        # =========Coord Label=========
        self.coord_label = QLabel(self)
        
        
        # =========Image Label=========
        self.image_label = ImageLabel(self.coord_label, self.img, self)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(self.coord_label)
        main_layout.addLayout(left_layout)



        # =======================Right Layout=======================
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)  
        right_layout.setContentsMargins(0, 0, 0, 0) # No space


        # =========Top three buttons=========
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        self.import_config_button = QPushButton("导入配置", self)
        self.save_config_button = QPushButton("保存配置", self)
        self.import_template_button = QPushButton("导入模版", self)
        self.import_template_button.clicked.connect(self.select_image)
        self.import_config_button.clicked.connect(self.import_config)
        self.save_config_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.import_config_button)
        button_layout.addWidget(self.import_template_button)
        button_layout.addWidget(self.save_config_button)
        right_layout.addLayout(button_layout)


        # =========Detail configs=========
        self.detail_label = QLabel("详细配置", self)
        right_layout.addWidget(self.detail_label)


        # =========Scroll Area=========
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)


        # =========Widget and layout=========
        self.config_widget = QWidget()
        self.config_layout = QGridLayout()
        self.config_layout.setSpacing(5)
        self.config_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        headers = ["文字", "X", "Y", "大小", "字体"]
        for i, header in enumerate(headers):
            label = QLabel(header, self)
            font = QFont()
            font.setBold(True)
            label.setFont(font)
            self.config_layout.addWidget(label, 0, i, alignment=Qt.AlignTop)

        # Example data
        for row in range(1, 100):
            for col in range(5):
                edit = QLineEdit(self)
                edit.setText(f"Example")
                self.config_layout.addWidget(edit, row, col, alignment=Qt.AlignTop)

        self.config_widget.setLayout(self.config_layout)
        self.config_layout.setRowStretch(self.config_layout.rowCount(), 1)

        # set scroll part
        scroll_area.setWidget(self.config_widget)
        right_layout.addWidget(scroll_area)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        
        # =========Scan & Generate button=========
        preview_layout = QHBoxLayout()
        self.preview_button = QPushButton("预览", self)
        self.back_button = QPushButton("还原", self)
        self.generate_button = QPushButton("生成", self)
        
        self.preview_button.clicked.connect(self.preview_image)
        self.back_button.clicked.connect(self.back_image)

        preview_layout.addWidget(self.preview_button)
        preview_layout.addWidget(self.back_button)
        right_layout.addLayout(preview_layout)
        # right_layout.addWidget(self.preview_button)
        right_layout.addWidget(self.generate_button)

        main_layout.addLayout(right_layout)

        # main widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


    def select_image(self):
        default_folder = pjoin(root(), 'assets', 'templates')
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", default_folder, "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            self.image_label.imgp = file_name
            self.img = file_name
    
    def import_config(self):
        default_folder = pjoin(root(), 'configs')
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File", default_folder, "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if file_name:
            df = check_format(file_name)
            self.conf = df
            try:
                if df.empty:
                    return
            except:
                pass

        # Delete formal content 
        for i in reversed(range(self.config_layout.count())):
            if i >= 5:
                widget_to_remove = self.config_layout.itemAt(i).widget()
                if widget_to_remove is not None:
                    widget_to_remove.deleteLater()

        # Show new content
        for row in range(len(df)):
            for col, key in enumerate(["文字", "X", "Y", "大小", "字体"]):
                value = df.iloc[row][key]
                edit = QLineEdit(self)
                edit.setText(str(value))
                self.config_layout.addWidget(edit, row+1, col, alignment=Qt.AlignTop)

    def save_config(self):
        columns = ["文字", "X", "Y", "大小", "字体"]
        data = {col: [] for col in columns}

        # Iterate over the layout to gather the data
        row_count = self.config_layout.rowCount()
        for row in range(1, row_count):
            row_data = []
            for col in range(len(columns)):
                item = self.config_layout.itemAtPosition(row, col)
                if item is not None:
                    widget = item.widget()
                    if isinstance(widget, QLineEdit):
                        row_data.append(widget.text())
                    else:
                        row_data.append("")  # If widget is not a QLineEdit, append an empty string
                else:
                    row_data.append("")  # If item is None, append an empty string
            if any(row_data):  # Only add rows that have data
                for col_name, value in zip(columns, row_data):
                    data[col_name].append(value)

        # Convert the data into a DataFrame
        df = pd.DataFrame(data)

        # Ask the user where to save the file
        default_folder = pjoin(root(), 'configs')
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", default_folder, "Excel Files (*.xlsx);;CSV Files (*.csv)")
        
        if file_name:
            try:
                if file_name.endswith('.xlsx'):
                    df.to_excel(file_name, index=False)
                elif file_name.endswith('.csv'):
                    df.to_csv(file_name, index=False)
                print("Configuration saved successfully!")
            except Exception as e:
                print(f"Failed to save configuration: {e}")

    def preview_image(self):
        default_path = pjoin(root(), 'tmp', 'preview.png')
        try:
            flag = draw(self.img, self.conf, default_path)
            if flag:
                self.preview_imgp = default_path
                self.image_label.imgp = self.preview_imgp
        except:
            print("Load fail!")
    
    def back_image(self):
        try:
            self.image_label.imgp = self.img
        except:
            print("Back fail!")
        

    def show_image():
        pass

    def generate_image(self):
        # 生成最终图像逻辑
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageEditor()
    ex.show()
    sys.exit(app.exec_())
