import pyautogui
import time
import keyboard
import threading
from PIL import ImageGrab

class SimpleAutoHPDebug:
    def __init__(self):
        self.running = False
        self.paused = False
        self.monitor_point = None
        self.target_color = None
        self.key_to_press = 'f1'
        self.tolerance = 30
        self.check_interval = 0.5
        self.cooldown = 2.0
        self.last_press_time = 0
        
        # Safety feature
        pyautogui.FAILSAFE = True
        print("🔧 Debug mode initialized")
        
    def set_monitor_point(self):
        """Set the point to monitor color"""
        print("📍 Setting Monitor Point")
        print("1. You have 7 seconds to move your mouse to the desired position")
        print("2. Move your mouse now...")
        
        for i in range(7, 0, -1):
            print(f"   Time remaining: {i} seconds")
            time.sleep(1)
        
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
        print("2. Move your mouse to the color you want to detect...")
        
        for i in range(7, 0, -1):
            print(f"   Time remaining: {i} seconds")
            time.sleep(1)
        
        # Capture color from current mouse position
        current_pos = pyautogui.position()
        print(f"📱 Mouse position: {current_pos}")
        
        try:
            screenshot = ImageGrab.grab()
            color = screenshot.getpixel(current_pos)
            print(f"🎨 Raw color data: {color}")
            
            # Check if it's a valid RGB tuple
            if isinstance(color, (tuple, list)) and len(color) >= 3:
                self.target_color = tuple(color[:3])  # Use only first 3 values (RGB)
                print(f"✅ Color RGB saved: {self.target_color}")
                return True
            else:
                print(f"❌ Invalid color format: {color}")
                return False
                
        except Exception as e:
            print(f"❌ Error capturing color: {e}")
            return False
    
    def get_pixel_color(self):
        """Read color from the specified point"""
        try:
            if self.monitor_point is None:
                print("❌ Monitor point not set")
                return None
            
            screenshot = ImageGrab.grab()
            color = screenshot.getpixel(self.monitor_point)
            
            # Check if it's a valid RGB tuple
            if isinstance(color, (tuple, list)) and len(color) >= 3:
                return tuple(color[:3])  # Use only first 3 values (RGB)
            else:
                print(f"❌ Invalid color format: {color}")
                return None
                
        except Exception as e:
            print(f"❌ Cannot read color: {e}")
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
        
        # Debug info
        print(f"🔍 Color check: Current={current_color}, Target={self.target_color}")
        print(f"   Diff: R={diff_r}, G={diff_g}, B={diff_b}, Tolerance={self.tolerance}")
        
        # Check if difference is within acceptable range
        matches = (diff_r <= self.tolerance and 
                  diff_g <= self.tolerance and 
                  diff_b <= self.tolerance)
        
        print(f"   Match: {matches}")
        return matches
    
    def press_key(self):
        """Press the specified key"""
        current_time = time.time()
        if current_time - self.last_press_time >= self.cooldown:
            try:
                print(f"⌨️ Attempting to press key: {self.key_to_press}")
                pyautogui.press(self.key_to_press)
                self.last_press_time = current_time
                print(f"⚡ Key pressed successfully: {self.key_to_press}")
                return True
            except Exception as e:
                print(f"❌ Cannot press key: {e}")
                return False
        else:
            print(f"⏱️ Cooldown active, skipping key press")
            return False
    
    def monitor_loop(self):
        """Color monitoring loop"""
        print("🔍 Starting color monitoring...")
        print(f"📍 Position: {self.monitor_point}")
        print(f"🎯 Target color: {self.target_color}")
        print(f"⌨️ Key: {self.key_to_press}")
        print(f"⏱️ Check interval: {self.check_interval}s")
        print(f"🕐 Cooldown: {self.cooldown}s")
        print("-" * 40)
        
        check_count = 0
        
        while self.running:
            try:
                # Skip monitoring if paused
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                check_count += 1
                
                # Read color from specified point
                current_color = self.get_pixel_color()
                
                if current_color:
                    # Show current color every 10 checks
                    if check_count % 10 == 0:
                        print(f"📊 Check #{check_count} - Current color: {current_color}")
                    
                    # Check if color matches
                    if self.color_matches(current_color):
                        print(f"✅ Target color found: {current_color}")
                        self.press_key()
                else:
                    print(f"❌ Check #{check_count} - Failed to read color")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("🛑 Keyboard interrupt detected")
                break
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                time.sleep(1)
    
    def setup(self):
        """Initial setup"""
        print("🎮 Simple Auto HP Monitor - DEBUG MODE")
        print("=" * 40)
        
        # Set key
        key_input = input(f"⌨️ Key to press (current: {self.key_to_press}): ").strip()
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
            cooldown_input = input(f"⏱️ Cooldown (seconds, current: {self.cooldown}): ").strip()
            if cooldown_input:
                cooldown = float(cooldown_input)
                if cooldown >= 0.1:
                    self.cooldown = cooldown
                    print(f"✅ Cooldown set: {self.cooldown}s")
        except ValueError:
            print("❌ Invalid value, using default")
        
        print("\n" + "=" * 40)
        
        # Set monitor point
        if not self.set_monitor_point():
            return False
        
        print("\n" + "=" * 40)
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
        print("⏸️ Press 'F11' to pause/resume")
        print("📊 Press 's' to show status")
        print("🎨 Press 'c' to check current color")
        
        # Wait for user commands
        try:
            while self.running:
                if keyboard.is_pressed('f12'):
                    print("🛑 F12 pressed - stopping program")
                    break
                elif keyboard.is_pressed('f11'):
                    self.paused = not self.paused
                    status = "⏸️ Paused" if self.paused else "▶️ Resumed"
                    print(f"\n{status}")
                    time.sleep(0.5)
                elif keyboard.is_pressed('s'):
                    print(f"\n📊 Current status:")
                    print(f"   📍 Position: {self.monitor_point}")
                    print(f"   🎯 Target color: {self.target_color}")
                    print(f"   ⌨️ Key: {self.key_to_press}")
                    print(f"   ⏱️ Cooldown: {self.cooldown}s")
                    print(f"   ⏸️ Status: {'Paused' if self.paused else 'Running'}")
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
            print("🛑 Keyboard interrupt detected")
        
        self.stop()
    
    def stop(self):
        """Stop the program"""
        self.running = False
        print("\n🛑 Program stopped")

def main():
    """Main function"""
    try:
        print("🚀 Starting Simple Auto HP Monitor - DEBUG MODE")
        auto_hp = SimpleAutoHPDebug()
        auto_hp.start()
    except Exception as e:
        print(f"❌ Critical error occurred: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user")

if __name__ == "__main__":
    main() 