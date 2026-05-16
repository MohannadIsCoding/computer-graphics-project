from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QMouseEvent
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class OpenGLWidget(QGLWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.shapes = []  # list of (vertices, color, name, is_animated)
        self.original_shape = None
        self.original_vertices = None
        self.drawing_mode = None
        self.curve_points = []
        self.clip_window = None
        self.temp_start = None
        self.algo_combo = None
        self.clip_combo = None
        self.curve_combo = None
        self.shape_combo = None
        
        # Animation variables
        self.animating = False
        self.animation_progress = 0.0
        self.animation_start_shape = []
        self.animation_end_shape = []
        self.animation_speed = 0.05
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        self.waiting_for_curve = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0

    def initializeGL(self):
        glClearColor(1, 1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 600)
        glMatrixMode(GL_MODELVIEW)
        glPointSize(6)
        glLineWidth(2)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, w, 0, h)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw grid
        glColor3f(0.9, 0.9, 0.9)
        glBegin(GL_LINES)
        for x in range(0, 801, 50):
            glVertex2f(x, 0)
            glVertex2f(x, 600)
        for y in range(0, 601, 50):
            glVertex2f(0, y)
            glVertex2f(800, y)
        glEnd()

        # Draw all shapes
        for item in self.shapes:
            if len(item) >= 4:
                vertices, color, name, animated = item[0], item[1], item[2], item[3]
            elif len(item) == 3:
                vertices, color, name = item[0], item[1], item[2]
                animated = False
            else:
                continue
                
            if len(vertices) < 2:
                continue
                
            glColor3f(*color)
            glBegin(GL_LINE_STRIP)
            for v in vertices:
                glVertex2f(v[0], v[1])
            glEnd()
            
            # Close the shape if it's a polygon
            if name in ["Triangle", "Rectangle", "Pentagon"] and len(vertices) > 2:
                glBegin(GL_LINES)
                glVertex2f(vertices[-1][0], vertices[-1][1])
                glVertex2f(vertices[0][0], vertices[0][1])
                glEnd()
            
            # For circles, close properly
            if name == "Circle" and len(vertices) > 2:
                glBegin(GL_LINES)
                glVertex2f(vertices[-1][0], vertices[-1][1])
                glVertex2f(vertices[0][0], vertices[0][1])
                glEnd()

        # Draw clipping window
        if self.clip_window:
            glColor3f(1, 0, 0)
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
            xmin, ymin, xmax, ymax = self.clip_window
            glVertex2f(xmin, ymin)
            glVertex2f(xmax, ymin)
            glVertex2f(xmax, ymax)
            glVertex2f(xmin, ymax)
            glEnd()
            glLineWidth(1)

        # Draw curve control points
        if self.drawing_mode == 'curve' or self.waiting_for_curve:
            glColor3f(0, 0, 1)
            glBegin(GL_POINTS)
            for p in self.curve_points:
                glVertex2f(p[0], p[1])
            glEnd()
            
            if len(self.curve_points) > 1:
                glColor3f(0.5, 0.5, 1)
                glBegin(GL_LINE_STRIP)
                for p in self.curve_points:
                    glVertex2f(p[0], p[1])
                glEnd()

        # Draw temporary line
        if self.temp_start and self.drawing_mode == 'clip':
            glColor3f(1, 0.5, 0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(self.temp_start[0], self.temp_start[1])
            glVertex2f(self.last_mouse_x, self.last_mouse_y)
            glEnd()

    def update_animation(self):
        self.animation_progress += self.animation_speed
        
        if self.animation_progress >= 1.0:
            self.animation_timer.stop()
            self.animating = False
            self.animation_progress = 1.0
            
            if self.animation_end_shape:
                self.shapes.append([self.animation_end_shape, (1, 0, 0), "Transformed", False])
                self.log_signal.emit("Animation complete")
        else:
            t = self.animation_progress
            current_shape = []
            
            min_len = min(len(self.animation_start_shape), len(self.animation_end_shape))
            for i in range(min_len):
                x1, y1 = self.animation_start_shape[i]
                x2, y2 = self.animation_end_shape[i]
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
                current_shape.append((x, y))
            
            # Update animated shape
            for i in range(len(self.shapes) - 1, -1, -1):
                if len(self.shapes[i]) >= 4 and self.shapes[i][3]:
                    self.shapes[i] = [current_shape, (1, 0.5, 0), "Animating", True]
                    break
        
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = self.height() - event.y()
            self.last_mouse_x = x
            self.last_mouse_y = y
            
            if self.drawing_mode == 'clip':
                if self.temp_start is None:
                    self.temp_start = (x, y)
                    self.log_signal.emit("Click second corner for clip window")
                else:
                    x1, y1 = self.temp_start
                    x2, y2 = x, y
                    self.clip_window = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                    self.temp_start = None
                    self.drawing_mode = None
                    self.log_signal.emit(f"Clipping window set")
                    self.update()
                    
            elif self.drawing_mode == 'shape':
                if self.temp_start is None:
                    self.temp_start = (x, y)
                    self.log_signal.emit("Click second point to draw")
                else:
                    x1, y1 = self.temp_start
                    x2, y2 = x, y
                    self.draw_shape(x1, y1, x2, y2)
                    self.temp_start = None
                    
            elif self.drawing_mode == 'basic_shape':
                self.draw_basic_shape(x, y)
                self.drawing_mode = None
                
            elif self.drawing_mode == 'curve':
                self.curve_points.append((x, y))
                self.log_signal.emit(f"Control point {len(self.curve_points)}: ({x}, {y})")
                self.update()
                
        elif event.button() == Qt.RightButton:
            if self.drawing_mode == 'curve' and len(self.curve_points) >= 2:
                self.draw_curve()
                self.drawing_mode = None
                self.waiting_for_curve = False
                self.log_signal.emit("Curve finalized")
            elif self.waiting_for_curve:
                self.draw_curve()
                self.waiting_for_curve = False
                
    def mouseMoveEvent(self, event):
        self.last_mouse_x = event.x()
        self.last_mouse_y = self.height() - event.y()
        self.update()

    def draw_shape(self, x1, y1, x2, y2):
        if not self.algo_combo:
            self.log_signal.emit("Error: No algorithm selected")
            return
            
        algo = self.algo_combo.currentText()
        
        if "Line" in algo:
            if algo == "DDA Line":
                vertices = self.dda_line(x1, y1, x2, y2)
            else:
                vertices = self.bresenham_line(x1, y1, x2, y2)
            self.original_shape = vertices[:]
            self.original_vertices = vertices[:]
            self.shapes.append([vertices, (0, 0, 0), "Line", False])
            self.log_signal.emit(f"Drawn line using {algo}")
            
        elif "Circle" in algo:
            radius = int(math.hypot(x2 - x1, y2 - y1))
            cx, cy = x1, y1
            if algo == "Midpoint Circle":
                vertices = self.midpoint_circle_hollow(cx, cy, radius)
            else:
                vertices = self.bresenham_circle_hollow(cx, cy, radius)
            self.original_shape = vertices[:]
            self.original_vertices = vertices[:]
            self.shapes.append([vertices, (0, 0, 0), "Circle", False])
            self.log_signal.emit(f"Drawn circle using {algo}, radius={radius}")
            
        self.update()

    def draw_basic_shape(self, cx, cy):
        if not self.shape_combo:
            shape_type = "Triangle"
        else:
            shape_type = self.shape_combo.currentText()
            
        size = 70
        
        if shape_type == "Triangle":
            vertices = [
                (cx, cy + size),
                (cx - size * 0.866, cy - size/2),
                (cx + size * 0.866, cy - size/2),
                (cx, cy + size)
            ]
        elif shape_type == "Rectangle":
            vertices = [
                (cx - size, cy - size/2),
                (cx + size, cy - size/2),
                (cx + size, cy + size/2),
                (cx - size, cy + size/2),
                (cx - size, cy - size/2)
            ]
        else:  # Pentagon
            vertices = []
            for i in range(6):
                angle = math.radians(90 - i * 72)
                vertices.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
        
        self.original_shape = vertices[:]
        self.original_vertices = vertices[:]
        self.shapes.append([vertices, (0, 0.5, 0), shape_type, False])
        self.log_signal.emit(f"Drawn {shape_type} at ({cx}, {cy})")
        self.update()

    def draw_curve(self):
        if len(self.curve_points) < 2:
            self.log_signal.emit("Need at least 2 control points for curve")
            return
            
        if not self.curve_combo:
            return
            
        curve_type = self.curve_combo.currentText()
        
        if curve_type == "Bezier":
            vertices = self.bezier_curve(self.curve_points)
        else:
            vertices = self.bspline_curve(self.curve_points)
            
        self.original_shape = vertices[:]
        self.original_vertices = vertices[:]
        self.shapes.append([vertices, (0, 0, 1), curve_type, False])
        self.log_signal.emit(f"Drawn {curve_type} curve with {len(self.curve_points)} control points")
        self.update()

    def apply_transform(self, trans_type, params):
      if not self.original_vertices:
          self.log_signal.emit("No shape to transform")
          return
          
      transformed = []
      cx, cy = self.get_center(self.original_vertices)
      
      for x, y in self.original_vertices:
          nx, ny = x, y
          
          if trans_type == "Translate":
              nx = x + params.get('dx', 0)
              ny = y + params.get('dy', 0)
          elif trans_type == "Rotate":
              angle_rad = math.radians(params.get('angle', 0))
              nx = cx + (x - cx) * math.cos(angle_rad) - (y - cy) * math.sin(angle_rad)
              ny = cy + (x - cx) * math.sin(angle_rad) + (y - cy) * math.cos(angle_rad)
          elif trans_type == "Scale":
              sx = params.get('sx', 1)
              sy = params.get('sy', 1)
              nx = cx + (x - cx) * sx
              ny = cy + (y - cy) * sy
          elif trans_type == "Reflect X":
              nx = x
              ny = 2 * cy - y
          elif trans_type == "Reflect Y":
              nx = 2 * cx - x
              ny = y
          elif trans_type == "Shear X":
              nx = x + params.get('shear_x', 0) * (y - cy)
              ny = y
          elif trans_type == "Shear Y":
              nx = x
              ny = y + params.get('shear_y', 0) * (x - cx)
              
          transformed.append((nx, ny))
      
      # Remove any existing transformed or animated shapes
      self.remove_transformed_shapes()
      
      # Add the transformed shape
      self.shapes.append([transformed, (1, 0, 0), "Transformed", False])
      self.log_signal.emit(f"Applied {trans_type}")
      self.update()

    def remove_transformed_shapes(self):
      new_shapes = []
      for item in self.shapes:
          if len(item) >= 3:
              name = item[2]
              # Keep only original shapes (black/green/blue), remove transformed (red) and animated
              if name not in ["Transformed", "Animating", "Clipped"]:
                  new_shapes.append(item)
      self.shapes = new_shapes
      
      # Also stop any ongoing animation
      if self.animating:
          self.animation_timer.stop()
          self.animating = False

    def reset_shape(self):
      if self.original_vertices:
          self.remove_transformed_shapes()
          self.update()
          self.log_signal.emit("Reset to original shape")
      else:
          self.log_signal.emit("No original shape to reset")
          
    def start_animation(self, start_shape, end_shape):
        self.animation_start_shape = start_shape[:]
        self.animation_end_shape = end_shape[:]
        self.animation_progress = 0.0
        self.animating = True
        
        self.shapes.append([start_shape[:], (1, 0.5, 0), "Animating", True])
        self.animation_timer.start(16)

    def apply_clipping(self):
        if not self.clip_window:
            self.log_signal.emit("No clipping window set")
            return
            
        if not self.original_vertices:
            self.log_signal.emit("No shape to clip")
            return
            
        if not self.clip_combo:
            return
            
        algo = self.clip_combo.currentText()
        
        if algo == "Cohen-Sutherland":
            clipped = self.cohen_sutherland_clip_polygon(self.original_vertices, self.clip_window)
        else:
            clipped = self.sutherland_hodgman_clip(self.original_vertices, self.clip_window)
            
        if clipped and len(clipped) > 2:
            self.shapes.append([clipped, (1, 0, 0), "Clipped", False])
            self.log_signal.emit(f"Clipped using {algo}")
        else:
            self.log_signal.emit("Shape completely outside clip window")
        self.update()

    # ========== SAVE/LOAD METHODS ==========
    
    def get_shapes_data(self):
        """Export current shapes to serializable format"""
        shapes_data = []
        for item in self.shapes:
            # Handle different possible tuple lengths
            if len(item) >= 3:
                vertices = item[0]
                color = item[1]
                name = item[2]
                animated = item[3] if len(item) > 3 else False
                
                # Don't save animated or temporary shapes
                if not animated and name not in ["Animating"]:
                    # Convert vertices to list of lists for JSON serialization
                    serializable_vertices = []
                    for v in vertices:
                        serializable_vertices.append([float(v[0]), float(v[1])])
                    
                    shapes_data.append({
                        'type': 'shape',
                        'name': str(name),
                        'vertices': serializable_vertices,
                        'color': [float(color[0]), float(color[1]), float(color[2])]
                    })
        return shapes_data

    def load_shapes_data(self, shapes_data, clip_window=None):
        """Load shapes from serialized data"""
        self.clear()
        
        for shape in shapes_data:
            vertices = []
            for v in shape['vertices']:
                vertices.append((v[0], v[1]))
            
            name = shape['name']
            color = tuple(shape['color'])
            
            self.shapes.append([vertices, color, name, False])
            
            # Store the first shape as original for transformations
            if len(self.shapes) == 1:
                self.original_shape = vertices[:]
                self.original_vertices = vertices[:]
        
        if clip_window:
            self.clip_window = tuple(clip_window)
        
        self.update()
        self.log_signal.emit(f"Loaded {len(shapes_data)} shapes")

    # ========== HOLLOW CIRCLE ALGORITHMS ==========
    
    def midpoint_circle_hollow(self, cx, cy, r):
        points = []
        x = 0
        y = r
        d = 1 - r
        
        points.append((cx + x, cy + y))
        points.append((cx + y, cy + x))
        points.append((cx - x, cy + y))
        points.append((cx - y, cy + x))
        points.append((cx + x, cy - y))
        points.append((cx + y, cy - x))
        points.append((cx - x, cy - y))
        points.append((cx - y, cy - x))
        
        while x < y:
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1
            
            points.append((cx + x, cy + y))
            points.append((cx + y, cy + x))
            points.append((cx - x, cy + y))
            points.append((cx - y, cy + x))
            points.append((cx + x, cy - y))
            points.append((cx + y, cy - x))
            points.append((cx - x, cy - y))
            points.append((cx - y, cy - x))
        
        unique_points = []
        seen = set()
        for p in points:
            if p not in seen:
                seen.add(p)
                unique_points.append(p)
        
        return self.order_circle_points(unique_points, cx, cy)

    def bresenham_circle_hollow(self, cx, cy, r):
        return self.midpoint_circle_hollow(cx, cy, r)

    def order_circle_points(self, points, cx, cy):
        if len(points) < 3:
            return points
        
        def get_angle(p):
            return math.atan2(p[1] - cy, p[0] - cx)
        
        ordered = sorted(points, key=get_angle)
        return ordered

    # ========== LINE ALGORITHMS ==========
    
    def dda_line(self, x1, y1, x2, y2):
        points = []
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return [(x1, y1)]
        x_inc = dx / steps
        y_inc = dy / steps
        x, y = x1, y1
        for i in range(steps + 1):
            points.append((round(x), round(y)))
            x += x_inc
            y += y_inc
        return points

    def bresenham_line(self, x1, y1, x2, y2):
        points = []
        x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        return points

    # ========== CURVE ALGORITHMS ==========
    
    def bezier_curve(self, points, num_segments=200):
        vertices = []
        n = len(points) - 1
        
        for t in range(num_segments + 1):
            t_param = t / num_segments
            temp_points = points[:]
            while len(temp_points) > 1:
                new_points = []
                for i in range(len(temp_points) - 1):
                    x = (1 - t_param) * temp_points[i][0] + t_param * temp_points[i + 1][0]
                    y = (1 - t_param) * temp_points[i][1] + t_param * temp_points[i + 1][1]
                    new_points.append((x, y))
                temp_points = new_points
            vertices.append(temp_points[0])
        return vertices

    def bspline_curve(self, points, num_segments=200):
        vertices = []
        n = len(points)
        
        if n < 3:
            return self.bezier_curve(points)
        
        for t in range(num_segments + 1):
            t_param = t / num_segments
            
            for i in range(n - 3):
                t2 = t_param * t_param
                t3 = t2 * t_param
                
                b0 = (1 - t_param) ** 3 / 6
                b1 = (3 * t3 - 6 * t2 + 4) / 6
                b2 = (-3 * t3 + 3 * t2 + 3 * t_param + 1) / 6
                b3 = t3 / 6
                
                x = b0 * points[i][0] + b1 * points[i+1][0] + b2 * points[i+2][0] + b3 * points[i+3][0]
                y = b0 * points[i][1] + b1 * points[i+1][1] + b2 * points[i+2][1] + b3 * points[i+3][1]
                vertices.append((x, y))
                
        return vertices

    # ========== CLIPPING ALGORITHMS ==========
    
    def compute_region_code(self, x, y, xmin, ymin, xmax, ymax):
        code = 0
        if x < xmin:
            code |= 1
        elif x > xmax:
            code |= 2
        if y < ymin:
            code |= 4
        elif y > ymax:
            code |= 8
        return code

    def cohen_sutherland_clip_polygon(self, polygon, window):
        xmin, ymin, xmax, ymax = window
        clipped_points = []
        
        for i in range(len(polygon)):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i+1) % len(polygon)]
            
            segment = self.clip_line_segment(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
            if segment:
                clipped_points.extend(segment)
        
        return self.remove_duplicate_points(clipped_points)

    def clip_line_segment(self, x1, y1, x2, y2, xmin, ymin, xmax, ymax):
        code1 = self.compute_region_code(x1, y1, xmin, ymin, xmax, ymax)
        code2 = self.compute_region_code(x2, y2, xmin, ymin, xmax, ymax)
        
        accept = False
        done = False
        
        while not done:
            if code1 == 0 and code2 == 0:
                accept = True
                done = True
            elif (code1 & code2) != 0:
                done = True
            else:
                code_out = code1 if code1 != 0 else code2
                x, y = 0, 0
                
                if code_out & 1:
                    x = xmin
                    y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                elif code_out & 2:
                    x = xmax
                    y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                elif code_out & 4:
                    y = ymin
                    x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                elif code_out & 8:
                    y = ymax
                    x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                
                if code_out == code1:
                    x1, y1 = x, y
                    code1 = self.compute_region_code(x1, y1, xmin, ymin, xmax, ymax)
                else:
                    x2, y2 = x, y
                    code2 = self.compute_region_code(x2, y2, xmin, ymin, xmax, ymax)
        
        if accept:
            return [(x1, y1), (x2, y2)]
        return []

    def sutherland_hodgman_clip(self, polygon, window):
        xmin, ymin, xmax, ymax = window
        
        def clip_edge(poly, x1, y1, x2, y2):
            new_poly = []
            if not poly:
                return new_poly
                
            for i in range(len(poly)):
                curr = poly[i]
                prev = poly[i-1]
                
                curr_inside = self.is_inside_edge(curr[0], curr[1], x1, y1, x2, y2)
                prev_inside = self.is_inside_edge(prev[0], prev[1], x1, y1, x2, y2)
                
                if prev_inside and curr_inside:
                    new_poly.append(curr)
                elif prev_inside and not curr_inside:
                    inter = self.line_intersection(prev[0], prev[1], curr[0], curr[1], x1, y1, x2, y2)
                    if inter:
                        new_poly.append(inter)
                elif not prev_inside and curr_inside:
                    inter = self.line_intersection(prev[0], prev[1], curr[0], curr[1], x1, y1, x2, y2)
                    if inter:
                        new_poly.append(inter)
                    new_poly.append(curr)
            return new_poly
        
        poly = polygon
        poly = clip_edge(poly, xmin, ymin, xmin, ymax)
        poly = clip_edge(poly, xmax, ymin, xmax, ymax)
        poly = clip_edge(poly, xmin, ymin, xmax, ymin)
        poly = clip_edge(poly, xmin, ymax, xmax, ymax)
        
        return poly

    def is_inside_edge(self, x, y, x1, y1, x2, y2):
        if x1 == x2:
            return x >= x1 if x2 > x1 else x <= x1
        else:
            return y >= y1 if y2 > y1 else y <= y1

    def line_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (x, y)
        return None

    def remove_duplicate_points(self, points, tolerance=1.0):
        if len(points) < 2:
            return points
            
        unique = [points[0]]
        for p in points[1:]:
            last = unique[-1]
            if abs(p[0] - last[0]) > tolerance or abs(p[1] - last[1]) > tolerance:
                unique.append(p)
        return unique

    # ========== HELPER METHODS ==========
    
    def get_center(self, vertices):
        if not vertices:
            return (400, 300)
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        return sum(xs)/len(xs), sum(ys)/len(ys)

    def start_shape_mode(self):
        self.drawing_mode = 'shape'
        self.temp_start = None
        self.curve_points = []
        self.log_signal.emit("Shape mode: Click two points to draw line or circle")

    def start_clip_mode(self):
        self.drawing_mode = 'clip'
        self.temp_start = None
        self.log_signal.emit("Clip mode: Click two points to set clipping window")

    def start_curve_mode(self):
        self.drawing_mode = 'curve'
        self.curve_points = []
        self.waiting_for_curve = True
        self.log_signal.emit("Curve mode: Click control points, then RIGHT-CLICK to draw curve")
        self.update()

    def start_shape_draw_mode(self):
        self.drawing_mode = 'basic_shape'
        self.log_signal.emit("Click where to place the shape")

    def clear_curve_points(self):
        self.curve_points = []
        self.drawing_mode = None
        self.waiting_for_curve = False
        self.log_signal.emit("Curve points cleared")
        self.update()

    def reset_shape(self):
        if self.original_vertices:
            new_shapes = []
            for item in self.shapes:
                if len(item) >= 3 and item[2] not in ["Transformed", "Clipped", "Animating"]:
                    new_shapes.append(item)
            self.shapes = new_shapes
            self.update()
            self.log_signal.emit("Reset to original shape")
        else:
            self.log_signal.emit("No original shape to reset")

    def clear(self):
        self.shapes = []
        self.original_shape = None
        self.original_vertices = None
        self.clip_window = None
        self.curve_points = []
        self.drawing_mode = None
        self.temp_start = None
        self.animating = False
        self.animation_timer.stop()
        self.update()
        self.log_signal.emit("Canvas cleared")