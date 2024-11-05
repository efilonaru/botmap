import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import numpy as np
from PIL import Image
import os

class MapsScreenshotBot:
    def __init__(self, city, boundary_coords, zoom_level=21):
        """
        Initialize the bot with city name, boundary coordinates, and zoom level
        
        Args:
            city (str): Name of the city to screenshot
            boundary_coords (list): List of coordinates defining city boundary
            zoom_level (int): Google Maps zoom level (0-21)
                - 0: World view
                - 10: City view
                - 15: Streets view
                - 18: Buildings view (default)
                - 20: Building details
                - 21: Maximum zoom
        """
        self.city = city
        self.boundary_coords = boundary_coords
        self.zoom_level = min(21, max(0, zoom_level))  # Ensure valid zoom level
        self.driver = webdriver.Chrome()
        self.screenshot_path = f"screenshots_{city}_zoom{zoom_level}"
        
        if not os.path.exists(self.screenshot_path):
            os.makedirs(self.screenshot_path)
    
    def is_within_boundary(self, current_coords):
        """
        Check if current coordinates are within city boundary
        
        Args:
            current_coords (tuple): Current latitude and longitude
            
        Returns:
            bool: True if within boundary, False otherwise
        """
        def point_in_polygon(point, polygon):
            x, y = point
            n = len(polygon)
            inside = False
            
            p1x, p1y = polygon[0]
            for i in range(n + 1):
                p2x, p2y = polygon[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
                
            return inside
            
        return point_in_polygon(current_coords, self.boundary_coords)

    def calculate_grid_step(self):
        """
        Calculate grid step size based on zoom level
        Higher zoom = smaller step size for more detail
        """
        # Base step sizes at zoom level 18
        base_lat_step = 0.001  # Approximately 111 meters
        base_lon_step = 0.001
        
        # Adjust step size based on zoom level difference
        zoom_factor = 2 ** (18 - self.zoom_level)
        return base_lat_step * zoom_factor, base_lon_step * zoom_factor
    
    def navigate_to_position(self, lat, lon):
        """Navigate to specific coordinates with custom zoom level"""
        url = f"https://www.google.com/maps/@{lat},{lon},{self.zoom_level}z"
        self.driver.get(url)
        time.sleep(2)  # Wait for map to load   
        
        # Ensure map is fully loaded at desired zoom
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "gm-style"))
            )
        except:
            print(f"Warning: Map loading timeout at coordinates: {lat}, {lon}")
    
    def scan_city(self, grid_size=10):
        """
        Scan city area taking screenshots with specified zoom level
        
        Args:
            grid_size (int): Size of grid to divide city into
        """
        try:
            # Calculate area bounds and convert to float
            lat_min = float(min(coord[0] for coord in self.boundary_coords))
            lat_max = float(max(coord[0] for coord in self.boundary_coords))
            lon_min = float(min(coord[1] for coord in self.boundary_coords))
            lon_max = float(max(coord[1] for coord in self.boundary_coords))
            
            # Calculate step sizes based on zoom level
            lat_step, lon_step = self.calculate_grid_step()
            
            # Adjust grid size based on zoom level
            actual_grid_size = grid_size * (2 ** (self.zoom_level - 18))
            
            lat_steps = np.linspace(lat_min, lat_max, actual_grid_size)
            lon_steps = np.linspace(lon_min, lon_max, actual_grid_size)
            
            total_points = len(lat_steps) * len(lon_steps)
            processed_points = 0
            
            for lat in lat_steps:
                for lon in lon_steps:
                    if self.is_within_boundary((lat, lon)):
                        # Navigate to position with custom zoom
                        self.navigate_to_position(lat, lon)
                        
                        # Take screenshot
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        filename = f"{self.screenshot_path}/{self.city}_{lat}_{lon}_z{self.zoom_level}_{timestamp}.png"
                        screenshot = pyautogui.screenshot()
                        screenshot.save(filename)
                        
                        # Progress update
                        processed_points += 1
                        progress = (processed_points / total_points) * 100
                        print(f"Progress: {progress:.1f}% ({processed_points}/{total_points})")
                        
                        # Optional: Add small delay to prevent rate limiting
                        time.sleep(1)
            
        finally:
            self.driver.quit()

# Contoh penggunaan dengan berbagai zoom level
def create_detailed_map(city_name, boundary_coords):
    """
    Membuat screenshot dengan berbagai tingkat detail
    """
    zoom_levels = {
        "overview": 16,      # Area overview
        "streets": 18,       # Street level detail
        "buildings": 19,     # Building detail
        "maximum": 20        # Maximum detail
    }
    
    for level_name, zoom in zoom_levels.items():
        print(f"\nStarting {level_name} scan at zoom level {zoom}")
        bot = MapsScreenshotBot(city_name, boundary_coords, zoom_level=zoom)
        bot.scan_city(grid_size=10)

