import sys
import os
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QRadioButton, QTextEdit
from converter.csvw import CSVWConverter, build_schema, extensions
from rdflib import ConjunctiveGraph

class COWGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('CSV on the Web Converter GUI')
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.mode_label = QLabel('Select Mode:')
        layout.addWidget(self.mode_label)

        self.mode_radio_layout = QHBoxLayout()
        self.mode_radio_convert = QRadioButton('Convert')
        self.mode_radio_build = QRadioButton('Build')
        self.mode_radio_convert.setChecked(True)
        self.mode_radio_layout.addWidget(self.mode_radio_convert)
        self.mode_radio_layout.addWidget(self.mode_radio_build)
        layout.addLayout(self.mode_radio_layout)

        self.file_label = QLabel('Select File:')
        layout.addWidget(self.file_label)

        self.file_button = QPushButton('Browse Files')
        self.file_button.clicked.connect(self.browse_files)
        layout.addWidget(self.file_button)

        self.process_button = QPushButton('Convert/Build')
        self.process_button.clicked.connect(self.process_files)
        layout.addWidget(self.process_button)

        self.output_text_edit = QTextEdit()
        layout.addWidget(self.output_text_edit)

        self.central_widget.setLayout(layout)

        self.files = []
        self.mode = 'convert'  

    def browse_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('CSV Files (*.csv)')
        selected_files, _ = file_dialog.getOpenFileNames(self, 'Select CSV File(s)', '', 'CSV Files (*.csv);;All Files (*)', options=options)
        if selected_files:
            self.files = selected_files
            self.output_text_edit.append(f"Added the file {self.files}")

    def process_files(self):
        if not self.files:
            return

        if self.mode_radio_build.isChecked():
            for file in self.files:
                self.output_text_edit.append(f"Building schema for {file}")
                target_file = f"{file}-metadata.json"

                if os.path.exists(target_file):
                    new_filename = f"{os.path.splitext(target_file)[0]}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                    os.rename(target_file, new_filename)
                    self.output_text_edit.append(f"Backed up prior version of schema to {new_filename}")

                build_schema(file, target_file, dataset_name=None, delimiter=None, encoding=None, quotechar='\"', base="https://example.com/id/")
                self.output_text_edit.append(f"Schema built and saved as {target_file}")
        elif self.mode_radio_convert.isChecked():
            for file in self.files:
                self.output_text_edit.append(f"Converting {file} to RDF")
                try:
                    c = CSVWConverter(file, delimiter = None, quotechar='\"', encoding = None, processes=4, chunksize=5000, output_format='nquads', base="https://example.com/id/")
                    c.convert()

                    quads_filename = f"{file}.nq"
                    new_filename = f"{os.path.splitext(file)[0]}.rdf"

                    with open(quads_filename, 'rb') as nquads_file:
                        g = ConjunctiveGraph()
                        g.parse(nquads_file, format='nquads')

                    with open(new_filename, 'wb') as output_file:
                        g.serialize(destination=output_file, format='xml')

                    self.output_text_edit.append(f"Conversion completed and saved as {new_filename}")

                except Exception as e:
                    self.output_text_edit.append(f"Something went wrong while processing {file}: {str(e)}")

def main():
    app = QApplication(sys.argv)
    gui = COWGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
