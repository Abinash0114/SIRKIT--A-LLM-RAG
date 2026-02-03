import os
import shutil
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, font, messagebox, simpledialog
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

from voice_engine import VoiceEngine
from llm_client import LLMClient
from file_monitor import FileMonitor
from camera_engine import CameraEngine
import config

class SirkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SIRKIT")
        self.root.geometry("1100x650")
        self.root.configure(bg="#8a8aa8")  # Main background

        # Fonts
        self.title_font = font.Font(family="Segoe UI", size=24, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=18)
        self.button_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.text_font = font.Font(family="Consolas", size=10)

        # State
        self.voice = None
        self.llm = None
        self.camera = None
        self.camera_session_active = False
        self.running = False
        self.current_preview_path = None
        self.current_browse_dir = config.IMAGES_DIR

        self.setup_ui()
        self.refresh_file_list()

        # Active File Monitoring
        self.monitor = None
        self.start_monitor()

    def setup_ui(self):
        # Top Title
        title_label = tk.Label(self.root, text="SIRKIT", fg="#2a2a4a", bg="#8a8aa8", font=self.title_font)
        title_label.pack(pady=10)

        # Main Layout Frame (Two Columns)
        self.main_frame = tk.Frame(self.root, bg="#8a8aa8")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # --- LEFT COLUMN: CONVERSATION ---
        self.left_col = tk.Frame(self.main_frame, bg="#7b7ba1", bd=2, relief=tk.FLAT)
        self.left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(self.left_col, text="conversation", fg="white", bg="#7b7ba1", font=self.header_font).pack(pady=5)
        
        # Scrolled Text for history (Read-only)
        self.log_area = scrolledtext.ScrolledText(
            self.left_col, wrap=tk.WORD, bg="#c4c4d4", fg="#2a2a4a", 
            font=self.text_font, bd=0, highlightthickness=0, state=tk.DISABLED
        )
        self.log_area.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        # Input Area (at bottom of left col)
        self.input_frame = tk.Frame(self.left_col, bg="#7b7ba1")
        self.input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.text_input = tk.Entry(
            self.input_frame, bg="#c4c4d4", fg="#2a2a4a", 
            insertbackground="#2a2a4a", font=("Arial", 12), bd=0
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.text_input.bind("<Return>", lambda e: self.send_text())

        self.send_btn = tk.Button(
            self.input_frame, text="send", command=self.send_text, 
            bg="#3e3e4e", fg="#5ddc7c", font=("Arial", 10, "bold"), 
            bd=0, padx=15, cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # --- RIGHT COLUMN: FILES / PREVIEW ---
        self.right_col = tk.Frame(self.main_frame, bg="#7b7ba1", bd=2, relief=tk.FLAT)
        self.right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Header for right column
        self.right_header_frame = tk.Frame(self.right_col, bg="#7b7ba1")
        self.right_header_frame.pack(fill=tk.X, pady=5)

        self.back_btn = tk.Button(
            self.right_header_frame, text="back", command=self.go_back,
            bg="#3e3e4e", fg="white", font=("Arial", 10, "bold"),
            bd=0, padx=10, cursor="hand2"
        )
        self.back_btn.pack(side=tk.LEFT, padx=15)
        self.back_btn.pack_forget() # Hidden by default

        self.right_label = tk.Label(
            self.right_header_frame, text="Files", fg="white", 
            bg="#7b7ba1", font=self.header_font
        )
        self.right_label.pack(expand=True)

        # Files List / Preview Container
        self.display_container = tk.Frame(self.right_col, bg="#6a6a8a")
        self.display_container.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        # Listbox for files
        self.file_listbox = tk.Listbox(
            self.display_container, bg="#6a6a8a", fg="white", 
            font=("Segoe UI", 12), bd=0, highlightthickness=0, 
            selectbackground="#4a4a6a"
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind("<Double-Button-1>", self.on_item_double_click)
        self.file_listbox.bind("<Button-3>", self.show_context_menu)

        # Preview Label (Hidden by default)
        self.preview_label = tk.Label(self.display_container, bg="#6a6a8a")

        # Context Menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#3e3e4e", fg="white", activebackground="#4a4a6a")
        self.context_menu.add_command(label="Open", command=self.on_open)
        self.context_menu.add_command(label="New Folder", command=self.on_new_folder)
        self.context_menu.add_command(label="Rename", command=self.on_rename)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.on_delete)

        # Control Buttons (Status and Start/Stop)
        self.control_frame = tk.Frame(self.root, bg="#8a8aa8")
        self.control_frame.pack(fill=tk.X, padx=40, pady=(0, 20))

        self.status_var = tk.StringVar(value="Status: Ready")
        self.status_label = tk.Label(self.control_frame, textvariable=self.status_var, fg="#2a2a4a", bg="#8a8aa8", font=("Arial", 10, "italic"))
        self.status_label.pack(side=tk.LEFT)

        self.stop_btn = tk.Button(
            self.control_frame, text="Stop", command=self.exit_app, 
            bg="#ff4d4d", fg="white", font=self.button_font, 
            bd=0, width=10, cursor="hand2"
        )
        self.stop_btn.pack(side=tk.RIGHT, padx=5)

        self.start_btn = tk.Button(
            self.control_frame, text="Start", command=self.start_backend, 
            bg="#4caf50", fg="white", font=self.button_font, 
            bd=0, width=10, cursor="hand2"
        )
        self.start_btn.pack(side=tk.RIGHT, padx=5)

        # Enable Drag and Drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            items = os.listdir(self.current_browse_dir)
            # Folders first
            for item in sorted(items):
                if os.path.isdir(os.path.join(self.current_browse_dir, item)):
                    self.file_listbox.insert(tk.END, "📁 " + item)
            # Files next
            for item in sorted(items):
                if os.path.isfile(os.path.join(self.current_browse_dir, item)):
                    self.file_listbox.insert(tk.END, "📄 " + item)
            
            # Sync with LLM background
            if self.llm:
                threading.Thread(target=self.sync_files_to_ai, daemon=True).start()
        except Exception as e:
            self.log(f"Error listing files: {e}")

    def sync_files_to_ai(self):
        if not self.llm: return
        try:
            listing_text = self.llm.rag.sync_folder_contents(self.current_browse_dir)
            self.llm.set_files_context(listing_text)
        except: pass

    def on_item_double_click(self, event):
        self.on_open()

    def on_open(self):
        selection = self.file_listbox.curselection()
        if not selection: return
        
        item_text = self.file_listbox.get(selection[0])
        item_name = item_text[2:] # Remove icon
        item_path = os.path.join(self.current_browse_dir, item_name)

        if os.path.isdir(item_path):
            self.current_browse_dir = item_path
            self.back_btn.pack(side=tk.LEFT, padx=15)
            self.refresh_file_list()
        else:
            # Check if it's an image
            ext = os.path.splitext(item_name)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                self.show_preview(item_path)

    def show_context_menu(self, event):
        # Select item on right click
        idx = self.file_listbox.nearest(event.y)
        self.file_listbox.selection_clear(0, tk.END)
        self.file_listbox.selection_set(idx)
        self.file_listbox.activate(idx)
        self.context_menu.post(event.x_root, event.y_root)

    def on_new_folder(self):
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:", parent=self.root)
        if folder_name:
            new_path = os.path.join(self.current_browse_dir, folder_name)
            try:
                os.makedirs(new_path, exist_ok=False)
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")

    def on_delete(self):
        selection = self.file_listbox.curselection()
        if not selection: return
        
        item_text = self.file_listbox.get(selection[0])
        item_name = item_text[2:]
        item_path = os.path.join(self.current_browse_dir, item_name)
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete item: {e}")

    def on_rename(self):
        selection = self.file_listbox.curselection()
        if not selection: return
        
        item_text = self.file_listbox.get(selection[0])
        item_name = item_text[2:]
        old_path = os.path.join(self.current_browse_dir, item_name)
        
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=item_name, parent=self.root)
        if new_name and new_name != item_name:
            new_path = os.path.join(self.current_browse_dir, new_name)
            try:
                os.rename(old_path, new_path)
                # Success - the file monitor will handle RAG updates if it was a file
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename item: {e}")

    def show_preview(self, path):
        try:
            image = Image.open(path)
            # Resize to fit display container
            container_w = self.display_container.winfo_width()
            container_h = self.display_container.winfo_height()
            
            # Maintain aspect ratio
            image.thumbnail((container_w, container_h), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo # Keep reference
            
            self.file_listbox.pack_forget()
            self.preview_label.pack(fill=tk.BOTH, expand=True)
            self.right_label.config(text="preview")
            self.back_btn.pack(side=tk.LEFT, padx=15)
            self.current_preview_path = path
        except Exception as e:
            self.log(f"Error loading image: {e}")

    def go_back(self):
        if self.current_preview_path:
            # Back from image preview
            self.preview_label.pack_forget()
            self.file_listbox.pack(fill=tk.BOTH, expand=True)
            self.right_label.config(text="Files")
            self.current_preview_path = None
            # Only hide back button if we are also at root
            if self.current_browse_dir == config.IMAGES_DIR:
                self.back_btn.pack_forget()
        else:
            # Back from subfolder
            parent = os.path.dirname(self.current_browse_dir)
            if parent.startswith(config.IMAGES_DIR):
                self.current_browse_dir = parent
                self.refresh_file_list()
                if self.current_browse_dir == config.IMAGES_DIR:
                    self.back_btn.pack_forget()

    def handle_drop(self, event):
        # Extract file paths from event data (handles curly braces for spaces)
        files = self.root.tk.splitlist(event.data)
        imported_count = 0
        for fpath in files:
            if os.path.isfile(fpath):
                dest = os.path.join(self.current_browse_dir, os.path.basename(fpath))
                try:
                    shutil.copy2(fpath, dest)
                    self.log(f"SYSTEM: File imported to workspace: {os.path.basename(fpath)}")
                    imported_count += 1
                except Exception as e:
                    self.log(f"Error importing {fpath}: {e}")
        
        if imported_count > 0:
            self.refresh_file_list()
            # If backend is running, notify the assistant via speech or log
            if self.llm:
                self.log(f"SIRKIT: I noticed {imported_count} new item(s) in your workspace. I've indexed them for you.")

    def start_backend(self):
        if self.running: return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.backend_loop, daemon=True).start()

    def perform_capture(self, source="Voice"):
        """Executes the capture function."""
        if not self.camera:
            self.camera = CameraEngine()
            
        # Auto-start session if not active to ensure persistent permission
        if not self.camera_session_active:
            self.log("ACTION: Auto-starting Camera Session...")
            if self.camera.start_session():
                self.camera_session_active = True
                self.voice.speak("Camera initialized.")
            else:
                self.voice.speak("Could not initialize camera.")
                return False
            
        self.log(f"ACTION: Capturing image via {source}...")
        self.voice.speak("Clicking.")
        
        frame = self.camera.capture_image()
        if frame is not None:
            saved_path = self.camera.save_image(frame)
            if saved_path:
                filename = os.path.basename(saved_path)
                self.log(f"SUCCESS: Saved to {filename}")
                self.voice.speak("Picture clicked and saved.")
                # File monitor will handle the rest, but we update memory for immediacy
                if self.llm:
                    self.llm.memory.add_message('assistant', f"I just clicked a picture named {filename}")
                return True
            else:
                self.voice.speak("I failed to save the image.")
        else:
            self.voice.speak("I couldn't access the camera.")
        return False

    def backend_loop(self):
        try:
            self.status_var.set("Status: Loading Models...")
            self.log("Initializing Engines...")
            if not self.voice:
                self.voice = VoiceEngine()
            if not self.llm:
                self.llm = LLMClient()
                # Initial sync
                self.sync_files_to_ai()
            if not self.camera:
                self.camera = CameraEngine()
            
            self.status_var.set(f"Status: Ready - Say '{config.WAKE_WORD}'")
            self.log("SYSTEM READY")
            self.voice.speak("System initialized. I am listening.")

            while self.running:
                if self.voice.listen_for_wake_word():
                    self.status_var.set("Status: Active Session")
                    self.log("\n[!] Assistant Activated")
                    self.voice.speak("How can I help you?")
                    
                    session_active = True
                    while session_active and self.running:
                        self.status_var.set("Status: Listening...")
                        user_text = self.voice.listen_and_transcribe()
                        
                        if not user_text:
                            self.log("Session Timeout (Silence)")
                            self.voice.speak("Going to sleep. Say Hey Jarvis to wake me up again.")
                            session_active = False
                            continue

                        self.log(f"YOU: {user_text}")
                        
                        stop_phrases = ["stop", "exit", "goodbye", "thank you", "that's all"]
                        if any(phrase in user_text.lower() for phrase in stop_phrases):
                            self.voice.speak("You're welcome. Standing by.")
                            self.log("SESSION ENDED")
                            session_active = False
                            continue
                        
                        # Command Parsing: Camera Mode
                        user_text_lower = user_text.lower()
                        
                        if "capture" in user_text_lower and not "decapture" in user_text_lower:
                            self.log("ACTION: Activating Camera Mode...")
                            if not self.camera_session_active:
                                if self.camera.start_session():
                                    self.camera_session_active = True
                                    self.voice.speak("Camera active. Say click to take photos.")
                                else:
                                    self.voice.speak("Failed to activate camera.")
                            else:
                                self.voice.speak("Camera is already active.")
                            continue

                        if "decapture" in user_text_lower:
                            self.log("ACTION: Deactivating Camera Mode...")
                            if self.camera_session_active:
                                self.camera.stop_session()
                                self.camera_session_active = False
                                self.voice.speak("Camera deactivated.")
                            else:
                                self.voice.speak("Camera is not active.")
                            continue

                        if "click" in user_text_lower:
                            self.perform_capture(source="Voice")
                            continue

                        self.status_var.set("Status: Thinking...")
                        ai_response = self.llm.chat(user_text)
                        
                        self.log(f"JARVIS: {ai_response}")
                        self.status_var.set("Status: Speaking...")
                        self.voice.speak(ai_response)
                        self.status_var.set("Status: Active Session (Listening)")
                
                self.status_var.set("Status: Ready - Say 'Hey Jarvis'")
                time.sleep(0.1)
        except Exception as e:
            self.log(f"BACKEND ERROR: {e}")
            self.running = False
            self.start_btn.config(state=tk.NORMAL)

    def send_text(self):
        query = self.text_input.get().strip()
        if not query: return
        
        self.text_input.delete(0, tk.END)
        self.log(f"YOU (Text): {query}")
        threading.Thread(target=self.process_text_query, args=(query,), daemon=True).start()

    def process_text_query(self, query):
        try:
            if not self.llm:
                self.log("Initializing LLM...")
                self.llm = LLMClient()
                self.sync_files_to_ai()
            if not self.voice:
                self.voice = VoiceEngine()

            # Command Parsing: Camera Mode
            query_lower = query.lower()
            
            if "capture" in query_lower and not "decapture" in query_lower:
                self.log("ACTION: Activating Camera Mode...")
                if not self.camera_session_active:
                    if self.camera.start_session():
                        self.camera_session_active = True
                        self.voice.speak("Camera active.")
                        self.status_var.set(f"Status: Camera Mode")
                    else:
                        self.voice.speak("Failed.")
                else:
                    self.voice.speak("Already active.")
                return 

            if "decapture" in query_lower:
                self.log("ACTION: Deactivating Camera Mode...")
                if self.camera_session_active:
                    self.camera.stop_session()
                    self.camera_session_active = False
                    self.voice.speak("Camera deactivated.")
                    self.status_var.set(f"Status: Ready")
                else:
                    self.voice.speak("Not active.")
                return

            if "click" in query_lower:
                if self.perform_capture(source="Text"):
                    return # Skip LLM chat

            self.status_var.set("Status: Thinking...")
            ai_response = self.llm.chat(query)
            
            self.log(f"JARVIS: {ai_response}")
            self.status_var.set("Status: Speaking...")
            self.voice.speak(ai_response)
            self.status_var.set(f"Status: Ready - Say '{config.WAKE_WORD}'")
            self.status_var.set(f"Status: Ready - Say '{config.WAKE_WORD}'")
        except Exception as e:
            self.log(f"TEXT QUERY ERROR: {e}")
            self.status_var.set("Status: Error")

    def exit_app(self):
        self.running = False
        if self.monitor:
            self.monitor.stop()
        self.root.destroy()

    def start_monitor(self):
        # We need a dummy RAG engine if LLM isn't loaded yet to avoid delay
        # but better to just use the one llm_client will create.
        # For now, let's wait until start_backend or initialize it here.
        from rag_engine import RAGEngine
        self.monitor_rag = RAGEngine()
        self.monitor = FileMonitor(config.IMAGES_DIR, self.monitor_rag, self.on_fs_change)
        self.monitor.start()

    def on_fs_change(self, change_type, filename):
        # This runs in the watcher thread, so use root.after for UI updates
        msg = f"SIRKIT: {change_type.capitalize()} detected: {filename}"
        self.root.after(0, lambda: self._handle_fs_event(msg))

    def _handle_fs_event(self, msg):
        self.log(msg)
        self.refresh_file_list()
        # If assistant is active, maybe notify
        if self.voice and self.running:
            # self.voice.speak("I noticed a change in your files.") # Optional, might be annoying
            pass

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SirkitGUI(root)
    root.mainloop()
