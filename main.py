import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, 
                             QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt

class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("DraftSculptor")
        self.setGeometry(100, 100, 800, 600)  # Set size

        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)  # Main layout space

        # 左侧布局（图像预览框）
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5) 
        left_layout.setContentsMargins(0, 0, 0, 0)  # No space

        self.image_label = QLabel(self)
        self.image_label.setFixedSize(400, 600)
        self.image_label.setStyleSheet("border: 1px solid black;")
        left_layout.addWidget(self.image_label)

        main_layout.addLayout(left_layout)

        # Right Layout
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)  
        right_layout.setContentsMargins(0, 0, 0, 0) # No space

        # Top two buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        self.import_config_button = QPushButton("导入配置", self)
        self.import_template_button = QPushButton("导入模版", self)
        button_layout.addWidget(self.import_config_button)
        button_layout.addWidget(self.import_template_button)
        right_layout.addLayout(button_layout)

        # Detail configs
        self.detail_label = QLabel("详细配置", self)
        right_layout.addWidget(self.detail_label)

        # Scroll part
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Widget and layout
        self.config_widget = QWidget()
        self.config_layout = QGridLayout()
        self.config_layout.setSpacing(5)
        self.config_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        headers = ["文字", "X", "Y", "大小", "字体"]
        for i, header in enumerate(headers):
            label = QLabel(header, self)
            self.config_layout.addWidget(label, 0, i, alignment=Qt.AlignTop)

        # Example data
        for row in range(1, 511):
            for col in range(5):
                edit = QLineEdit(self)
                edit.setText(f"Row{row}Col{col+1}")
                self.config_layout.addWidget(edit, row, col, alignment=Qt.AlignTop)

        self.config_widget.setLayout(self.config_layout)
        self.config_layout.setRowStretch(self.config_layout.rowCount(), 1)


        # set scroll part
        scroll_area.setWidget(self.config_widget)
        scroll_area.setFixedSize(350, 500)  # Scorll size
        right_layout.addWidget(scroll_area)
        

        # Scan & Generate button
        self.preview_button = QPushButton("预览", self)
        self.generate_button = QPushButton("生成", self)
        right_layout.addWidget(self.preview_button)
        right_layout.addWidget(self.generate_button)

        main_layout.addLayout(right_layout)

        # main widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def import_config(self):
        # 导入配置文件逻辑
        pass

    def import_template(self):
        # 导入模版逻辑
        pass

    def preview_image(self):
        # 预览图像逻辑
        pass

    def generate_image(self):
        # 生成最终图像逻辑
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageEditor()
    ex.show()
    sys.exit(app.exec_())
