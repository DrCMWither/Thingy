import sys
from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QLabel,
                             QLineEdit,
                             QVBoxLayout,
                             QGridLayout,
                             QFormLayout,
                             QPushButton,
                             QCheckBox,
                             QGroupBox,
                             QTextEdit)
from PyQt5.QtCore    import (Qt,
                             QTimer)
import pyaudio
import numpy as np
import pyqtgraph as pg


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Mixer")

layout = QVBoxLayout()
window.setLayout(layout)

grid_layout = QGridLayout()
layout.addLayout(grid_layout)

plot = pg.PlotWidget()
grid_layout.addWidget(plot, 0, 1)

form_layout = QFormLayout()
grid_layout.addLayout(form_layout, 0, 0)

custom_input_edit = QTextEdit()
custom_input_edit.setPlaceholderText("Enter Sine Waves (Frequency, Amplitude) per Line\n")
grid_layout.addWidget(custom_input_edit, 1, 0)

mute_group_box =        QGroupBox("Mute")
mute_group_box_layout = QVBoxLayout()
mute_group_box.setLayout(mute_group_box_layout)

mute_predefined_waves_checkbox = QCheckBox("Predefined Waves")
mute_custom_waves_checkbox =     QCheckBox("Custom Waves"    )

mute_group_box_layout.addWidget(mute_predefined_waves_checkbox)
mute_group_box_layout.addWidget(mute_custom_waves_checkbox    )

grid_layout.addWidget(mute_group_box, 1, 1)


freq_line_edits    = []
amp_line_edits     = []
enable_checkboxes  = []
enabled_waves      = [True] * 10

enabled_freq_edits = []
enabled_amp_edits  = []

for i in range(10):
    freq_edit = QLineEdit()
    freq_edit.setText("1000")
    amp_edit = QLineEdit()
    amp_edit.setText("50")
    enable_checkbox = QCheckBox("Enabled")
    enable_checkbox.setChecked(True)

    form_layout.addRow(f"Wave{i+1} Freq", freq_edit)
    form_layout.addRow(f"Wave{i+1} Lvl",   amp_edit)
    form_layout.addRow("", enable_checkbox)

    freq_line_edits.append(freq_edit)
    amp_line_edits.append(amp_edit)
    enable_checkboxes.append(enable_checkbox)


play_button = QPushButton("Play")
layout.addWidget(play_button)

tau = 2 * np.pi
fs = 44000

def parse_custom_waves(text):
    custom_waves = []
    for line in text.splitlines():
        try:
            freq, amp = map(float, line.split(","))
            custom_waves.append((freq, amp))
        except ValueError:
            print(f"Invalid format in custom input: {line}")
            return []
    return custom_waves

def update_data():
    t = np.linspace(0, 1, fs, False)
    audio_data = np.zeros(fs)

    predefined_freq_values = [float(freq_edit.text()) for i, freq_edit in enumerate(freq_line_edits)
                              if enabled_waves[i] and not mute_predefined_waves_checkbox.isChecked()]
    predefined_amp_values = [float(amp_edit.text()) for i, amp_edit in enumerate(amp_line_edits)
                              if enabled_waves[i] and not mute_predefined_waves_checkbox.isChecked()]


    custom_waves = parse_custom_waves(custom_input_edit.toPlainText())
    
    if not custom_waves or mute_custom_waves_checkbox.isChecked():
        print("No custom waves provided.")
        custom_freq_values = []
        custom_amp_values =  []
    else:
        custom_freq_values, custom_amp_values = zip(*custom_waves)

    all_freq_values = predefined_freq_values + list(custom_freq_values)
    all_amp_values =  predefined_amp_values  + list(custom_amp_values )

    for freq, amp in zip(all_freq_values, all_amp_values):
        try:
            audio_data += amp / 100  * np.sin(tau * freq * t)
        except ValueError:
            print("Invalid input!")
  
    fft_data = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(audio_data), 1 / fs)
    return audio_data, freqs, fft_data
def update_plot(audio_data, freqs, fft_data):
    plot.clear()
    plot.plot(freqs, np.abs(fft_data))

    plot.setXRange(np.exp(0), np.max(np.abs(freqs)) / 5)
    plot.setYRange(0,         np.max(np.abs(fft_data)) )

    plot.setTitle("Spectrogram"   )
    plot.setLabel('bottom', 'Freq')
    plot.setLabel('left',   'Amp' )

def play_audio():
    global enabled_waves
    enabled_waves = [checkbox.isChecked() for checkbox in enable_checkboxes]
    
    audio_data, freqs, fft_data = update_data()
    update_plot(audio_data, freqs, fft_data)

    stream = p.open(format = pyaudio.paFloat32, channels = 1, rate = fs, output = True)
    stream.write(audio_data.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()

p = pyaudio.PyAudio()


for freq_edit, amp_edit in zip(freq_line_edits, amp_line_edits):
    freq_edit.textChanged.connect(update_data)
    amp_edit.textChanged.connect (update_data)

def update_enable_checkboxes(state):

  for checkbox in enable_checkboxes:
    checkbox.setEnabled(not state) 

mute_predefined_waves_checkbox.stateChanged.connect(update_enable_checkboxes)

for checkbox in enable_checkboxes:
    checkbox.stateChanged.connect(lambda state, checkbox = checkbox: update_enabled_waves(checkbox))

def update_enabled_waves(checkbox):
    global enabled_waves
    index = enable_checkboxes.index(checkbox)
    enabled_waves[index] = checkbox.isChecked()

play_button.clicked.connect(play_audio)

audio_data, freqs, fft_data = update_data()
update_plot(audio_data, freqs, fft_data)

window.show()
sys.exit(app.exec_())
