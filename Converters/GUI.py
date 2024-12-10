import cv2
import numpy as np
import base58
import json
import customtkinter as ctk
from tkinter import filedialog
import threading
import os

class VideoConverterGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.window = ctk.CTk()
        self.window.title("Video-Text Converter")
        self.window.geometry("600x400")
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.title_label = ctk.CTkLabel(self.main_frame, text="Video-Text Converter", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill="x", padx=20, pady=10)
        self.input_label = ctk.CTkLabel(self.input_frame, text="Input File:")
        self.input_label.pack(side="left", padx=5)
        self.input_path = ctk.CTkEntry(self.input_frame)
        self.input_path.pack(side="left", fill="x", expand=True, padx=5)
        self.browse_btn = ctk.CTkButton(self.input_frame, text="Browse", command=self.browse_input)
        self.browse_btn.pack(side="right", padx=5)
        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.pack(fill="x", padx=20, pady=10)
        self.output_label = ctk.CTkLabel(self.output_frame, text="Output File:")
        self.output_label.pack(side="left", padx=5)
        self.output_path = ctk.CTkEntry(self.output_frame)
        self.output_path.pack(side="left", fill="x", expand=True, padx=5)
        self.save_btn = ctk.CTkButton(self.output_frame, text="Save As", command=self.browse_output)
        self.save_btn.pack(side="right", padx=5)
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready")
        self.status_label.pack(pady=5)
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", padx=20, pady=10)
        self.encode_btn = ctk.CTkButton(self.button_frame, text="Convert Video to Text", command=lambda: self.start_conversion("encode"))
        self.encode_btn.pack(side="left", padx=5, expand=True)
        self.decode_btn = ctk.CTkButton(self.button_frame, text="Convert Text to Video", command=lambda: self.start_conversion("decode"))
        self.decode_btn.pack(side="right", padx=5, expand=True)
        from Converter import VideoConverter
        self.converter = VideoConverter()

    def browse_input(self):
        filetypes = [('Video Files', '*.mp4 *.avi *.mkv'), ('Text Files', '*.txt'), ('All Files', '*.*')]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.input_path.delete(0, 'end')
            self.input_path.insert(0, filename)
            if not self.output_path.get():
                base, ext = os.path.splitext(filename)
                if ext.lower() in ['.mp4', '.avi', '.mkv']:
                    self.output_path.delete(0, 'end')
                    self.output_path.insert(0, base + '.txt')
                elif ext.lower() == '.txt':
                    self.output_path.delete(0, 'end')
                    self.output_path.insert(0, base + '.mp4')

    def browse_output(self):
        if self.input_path.get().lower().endswith('.txt'):
            filetypes = [('Video Files', '*.mp4')]
            defaultextension = '.mp4'
        else:
            filetypes = [('Text Files', '*.txt')]
            defaultextension = '.txt'
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=defaultextension)
        if filename:
            self.output_path.delete(0, 'end')
            self.output_path.insert(0, filename)

    def update_progress(self, value):
        self.progress_bar.set(value / 100)
        self.status_label.configure(text=f"Converting... {value:.1f}%")
        self.window.update_idletasks()

    def start_conversion(self, mode):
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        if not input_path or not output_path:
            self.status_label.configure(text="Please select input and output files")
            return
        self.encode_btn.configure(state="disabled")
        self.decode_btn.configure(state="disabled")
        self.status_label.configure(text="Starting conversion...")
        self.progress_bar.set(0)
        
        def conversion_thread():
            try:
                if mode == "encode":
                    self.converter.video_to_text(input_path, output_path, self.update_progress)
                else:
                    self.converter.text_to_video(input_path, output_path, self.update_progress)
                self.window.after(0, lambda: self.status_label.configure(text="Conversion completed!"))
                self.window.after(0, lambda: self.progress_bar.set(1.0))
            except Exception as e:
                self.window.after(0, lambda: self.status_label.configure(text=f"Error: {str(e)}"))
            finally:
                self.window.after(0, lambda: self.encode_btn.configure(state="normal"))
                self.window.after(0, lambda: self.decode_btn.configure(state="normal"))
        thread = threading.Thread(target=conversion_thread)
        thread.start()

    def run(self):
        if os.path.exists("video.mp4"):
            self.input_path.insert(0, os.path.abspath("video.mp4"))
            self.output_path.insert(0, os.path.abspath("video.txt"))
        self.window.mainloop()

if __name__ == "__main__":
    app = VideoConverterGUI()
    app.run()