# Example usage
if __name__ == "__main__":
    # Example coordinates for Surabaya (simplified boundary)
    surabaya_boundary = [
    # Surabaya Utara (sekitar Pelabuhan Tanjung Perak)
    (-7.1955, 112.7321),  # Pelabuhan Tanjung Perak
    (-7.1891, 112.7445),  # Ujung
    (-7.2023, 112.7667),  # Kenjeran
    
    # Surabaya Timur
    (-7.2284, 112.7912),  # Sukolilo
    (-7.2567, 112.8023),  # Rungkut
    (-7.2789, 112.7989),  # Gunung Anyar
    (-7.3012, 112.7867),  # Tambaksari
    
    # Surabaya Selatan
    (-7.3234, 112.7654),  # Gayungan
    (-7.3345, 112.7445),  # Wiyung
    (-7.3256, 112.7234),  # Karang Pilang
    
    # Surabaya Barat
    (-7.2867, 112.6789),  # Lakarsantri
    (-7.2567, 112.6654),  # Benowo
    (-7.2334, 112.6789),  # Tandes
    (-7.2123, 112.6912),  # Asemrowo
    
    # Kembali ke titik awal untuk menutup polygon
    (-7.1955, 112.7321)   # Pelabuhan Tanjung Perak
]
    
    SURABAYA_KELURAHAN_BOUNDARIES = {
    # SURABAYA PUSAT
    "Kecamatan Bubutan": {
        "Alun-alun Contong": [
            (-7.2478, 112.7345),
            (-7.2456, 112.7401),
            (-7.2501, 112.7423),
            (-7.2523, 112.7367),
            (-7.2478, 112.7345)
        ],
        "Bubutan": [
            (-7.2512, 112.7312),
            (-7.2489, 112.7367),
            (-7.2534, 112.7389),
            (-7.2556, 112.7334),
            (-7.2512, 112.7312)
        ],
        "Gundih": [
            (-7.2467, 112.7289),
            (-7.2445, 112.7345),
            (-7.2489, 112.7367),
            (-7.2512, 112.7312),
            (-7.2467, 112.7289)
        ],
        "Jepara": [
            (-7.2423, 112.7267),
            (-7.2401, 112.7323),
            (-7.2445, 112.7345),
            (-7.2467, 112.7289),
            (-7.2423, 112.7267)
        ]
    },
    
    # SURABAYA TIMUR
    "Kecamatan Gubeng": {
        "Airlangga": [
            (-7.2712, 112.7589),
            (-7.2689, 112.7645),
            (-7.2734, 112.7678),
            (-7.2756, 112.7623),
            (-7.2712, 112.7589)
        ],
        "Baratajaya": [
            (-7.2867, 112.7567),
            (-7.2845, 112.7634),
            (-7.2889, 112.7656),
            (-7.2912, 112.7589),
            (-7.2867, 112.7567)
        ],
        "Gubeng": [
            (-7.2645, 112.7512),
            (-7.2623, 112.7578),
            (-7.2667, 112.7601),
            (-7.2689, 112.7534),
            (-7.2645, 112.7512)
        ],
        "Kertajaya": [
            (-7.2778, 112.7534),
            (-7.2756, 112.7601),
            (-7.2801, 112.7623),
            (-7.2823, 112.7556),
            (-7.2778, 112.7534)
        ],
        "Mojo": [
            (-7.2734, 112.7556),
            (-7.2712, 112.7623),
            (-7.2756, 112.7645),
            (-7.2778, 112.7578),
            (-7.2734, 112.7556)
        ],
        "Pucang Sewu": [
            (-7.2689, 112.7534),
            (-7.2667, 112.7601),
            (-7.2712, 112.7623),
            (-7.2734, 112.7556),
            (-7.2689, 112.7534)
        ]
    },
    "Kecamatan Gunung Anyar": {
        "Gunung Anyar": [
            (-7.3323, 112.7867),
            (-7.3301, 112.7934),
            (-7.3345, 112.7956),
            (-7.3367, 112.7889),
            (-7.3323, 112.7867)
        ],
        "Gunung Anyar Tambak": [
            (-7.3367, 112.7889),
            (-7.3345, 112.7956),
            (-7.3389, 112.7978),
            (-7.3412, 112.7912),
            (-7.3367, 112.7889)
        ],
        "Rungkut Menanggal": [
            (-7.3278, 112.7845),
            (-7.3256, 112.7912),
            (-7.3301, 112.7934),
            (-7.3323, 112.7867),
            (-7.3278, 112.7845)
        ]
    },
    }

    gunung_anyar = [
        (-7.3323, 112.7867),
        (-7.3301, 112.7934),
        (-7.3345, 112.7956),
        (-7.3367, 112.7889),
        (-7.3323, 112.7867)
    ]
    
    bot = MapsScreenshotBot("Surabaya", surabaya_boundary, zoom_level=20)
    bot.scan_city(grid_size=20)
