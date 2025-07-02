import pyautogui
import time
import keyboard
import threading
from PIL import ImageGrab
import win32gui
import win32con
import win32api
import win32ui
import ctypes
from ctypes import wintypes

class SimpleAutoHP:
    def __init__(self):
        self.running = False
        self.paused = False  # Pause state
        self.monitor_point = None  # Point to monitor color (x, y)
        self.target_color = None   # Target color to detect (R, G, B)
        self.key_to_press = 'f1'   # Key to press
        self.tolerance = 30        # Color tolerance (0-255)
        self.check_interval = 0.5  # Check every 0.5 seconds
        self.cooldown = 2.0        # Wait 2 seconds between key presses
        self.last_press_time = 0
        self.target_window = None  # Target window handle
        
        # Safety feature
        pyautogui.FAILSAFE = True
        
        
    def set_monitor_point(self):
        """Set the point to monitor color"""
        print("📍 Setting Monitor Point")
        print("1. You have 7 seconds to move your mouse to the desired position")
        time.sleep(7)  # Give user time to move mouse to desired position
        self.monitor_point = pyautogui.position()
        print(f"✅ Position saved: {self.monitor_point}")
        return True
    
    def set_target_color(self):
        """Set the target color to detect"""
        if not self.monitor_point:
            print("❌ Please set monitor point first")
            return False
            
        print("🎨 Setting Target Color")
        print("1. You have 7 seconds to move your mouse to a pixel with the desired color")
        time.sleep(7)  # Give user time to move mouse to desired position
        
        # Capture color from current mouse position using multiple methods
        current_pos = pyautogui.position()
        color = None
        
        # Try multiple methods to get color
        try:
            screenshot = ImageGrab.grab()
            color = screenshot.getpixel(current_pos)
        except:
            pass
        
        if not color or not isinstance(color, (tuple, list)):
            try:
                color = self._get_pixel_win32(current_pos.x, current_pos.y)
            except:
                pass
        
        if not color or not isinstance(color, (tuple, list)):
            try:
                color = self._get_pixel_alternative(current_pos.x, current_pos.y)
            except:
                pass
        
        # Check if it's a valid RGB tuple
        if isinstance(color, (tuple, list)) and len(color) >= 3:
            self.target_color = tuple(color[:3])  # Use only first 3 values (RGB)
            print(f"✅ Color RGB saved: {self.target_color}")
        else:
            print(f"❌ Cannot read color: {color}")
            return False
        
        return True
    
    def get_pixel_color(self):
        """Read color from the specified point using multiple methods"""
        try:
            if self.monitor_point is None:
                print("❌ Monitor point not set")
                return None
            
            # Try multiple methods to get pixel color
            color = None
            
            # Method 1: Direct screen capture (fastest)
            try:
                screenshot = ImageGrab.grab()
                color = screenshot.getpixel(self.monitor_point)
            except:
                pass
            
            # Method 2: Win32 API (more reliable for protected apps)
            if not color or not isinstance(color, (tuple, list)):
                try:
                    color = self._get_pixel_win32(self.monitor_point.x, self.monitor_point.y)
                except:
                    pass
            
            # Method 3: Alternative screen capture
            if not color or not isinstance(color, (tuple, list)):
                try:
                    color = self._get_pixel_alternative(self.monitor_point.x, self.monitor_point.y)
                except:
                    pass
            
            # Check if it's a valid RGB tuple
            if isinstance(color, (tuple, list)) and len(color) >= 3:
                return tuple(color[:3])  # Use only first 3 values (RGB)
            else:
                print(f"❌ Invalid color format: {color}")
                return None
                
        except Exception as e:
            print(f"❌ Cannot read color: {e}")
            return None
    
    def _get_pixel_win32(self, x, y):
        """Get pixel color using Win32 API"""
        try:
            # Get device context
            hdc = win32gui.GetDC(0)
            # Get pixel color
            color = win32gui.GetPixel(hdc, x, y)
            win32gui.ReleaseDC(0, hdc)
            
            # Convert to RGB
            r = color & 0xFF
            g = (color >> 8) & 0xFF
            b = (color >> 16) & 0xFF
            return (r, g, b)
        except:
            return None
    
    def _get_pixel_alternative(self, x, y):
        """Alternative method using different screen capture"""
        try:
            # Use win32ui for screen capture
            hwin = win32gui.GetDesktopWindow()
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            
            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, 1, 1)
            memdc.SelectObject(bmp)
            
            memdc.BitBlt((0, 0), (1, 1), srcdc, (x, y), win32con.SRCCOPY)
            
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            
            color = tuple(bmpstr[2:5])  # RGB values
            
            win32gui.DeleteObject(bmp.GetHandle())
            memdc.DeleteDC()
            srcdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            
            return color
        except:
            return None
    
    def color_matches(self, current_color):
        """Check if color matches the target color"""
        if not current_color or not self.target_color:
            return False
        
        # Check if it's a tuple with 3 values (RGB)
        if not isinstance(current_color, (tuple, list)) or len(current_color) < 3:
            return False
        if not isinstance(self.target_color, (tuple, list)) or len(self.target_color) < 3:
            return False
        
        # Calculate color difference
        diff_r = abs(current_color[0] - self.target_color[0])
        diff_g = abs(current_color[1] - self.target_color[1])
        diff_b = abs(current_color[2] - self.target_color[2])
        
        # Check if difference is within acceptable range
        return (diff_r <= self.tolerance and 
                diff_g <= self.tolerance and 
                diff_b <= self.tolerance)
    
    def select_target_window(self):
        """Select the target window to send keys to"""
        print("🪟 Window Selection")
        print("1. You have 7 seconds to click on the target window")
        print("2. Make sure the target program is visible and clickable")
        time.sleep(7)  # Give user time to click on target window
        
        # Get the currently active window
        self.target_window = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(self.target_window)
        print(f"✅ Target window selected: {window_title}")
        return True
    
    def press_key(self):
        """Press the specified key using multiple methods"""
        current_time = time.time()
        if current_time - self.last_press_time >= self.cooldown:
            try:
                success = False
                
                # Method 1: Try with window focus and click
                if self.target_window:
                    try:
                        # Focus the target window first
                        win32gui.SetForegroundWindow(self.target_window)
                        time.sleep(0.1)  # Small delay to ensure focus
                        
                        # Click on the monitor point to ensure the window is active
                        if self.monitor_point:
                            pyautogui.click(self.monitor_point.x, self.monitor_point.y)
                            time.sleep(0.05)
                        
                        # Press the key
                        pyautogui.press(self.key_to_press)
                        success = True
                    except:
                        pass
                
                # Method 2: Try direct key press without focus
                if not success:
                    try:
                        pyautogui.press(self.key_to_press)
                        success = True
                    except:
                        pass
                
                # Method 3: Try using keyboard library
                if not success:
                    try:
                        keyboard.press_and_release(self.key_to_press)
                        success = True
                    except:
                        pass
                
                # Method 4: Try using win32api
                if not success:
                    try:
                        self._send_key_win32(self.key_to_press)
                        success = True
                    except:
                        pass
                
                if success:
                    self.last_press_time = current_time
                    print(f"⚡ Key pressed: {self.key_to_press}")
                    return True
                else:
                    print(f"❌ All key press methods failed for: {self.key_to_press}")
                    return False
                    
            except Exception as e:
                print(f"❌ Cannot press key: {e}")
                return False
        return False
    
    def _send_key_win32(self, key):
        """Send key using Win32 API"""
        try:
            # Map common keys to virtual key codes
            key_map = {
                'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
                'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
                'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
                'space': 0x20, 'enter': 0x0D, 'tab': 0x09,
                'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12
            }
            
            vk_code = key_map.get(key.lower(), ord(key.upper()))
            
            # Send key down
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.01)
            # Send key up
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            
        except Exception as e:
            print(f"❌ Win32 key press failed: {e}")
            raise
    
    def monitor_loop(self):
        """Color monitoring loop"""
        print("🔍 Starting color monitoring...")
        print(f"📍 Position: {self.monitor_point}")
        print(f"🎯 Target color: {self.target_color}")
        print(f"⌨️  Key: {self.key_to_press}")
        print(f"⏱️  Check interval: {self.check_interval}s")
        print(f"🕐 Cooldown: {self.cooldown}s")
        print("-" * 40)
        
        while self.running:
            try:
                # Skip monitoring if paused
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Read color from specified point
                current_color = self.get_pixel_color()
                
                if current_color:
                    # Show current color (every 10 seconds)
                    if int(time.time()) % 10 == 0:
                        print(f"📊 Current color: {current_color}")
                    
                    # Check if color matches
                    if self.color_matches(current_color):
                        print(f"✅ Target color found: {current_color}")
                        self.press_key()
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error occurred: {e}")
                time.sleep(1)
    
    def setup(self):
        """Initial setup"""
        print("🎮 Simple Auto HP Monitor")
        print("=" * 30)
        
        # Set key
        key_input = input(f"⌨️  Key to press (current: {self.key_to_press}): ").strip()
        if key_input:
            self.key_to_press = key_input.lower()
            print(f"✅ Key set: {self.key_to_press}")
        
        # Set color tolerance
        try:
            tolerance_input = input(f"🎨 Color tolerance (0-255, current: {self.tolerance}): ").strip()
            if tolerance_input:
                tolerance = int(tolerance_input)
                if 0 <= tolerance <= 255:
                    self.tolerance = tolerance
                    print(f"✅ Tolerance set: {self.tolerance}")
        except ValueError:
            print("❌ Invalid value, using default")
        
        # Set cooldown
        try:
            cooldown_input = input(f"⏱️  Cooldown (seconds, current: {self.cooldown}): ").strip()
            if cooldown_input:
                cooldown = float(cooldown_input)
                if cooldown >= 0.1:
                    self.cooldown = cooldown
                    print(f"✅ Cooldown set: {self.cooldown}s")
        except ValueError:
            print("❌ Invalid value, using default")
        
        print("\n" + "=" * 30)
        
        # Select target window
        if not self.select_target_window():
            return False
        
        print("\n" + "=" * 30)
        print("🎯 Press Enter to start setting monitor point...")
        input()
        
        # Set monitor point
        if not self.set_monitor_point():
            return False
        
        print("\n" + "=" * 30)
        print("🎯 Press Enter to start setting target color...")
        input()
        
        # Set target color
        if not self.set_target_color():
            return False
        
        return True
    
    def start(self):
        """Start the program"""
        if not self.setup():
            print("❌ Setup failed")
            return
        
        print("\n✅ Setup completed!")
        print("🛑 Press Enter to start monitoring...")
        input()
        
        # Start monitoring
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\n🔥 Program is now running!")
        print("🛑 Press 'F12' to stop program")
        print("⏸️  Press 'F11' to pause/resume")
        print("📊 Press 's' to show status")
        print("🎨 Press 'c' to check current color")
        
        # Wait for user commands
        try:
            while self.running:
                if keyboard.is_pressed('f12'):
                    break
                elif keyboard.is_pressed('f11'):
                    self.paused = not self.paused
                    status = "⏸️ Paused" if self.paused else "▶️ Resumed"
                    print(f"\n{status}")
                    time.sleep(0.5)  # Prevent double press
                elif keyboard.is_pressed('s'):
                    print(f"\n📊 Current status:")
                    print(f"   📍 Position: {self.monitor_point}")
                    print(f"   🎯 Target color: {self.target_color}")
                    print(f"   ⌨️  Key: {self.key_to_press}")
                    print(f"   ⏱️  Cooldown: {self.cooldown}s")
                    print(f"   ⏸️  Status: {'Paused' if self.paused else 'Running'}")
                    if self.target_window:
                        window_title = win32gui.GetWindowText(self.target_window)
                        print(f"   🪟 Target window: {window_title}")
                    time.sleep(0.5)
                elif keyboard.is_pressed('c'):
                    if not self.paused:
                        current_color = self.get_pixel_color()
                        if current_color:
                            matches = "✅ Match" if self.color_matches(current_color) else "❌ No match"
                            print(f"🎨 Current color: {current_color} {matches}")
                    else:
                        print("⏸️ Program paused - cannot check color")
                    time.sleep(0.5)
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        self.stop()
    
    def stop(self):
        """Stop the program"""
        self.running = False
        print("\n🛑 Program stopped")

def main():
    """Main function"""
    try:
        auto_hp = SimpleAutoHP()
        auto_hp.start()
    except Exception as e:
        print(f"❌ Critical error occurred: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user")

if __name__ == "__main__":
    main()