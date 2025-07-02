import pyautogui
import time
import keyboard
import threading
from PIL import ImageGrab

class SimpleAutoHP:
    def __init__(self):
        self.running = False
        self.monitor_point = None  # จุดที่จะตรวจสอบสี (x, y)
        self.target_color = None   # สีที่ต้องการตรวจจับ (R, G, B)
        self.key_to_press = 'f1'   # ปุ่มที่จะกด
        self.tolerance = 30        # ความคลาดเคลื่อนของสี (0-255)
        self.check_interval = 0.5  # ตรวจสอบทุก 0.5 วินาที
        self.cooldown = 2.0        # รอ 2 วินาทีระหว่างการกดปุ่ม
        self.last_press_time = 0
        
        # ป้องกันอุบัติเหตุ
        pyautogui.FAILSAFE = True
        
    def set_monitor_point(self):
        """ตั้งค่าจุดที่จะตรวจสอบสี"""
        print("📍 การตั้งค่าจุดตรวจสอบ")
        print("1. เลื่อนเมาส์ไปยังจุดที่ต้องการตรวจสอบ")
        print("2. กด SPACE เพื่อบันทึกตำแหน่ง")
        print("3. กด ESC เพื่อยกเลิก")
        
        while True:
            if keyboard.is_pressed('space'):
                self.monitor_point = pyautogui.position()
                print(f"✅ บันทึกตำแหน่ง: {self.monitor_point}")
                time.sleep(0.5)  # ป้องกันการกดซ้ำ
                break
            elif keyboard.is_pressed('esc'):
                print("❌ ยกเลิกการตั้งค่า")
                return False
            time.sleep(0.1)
        
        return True
    
    def set_target_color(self):
        """ตั้งค่าสีที่ต้องการตรวจจับ"""
        if not self.monitor_point:
            print("❌ กรุณาตั้งค่าจุดตรวจสอบก่อน")
            return False
            
        print("🎨 การตั้งค่าสีเป้าหมาย")
        print("1. เลื่อนเมาส์ไปยังพิกเซลที่มีสีที่ต้องการ")
        print("2. กด SPACE เพื่อบันทึกสี")
        print("3. กด ESC เพื่อยกเลิก")
        
        while True:
            if keyboard.is_pressed('space'):
                # จับสีจากตำแหน่งเมาส์ปัจจุบัน
                current_pos = pyautogui.position()
                screenshot = ImageGrab.grab()
                self.target_color = screenshot.getpixel(current_pos)
                print(f"✅ บันทึกสี RGB: {self.target_color}")
                time.sleep(0.5)
                break
            elif keyboard.is_pressed('esc'):
                print("❌ ยกเลิกการตั้งค่า")
                return False
            time.sleep(0.1)
        
        return True
    
    def get_pixel_color(self):
        """อ่านสีจากจุดที่กำหนด"""
        try:
            screenshot = ImageGrab.grab()
            color = screenshot.getpixel(self.monitor_point)
            return color
        except Exception as e:
            print(f"❌ ไม่สามารถอ่านสีได้: {e}")
            return None
    
    def color_matches(self, current_color):
        """ตรวจสอบว่าสีตรงกับสีเป้าหมายหรือไม่"""
        if not current_color or not self.target_color:
            return False
        
        # คำนวณความแตกต่างของสี
        diff_r = abs(current_color[0] - self.target_color[0])
        diff_g = abs(current_color[1] - self.target_color[1])
        diff_b = abs(current_color[2] - self.target_color[2])
        
        # ตรวจสอบว่าความแตกต่างอยู่ในช่วงที่ยอมรับได้
        return (diff_r <= self.tolerance and 
                diff_g <= self.tolerance and 
                diff_b <= self.tolerance)
    
    def press_key(self):
        """กดปุ่มที่กำหนด"""
        current_time = time.time()
        if current_time - self.last_press_time >= self.cooldown:
            try:
                pyautogui.press(self.key_to_press)
                self.last_press_time = current_time
                print(f"⚡ กดปุ่ม: {self.key_to_press}")
                return True
            except Exception as e:
                print(f"❌ ไม่สามารถกดปุ่มได้: {e}")
                return False
        return False
    
    def monitor_loop(self):
        """ลูปการตรวจสอบสี"""
        print("🔍 เริ่มการตรวจสอบสี...")
        print(f"📍 ตำแหน่ง: {self.monitor_point}")
        print(f"🎯 สีเป้าหมาย: {self.target_color}")
        print(f"⌨️  ปุ่ม: {self.key_to_press}")
        print(f"⏱️  ตรวจสอบทุก: {self.check_interval}s")
        print(f"🕐 Cooldown: {self.cooldown}s")
        print("-" * 40)
        
        while self.running:
            try:
                # อ่านสีจากจุดที่กำหนด
                current_color = self.get_pixel_color()
                
                if current_color:
                    # แสดงสีปัจจุบัน (ทุก 10 ครั้ง)
                    if int(time.time()) % 10 == 0:
                        print(f"📊 สีปัจจุบัน: {current_color}")
                    
                    # ตรวจสอบว่าสีตรงกันหรือไม่
                    if self.color_matches(current_color):
                        print(f"✅ พบสีเป้าหมาย: {current_color}")
                        self.press_key()
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")
                time.sleep(1)
    
    def setup(self):
        """ตั้งค่าเริ่มต้น"""
        print("🎮 Simple Auto HP Monitor")
        print("=" * 30)
        
        # ตั้งค่าปุ่ม
        key_input = input(f"⌨️  ปุ่มที่จะกด (ปัจจุบัน: {self.key_to_press}): ").strip()
        if key_input:
            self.key_to_press = key_input.lower()
            print(f"✅ ตั้งค่าปุ่ม: {self.key_to_press}")
        
        # ตั้งค่าความคลาดเคลื่อนสี
        try:
            tolerance_input = input(f"🎨 ความคลาดเคลื่อนสี (0-255, ปัจจุบัน: {self.tolerance}): ").strip()
            if tolerance_input:
                tolerance = int(tolerance_input)
                if 0 <= tolerance <= 255:
                    self.tolerance = tolerance
                    print(f"✅ ตั้งค่าความคลาดเคลื่อน: {self.tolerance}")
        except ValueError:
            print("❌ ค่าไม่ถูกต้อง ใช้ค่าเดิม")
        
        # ตั้งค่า Cooldown
        try:
            cooldown_input = input(f"⏱️  Cooldown (วินาที, ปัจจุบัน: {self.cooldown}): ").strip()
            if cooldown_input:
                cooldown = float(cooldown_input)
                if cooldown >= 0.1:
                    self.cooldown = cooldown
                    print(f"✅ ตั้งค่า Cooldown: {self.cooldown}s")
        except ValueError:
            print("❌ ค่าไม่ถูกต้อง ใช้ค่าเดิม")
        
        print("\n" + "=" * 30)
        
        # ตั้งค่าจุดตรวจสอบ
        if not self.set_monitor_point():
            return False
        
        # ตั้งค่าสีเป้าหมาย
        if not self.set_target_color():
            return False
        
        return True
    
    def start(self):
        """เริ่มโปรแกรม"""
        if not self.setup():
            print("❌ การตั้งค่าล้มเหลว")
            return
        
        print("\n✅ การตั้งค่าเสร็จสิ้น!")
        print("🚀 กด Enter เพื่อเริ่มการทำงาน...")
        input()
        
        # เริ่มการตรวจสอบ
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\n🔥 โปรแกรมเริ่มทำงานแล้ว!")
        print("🛑 กด 'q' เพื่อหยุดโปรแกรม")
        print("📊 กด 's' เพื่อดูสถานะ")
        print("🎨 กด 'c' เพื่อดูสีปัจจุบัน")
        
        # รอคำสั่งจากผู้ใช้
        try:
            while self.running:
                if keyboard.is_pressed('q'):
                    break
                elif keyboard.is_pressed('s'):
                    print(f"\n📊 สถานะปัจจุบัน:")
                    print(f"   📍 ตำแหน่ง: {self.monitor_point}")
                    print(f"   🎯 สีเป้าหมาย: {self.target_color}")
                    print(f"   ⌨️  ปุ่ม: {self.key_to_press}")
                    print(f"   ⏱️  Cooldown: {self.cooldown}s")
                    time.sleep(0.5)
                elif keyboard.is_pressed('c'):
                    current_color = self.get_pixel_color()
                    if current_color:
                        matches = "✅ ตรง" if self.color_matches(current_color) else "❌ ไม่ตรง"
                        print(f"🎨 สีปัจจุบัน: {current_color} {matches}")
                    time.sleep(0.5)
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        self.stop()
    
    def stop(self):
        """หยุดโปรแกรม"""
        self.running = False
        print("\n🛑 โปรแกรมหยุดทำงานแล้ว")

def main():
    """ฟังก์ชันหลัก"""
    try:
        auto_hp = SimpleAutoHP()
        auto_hp.start()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดร้ายแรง: {e}")
    except KeyboardInterrupt:
        print("\n🛑 โปรแกรมถูกหยุดโดยผู้ใช้")

if __name__ == "__main__":
    main()