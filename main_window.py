from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QLabel, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QTabWidget, QTextEdit, QFileDialog, QSplitter,
                             QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from opengl_widget import OpenGLWidget
import json
import time
import os
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PerformanceChartWidget(FigureCanvas):
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout(pad=3.0)
        
    def plot_line_comparison(self, data):
        self.axes.clear()
        for algo, results in data.items():
            if results:
                x_vals = sorted(results.keys())
                y_vals = [results[x] for x in x_vals]
                self.axes.plot(x_vals, y_vals, marker='o', label=algo, linewidth=2)
        self.axes.set_xlabel('Line Length (pixels)', fontsize=10)
        self.axes.set_ylabel('Time (milliseconds)', fontsize=10)
        self.axes.set_title('Line Drawing Algorithms Performance', fontsize=12, fontweight='bold')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)
        self.draw()
        
    def plot_circle_comparison(self, data):
        self.axes.clear()
        for algo, results in data.items():
            if results:
                x_vals = sorted(results.keys())
                y_vals = [results[x] for x in x_vals]
                self.axes.plot(x_vals, y_vals, marker='s', label=algo, linewidth=2)
        self.axes.set_xlabel('Circle Radius (pixels)', fontsize=10)
        self.axes.set_ylabel('Time (milliseconds)', fontsize=10)
        self.axes.set_title('Circle Drawing Algorithms Performance', fontsize=12, fontweight='bold')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)
        self.draw()
        
    def plot_clip_comparison(self, data):
        self.axes.clear()
        for algo, results in data.items():
            if results:
                x_vals = sorted(results.keys())
                y_vals = [results[x] for x in x_vals]
                self.axes.plot(x_vals, y_vals, marker='^', label=algo, linewidth=2)
        self.axes.set_xlabel('Polygon Vertices', fontsize=10)
        self.axes.set_ylabel('Time (milliseconds)', fontsize=10)
        self.axes.set_title('Clipping Algorithms Performance', fontsize=12, fontweight='bold')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)
        self.draw()
        
    def plot_bar_comparison(self, data, title):
        self.axes.clear()
        algorithms = list(data.keys())
        times = list(data.values())
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#f44336']
        bars = self.axes.bar(algorithms, times, color=colors[:len(algorithms)])
        self.axes.set_ylabel('Time (milliseconds)', fontsize=10)
        self.axes.set_title(title, fontsize=12, fontweight='bold')
        for bar, time_val in zip(bars, times):
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                          f'{time_val:.3f}ms', ha='center', va='bottom', fontsize=9)
        self.axes.set_xticklabels(algorithms, rotation=15, ha='right')
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Computer Graphics Project")
        self.setGeometry(100, 100, 1500, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        h_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(h_splitter)

        self.gl_widget = OpenGLWidget()
        h_splitter.addWidget(self.gl_widget)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        self.control_tabs = QTabWidget()
        self.control_tabs.setMinimumWidth(400)
        self.control_tabs.setMaximumWidth(500)
        right_layout.addWidget(self.control_tabs)

        drawing_tab = QWidget()
        drawing_layout = QVBoxLayout(drawing_tab)
        drawing_layout.setSpacing(10)

        drawing_layout.addWidget(QLabel("Drawing Algorithms:"))
        
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["DDA Line", "Bresenham Line", "Midpoint Circle", "Bresenham Circle"])
        drawing_layout.addWidget(QLabel("Algorithm:"))
        drawing_layout.addWidget(self.algo_combo)

        draw_btn = QPushButton("Draw Line/Circle (Click 2 points)")
        draw_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }")
        draw_btn.clicked.connect(self.gl_widget.start_shape_mode)
        drawing_layout.addWidget(draw_btn)

        self.gl_widget.algo_combo = self.algo_combo

        drawing_layout.addWidget(QLabel("Basic Shapes:"))
        
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Triangle", "Rectangle", "Pentagon"])
        drawing_layout.addWidget(self.shape_combo)
        self.gl_widget.shape_combo = self.shape_combo

        draw_shape_btn = QPushButton("Draw Shape (Click center)")
        draw_shape_btn.clicked.connect(self.gl_widget.start_shape_draw_mode)
        drawing_layout.addWidget(draw_shape_btn)

        clear_btn = QPushButton("Clear Canvas")
        clear_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        clear_btn.clicked.connect(self.gl_widget.clear)
        drawing_layout.addWidget(clear_btn)
        
        drawing_layout.addStretch()
        self.control_tabs.addTab(drawing_tab, "Drawing")

        trans_tab = QWidget()
        trans_layout = QVBoxLayout(trans_tab)
        trans_layout.setSpacing(10)

        trans_layout.addWidget(QLabel("Geometric Transformations:"))
        
        self.transform_combo = QComboBox()
        self.transform_combo.addItems(["Translate", "Rotate", "Scale", "Reflect X", "Reflect Y", "Shear X", "Shear Y"])
        trans_layout.addWidget(QLabel("Transformation Type:"))
        trans_layout.addWidget(self.transform_combo)

        trans_group = QGroupBox("Translation")
        trans_group_layout = QHBoxLayout()
        self.tx_spin = QDoubleSpinBox()
        self.tx_spin.setRange(-200, 200)
        self.tx_spin.setPrefix("dx: ")
        trans_group_layout.addWidget(self.tx_spin)
        self.ty_spin = QDoubleSpinBox()
        self.ty_spin.setRange(-200, 200)
        self.ty_spin.setPrefix("dy: ")
        trans_group_layout.addWidget(self.ty_spin)
        trans_group.setLayout(trans_group_layout)
        trans_layout.addWidget(trans_group)

        rot_group = QGroupBox("Rotation")
        rot_group_layout = QVBoxLayout()
        self.rot_spin = QDoubleSpinBox()
        self.rot_spin.setRange(-360, 360)
        self.rot_spin.setPrefix("Angle (degrees): ")
        rot_group_layout.addWidget(self.rot_spin)
        rot_group.setLayout(rot_group_layout)
        trans_layout.addWidget(rot_group)

        scale_group = QGroupBox("Scale")
        scale_group_layout = QHBoxLayout()
        self.sx_spin = QDoubleSpinBox()
        self.sx_spin.setRange(0.1, 5)
        self.sx_spin.setValue(1)
        self.sx_spin.setPrefix("X: ")
        self.sx_spin.setSingleStep(0.1)
        scale_group_layout.addWidget(self.sx_spin)
        self.sy_spin = QDoubleSpinBox()
        self.sy_spin.setRange(0.1, 5)
        self.sy_spin.setValue(1)
        self.sy_spin.setPrefix("Y: ")
        self.sy_spin.setSingleStep(0.1)
        scale_group_layout.addWidget(self.sy_spin)
        scale_group.setLayout(scale_group_layout)
        trans_layout.addWidget(scale_group)

        shear_group = QGroupBox("Shear")
        shear_group_layout = QVBoxLayout()
        self.shear_spin = QDoubleSpinBox()
        self.shear_spin.setRange(-2, 2)
        self.shear_spin.setValue(0.5)
        self.shear_spin.setPrefix("Factor: ")
        self.shear_spin.setSingleStep(0.1)
        shear_group_layout.addWidget(self.shear_spin)
        shear_group.setLayout(shear_group_layout)
        trans_layout.addWidget(shear_group)

        apply_trans_btn = QPushButton("Apply Transformation")
        apply_trans_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")
        apply_trans_btn.clicked.connect(self.apply_transformation)
        trans_layout.addWidget(apply_trans_btn)

        reset_btn = QPushButton("Reset to Original")
        reset_btn.clicked.connect(self.gl_widget.reset_shape)
        trans_layout.addWidget(reset_btn)
        
        trans_layout.addStretch()
        self.control_tabs.addTab(trans_tab, "Transformations")

        clip_tab = QWidget()
        clip_layout = QVBoxLayout(clip_tab)
        clip_layout.setSpacing(10)

        clip_layout.addWidget(QLabel("Clipping Algorithms:"))
        
        self.clip_combo = QComboBox()
        self.clip_combo.addItems(["Cohen-Sutherland", "Sutherland-Hodgman"])
        clip_layout.addWidget(QLabel("Algorithm:"))
        clip_layout.addWidget(self.clip_combo)

        self.gl_widget.clip_combo = self.clip_combo

        clip_btn = QPushButton("Set Clip Window (Click 2 points)")
        clip_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px; }")
        clip_btn.clicked.connect(self.gl_widget.start_clip_mode)
        clip_layout.addWidget(clip_btn)

        clip_apply_btn = QPushButton("Apply Clipping")
        clip_apply_btn.clicked.connect(self.gl_widget.apply_clipping)
        clip_layout.addWidget(clip_apply_btn)

        clip_layout.addStretch()
        self.control_tabs.addTab(clip_tab, "Clipping")

        curve_tab = QWidget()
        curve_layout = QVBoxLayout(curve_tab)
        curve_layout.setSpacing(10)

        curve_layout.addWidget(QLabel("Curve Generation:"))
        
        self.curve_combo = QComboBox()
        self.curve_combo.addItems(["Bezier", "B-Spline"])
        curve_layout.addWidget(QLabel("Curve Type:"))
        curve_layout.addWidget(self.curve_combo)

        self.gl_widget.curve_combo = self.curve_combo

        curve_btn = QPushButton("Draw Curve (Click control points)")
        curve_btn.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; padding: 8px; }")
        curve_btn.clicked.connect(self.gl_widget.start_curve_mode)
        curve_layout.addWidget(curve_btn)

        curve_info = QLabel("Left-click to add control points, Right-click to draw curve")
        curve_info.setStyleSheet("QLabel { color: #666; font-size: 11px; }")
        curve_layout.addWidget(curve_info)

        curve_clear_btn = QPushButton("Clear Curve Points")
        curve_clear_btn.clicked.connect(self.gl_widget.clear_curve_points)
        curve_layout.addWidget(curve_clear_btn)

        curve_layout.addStretch()
        self.control_tabs.addTab(curve_tab, "Curves")

        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        file_layout.setSpacing(10)

        file_layout.addWidget(QLabel("File Operations:"))
        
        save_btn = QPushButton("Save Drawing")
        save_btn.setStyleSheet("QPushButton { background-color: #607D8B; color: white; padding: 8px; }")
        save_btn.clicked.connect(self.save_drawing)
        file_layout.addWidget(save_btn)

        load_btn = QPushButton("Load Drawing")
        load_btn.setStyleSheet("QPushButton { background-color: #607D8B; color: white; padding: 8px; }")
        load_btn.clicked.connect(self.load_drawing)
        file_layout.addWidget(load_btn)

        export_btn = QPushButton("Export as Image")
        export_btn.setStyleSheet("QPushButton { background-color: #607D8B; color: white; padding: 8px; }")
        export_btn.clicked.connect(self.export_as_image)
        file_layout.addWidget(export_btn)

        file_layout.addStretch()
        self.control_tabs.addTab(file_tab, "File")

        if MATPLOTLIB_AVAILABLE:
            perf_tab = QWidget()
            perf_layout = QVBoxLayout(perf_tab)
            perf_layout.setSpacing(10)
            
            perf_layout.addWidget(QLabel("Performance Comparison Charts"))
            
            benchmark_group = QGroupBox("Run Performance Tests")
            benchmark_layout = QVBoxLayout()
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            benchmark_layout.addWidget(self.progress_bar)
            
            run_benchmark_btn = QPushButton("Run All Benchmarks")
            run_benchmark_btn.setStyleSheet("QPushButton { background-color: #FF5722; color: white; padding: 10px; font-weight: bold; }")
            run_benchmark_btn.clicked.connect(self.run_performance_benchmarks)
            benchmark_layout.addWidget(run_benchmark_btn)
            
            benchmark_group.setLayout(benchmark_layout)
            perf_layout.addWidget(benchmark_group)
            
            chart_selector = QComboBox()
            chart_selector.addItems(["Line Algorithms", "Circle Algorithms", "Clipping Algorithms", "Summary Bar Chart"])
            chart_selector.currentTextChanged.connect(self.on_chart_selected)
            perf_layout.addWidget(QLabel("Select Chart:"))
            perf_layout.addWidget(chart_selector)
            
            self.chart_widget = PerformanceChartWidget(self, width=7, height=5, dpi=100)
            perf_layout.addWidget(self.chart_widget)
            
            self.perf_summary = QTextEdit()
            self.perf_summary.setMaximumHeight(150)
            self.perf_summary.setReadOnly(True)
            self.perf_summary.setStyleSheet("QTextEdit { background-color: #f5f5f5; font-family: monospace; }")
            perf_layout.addWidget(QLabel("Performance Summary:"))
            perf_layout.addWidget(self.perf_summary)
            
            self.control_tabs.addTab(perf_tab, "Performance")
            
            self.performance_data = {
                'line': {'DDA Line': {}, 'Bresenham Line': {}},
                'circle': {'Midpoint Circle': {}, 'Bresenham Circle': {}},
                'clip': {'Cohen-Sutherland': {}, 'Sutherland-Hodgman': {}}
            }
            self.current_chart_selector = chart_selector
        else:
            perf_tab = QWidget()
            perf_layout = QVBoxLayout(perf_tab)
            perf_layout.addWidget(QLabel(
                "Matplotlib not installed\n\nTo enable performance charts, install matplotlib:\npip install matplotlib"
            ))
            self.control_tabs.addTab(perf_tab, "Performance")

        log_label = QLabel("Output Log:")
        right_layout.addWidget(log_label)
        
        self.log = QTextEdit()
        self.log.setMaximumHeight(200)
        self.log.setMinimumHeight(120)
        self.log.setReadOnly(True)
        self.log.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #d4d4d4; font-family: monospace; font-size: 11px; }")
        right_layout.addWidget(self.log)

        self.gl_widget.log_signal.connect(self.log.append)

        h_splitter.addWidget(right_panel)
        h_splitter.setSizes([900, 500])

        self.statusBar().showMessage("Ready. Click on canvas to draw.")

    def save_drawing(self):
        """Save current drawing to JSON file"""
        shapes_data = self.gl_widget.get_shapes_data()
        
        if not shapes_data:
            QMessageBox.warning(self, "Save Failed", "No shapes to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Drawing", 
            os.path.expanduser("~/Desktop/drawing_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"),
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                save_data = {
                    "version": "1.0",
                    "timestamp": datetime.now().isoformat(),
                    "shapes": shapes_data,
                    "clip_window": self.gl_widget.clip_window
                }
                with open(file_path, 'w') as f:
                    json.dump(save_data, f, indent=2)
                self.log.append(f"Drawing saved to: {file_path}")
                self.statusBar().showMessage(f"Saved to {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save file: {str(e)}")
                self.log.append(f"Error saving: {str(e)}")

    def load_drawing(self):
        """Load drawing from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Drawing",
            os.path.expanduser("~/Desktop"),
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    load_data = json.load(f)
                
                shapes = load_data.get("shapes", [])
                clip_window = load_data.get("clip_window")
                
                if shapes:
                    self.gl_widget.load_shapes_data(shapes, clip_window)
                    self.log.append(f"Drawing loaded from: {file_path}")
                    self.log.append(f"Loaded {len(shapes)} shapes")
                    self.statusBar().showMessage(f"Loaded {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Load Failed", "No shapes found in file.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Could not load file: {str(e)}")
                self.log.append(f"Error loading: {str(e)}")

    def export_as_image(self):
        """Export current view as image (requires additional library)"""
        try:
            from PyQt5.QtGui import QPixmap
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Image",
                os.path.expanduser("~/Desktop/drawing_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"),
                "PNG Images (*.png);;JPEG Images (*.jpg)"
            )
            if file_path:
                pixmap = self.gl_widget.grab()
                pixmap.save(file_path)
                self.log.append(f"Image exported to: {file_path}")
                self.statusBar().showMessage(f"Exported to {os.path.basename(file_path)}")
        except Exception as e:
            self.log.append(f"Export error: {str(e)}")

    def on_chart_selected(self, chart_type):
        if not MATPLOTLIB_AVAILABLE:
            return
        if chart_type == "Line Algorithms":
            self.chart_widget.plot_line_comparison(self.performance_data['line'])
        elif chart_type == "Circle Algorithms":
            self.chart_widget.plot_circle_comparison(self.performance_data['circle'])
        elif chart_type == "Clipping Algorithms":
            self.chart_widget.plot_clip_comparison(self.performance_data['clip'])
        elif chart_type == "Summary Bar Chart":
            summary_data = {}
            if 100 in self.performance_data['line']['DDA Line']:
                summary_data['DDA Line'] = self.performance_data['line']['DDA Line'][100]
                summary_data['Bresenham Line'] = self.performance_data['line']['Bresenham Line'][100]
                summary_data['Midpoint Circle'] = self.performance_data['circle']['Midpoint Circle'].get(100, 0)
                summary_data['Bresenham Circle'] = self.performance_data['circle']['Bresenham Circle'].get(100, 0)
                self.chart_widget.plot_bar_comparison(summary_data, "Algorithm Performance Comparison (Size=100)")

    def run_performance_benchmarks(self):
        if not MATPLOTLIB_AVAILABLE:
            self.log.append("Cannot run benchmarks: matplotlib not installed")
            return
            
        self.log.append("\nStarting Performance Benchmarks...")
        
        self.progress_bar.setVisible(True)
        
        line_sizes = [20, 50, 100, 200, 400, 600]
        circle_radii = [10, 30, 50, 80, 120, 180]
        polygon_vertices = [10, 20, 50, 100, 200, 300]
        
        self.log.append("\nTesting Line Algorithms...")
        self.benchmark_line_algorithms(line_sizes)
        
        self.log.append("\nTesting Circle Algorithms...")
        self.benchmark_circle_algorithms(circle_radii)
        
        self.log.append("\nTesting Clipping Algorithms...")
        self.benchmark_clipping_algorithms(polygon_vertices)
        
        if hasattr(self, 'chart_widget'):
            self.chart_widget.plot_line_comparison(self.performance_data['line'])
            self.chart_widget.plot_circle_comparison(self.performance_data['circle'])
            self.chart_widget.plot_clip_comparison(self.performance_data['clip'])
        
        self.show_performance_summary()
        
        self.progress_bar.setVisible(False)
        self.log.append("\nBenchmarks Complete!")

    def benchmark_line_algorithms(self, sizes):
        for idx, size in enumerate(sizes):
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(int((idx + 1) / len(sizes) * 25))
            
            start = time.perf_counter()
            for _ in range(1000):
                self.gl_widget.dda_line(0, 0, size, size)
            dda_time = (time.perf_counter() - start) * 1000 / 1000
            self.performance_data['line']['DDA Line'][size] = dda_time
            
            start = time.perf_counter()
            for _ in range(1000):
                self.gl_widget.bresenham_line(0, 0, size, size)
            bres_time = (time.perf_counter() - start) * 1000 / 1000
            self.performance_data['line']['Bresenham Line'][size] = bres_time
            
            self.log.append(f"  Size {size:3d}: DDA={dda_time:.3f}ms, Bresenham={bres_time:.3f}ms")

    def benchmark_circle_algorithms(self, radii):
        for idx, radius in enumerate(radii):
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(25 + int((idx + 1) / len(radii) * 25))
            
            start = time.perf_counter()
            for _ in range(500):
                self.gl_widget.midpoint_circle_hollow(400, 300, radius)
            midpoint_time = (time.perf_counter() - start) * 1000 / 500
            self.performance_data['circle']['Midpoint Circle'][radius] = midpoint_time
            
            start = time.perf_counter()
            for _ in range(500):
                self.gl_widget.bresenham_circle_hollow(400, 300, radius)
            bres_time = (time.perf_counter() - start) * 1000 / 500
            self.performance_data['circle']['Bresenham Circle'][radius] = bres_time
            
            self.log.append(f"  Radius {radius:3d}: Midpoint={midpoint_time:.3f}ms, Bresenham={bres_time:.3f}ms")

    def benchmark_clipping_algorithms(self, vertex_counts):
        import math
        for idx, vertices in enumerate(vertex_counts):
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(50 + int((idx + 1) / len(vertex_counts) * 50))
            
            polygon = []
            for i in range(vertices):
                angle = i * 2 * math.pi / vertices
                polygon.append((400 + 200 * math.cos(angle), 300 + 200 * math.sin(angle)))
            window = (250, 200, 550, 400)
            
            start = time.perf_counter()
            for _ in range(200):
                self.gl_widget.cohen_sutherland_clip_polygon(polygon, window)
            cs_time = (time.perf_counter() - start) * 1000 / 200
            self.performance_data['clip']['Cohen-Sutherland'][vertices] = cs_time
            
            start = time.perf_counter()
            for _ in range(200):
                self.gl_widget.sutherland_hodgman_clip(polygon, window)
            sh_time = (time.perf_counter() - start) * 1000 / 200
            self.performance_data['clip']['Sutherland-Hodgman'][vertices] = sh_time
            
            self.log.append(f"  Vertices {vertices:3d}: Cohen-S={cs_time:.3f}ms, S-Hodgman={sh_time:.3f}ms")

    def show_performance_summary(self):
        summary = []
        summary.append("PERFORMANCE ANALYSIS SUMMARY")
        
        if 100 in self.performance_data['line']['DDA Line']:
            dda = self.performance_data['line']['DDA Line'][100]
            bres = self.performance_data['line']['Bresenham Line'][100]
            percent = abs((bres - dda) / dda * 100)
            summary.append(f"\nLine Algorithms (100px):")
            summary.append(f"  Bresenham is {percent:.1f}% faster than DDA")
            summary.append(f"  DDA: {dda:.3f}ms, Bresenham: {bres:.3f}ms")
        
        if 80 in self.performance_data['circle']['Midpoint Circle']:
            mid = self.performance_data['circle']['Midpoint Circle'][80]
            bres_circ = self.performance_data['circle']['Bresenham Circle'][80]
            summary.append(f"\nCircle Algorithms (radius=80):")
            summary.append(f"  Midpoint: {mid:.3f}ms, Bresenham: {bres_circ:.3f}ms")
        
        if 100 in self.performance_data['clip']['Cohen-Sutherland']:
            cs = self.performance_data['clip']['Cohen-Sutherland'][100]
            sh = self.performance_data['clip']['Sutherland-Hodgman'][100]
            summary.append(f"\nClipping Algorithms (100 vertices):")
            summary.append(f"  Cohen-Sutherland: {cs:.3f}ms, Sutherland-Hodgman: {sh:.3f}ms")
        
        summary.append("\n")
        
        if hasattr(self, 'perf_summary'):
            self.perf_summary.setText("\n".join(summary))
        self.log.append("\n" + "\n".join(summary))

    def apply_transformation(self):
        trans_type = self.transform_combo.currentText()
        params = {}
        
        if trans_type == "Translate":
            params['dx'] = self.tx_spin.value()
            params['dy'] = self.ty_spin.value()
            self.log.append(f"Applying Translation: dx={params['dx']}, dy={params['dy']}")
        elif trans_type == "Rotate":
            params['angle'] = self.rot_spin.value()
            self.log.append(f"Applying Rotation: angle={params['angle']} degrees")
        elif trans_type == "Scale":
            params['sx'] = self.sx_spin.value()
            params['sy'] = self.sy_spin.value()
            self.log.append(f"Applying Scale: sx={params['sx']}, sy={params['sy']}")
        elif trans_type == "Reflect X":
            params['reflect_x'] = True
            self.log.append("Applying Reflection about X-axis")
        elif trans_type == "Reflect Y":
            params['reflect_y'] = True
            self.log.append("Applying Reflection about Y-axis")
        elif trans_type == "Shear X":
            params['shear_x'] = self.shear_spin.value()
            self.log.append(f"Applying Shear X: factor={params['shear_x']}")
        elif trans_type == "Shear Y":
            params['shear_y'] = self.shear_spin.value()
            self.log.append(f"Applying Shear Y: factor={params['shear_y']}")
            
        self.gl_widget.apply_transform(trans_type, params)