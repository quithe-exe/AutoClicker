import customtkinter as ctk
import pyautogui
import threading
import time
import keyboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Clicker")
        self.geometry("320x420")

        self.running = False
        self.click_times = []
        self.current_hotkey = "f6"
        self.waiting_for_key = False

        # Interval
        self.label = ctk.CTkLabel(self, text="Click interval (seconds):")
        self.label.pack(pady=10)

        self.interval_entry = ctk.CTkEntry(self)
        self.interval_entry.insert(0, "1")
        self.interval_entry.pack(pady=5)

        # Mouse button
        self.button_label = ctk.CTkLabel(self, text="Mouse button:")
        self.button_label.pack(pady=10)

        self.button_option = ctk.CTkOptionMenu(
            self,
            values=["left", "right", "middle"]
        )
        self.button_option.set("left")
        self.button_option.pack(pady=5)

        # Buttons
        self.start_button = ctk.CTkButton(self, text="Start", command=self.start_clicking)
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self, text="Stop", command=self.stop_clicking)
        self.stop_button.pack(pady=5)

        # Status
        self.status_label = ctk.CTkLabel(self, text="Status: 🔴 Stopped")
        self.status_label.pack(pady=10)

        # CPS
        self.cps_label = ctk.CTkLabel(self, text="CPS: 0")
        self.cps_label.pack(pady=5)

        # Hotkey section
        self.hotkey_info = ctk.CTkLabel(self, text=f"Current Hotkey: {self.current_hotkey}")
        self.hotkey_info.pack(pady=10)

        self.set_hotkey_button = ctk.CTkButton(
            self,
            text="Set Hotkey (press key)",
            command=self.wait_for_hotkey
        )
        self.set_hotkey_button.pack(pady=5)

        # Register default hotkey
        keyboard.add_hotkey(self.current_hotkey, self.toggle_clicking)

        # CPS updater
        self.update_cps_loop()

    def wait_for_hotkey(self):
        self.waiting_for_key = True
        self.hotkey_info.configure(text="Press any key...")

        threading.Thread(target=self.capture_key, daemon=True).start()

    def capture_key(self):
        key_event = keyboard.read_event()
        if key_event.event_type == keyboard.KEY_DOWN and self.waiting_for_key:
            new_key = key_event.name

            try:
                keyboard.remove_hotkey(self.current_hotkey)
            except:
                pass

            try:
                keyboard.add_hotkey(new_key, self.toggle_clicking)
                self.current_hotkey = new_key
                self.hotkey_info.configure(text=f"Current Hotkey: {new_key}")
            except:
                self.hotkey_info.configure(text="Invalid key!")

            self.waiting_for_key = False

    def update_status(self):
        if self.running:
            self.status_label.configure(text="Status: 🟢 Running")
        else:
            self.status_label.configure(text="Status: 🔴 Stopped")

    def click_loop(self, interval, button):
        while self.running:
            pyautogui.click(button=button)

            now = time.time()
            self.click_times.append(now)

            time.sleep(interval)

    def update_cps_loop(self):
        now = time.time()
        self.click_times = [t for t in self.click_times if now - t <= 1]

        cps = len(self.click_times)
        self.cps_label.configure(text=f"CPS: {cps}")

        self.after(100, self.update_cps_loop)

    def start_clicking(self):
        if not self.running:
            try:
                interval = float(self.interval_entry.get())
                button = self.button_option.get()
            except:
                return

            self.running = True
            self.click_times.clear()
            self.update_status()

            threading.Thread(
                target=self.click_loop,
                args=(interval, button),
                daemon=True
            ).start()

    def stop_clicking(self):
        self.running = False
        self.update_status()

    def toggle_clicking(self):
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

if __name__ == "__main__":
    app = AutoClickerApp()
    app.mainloop()
