import tkinter as tk
from tkinter import Frame, Canvas, Button
import threading
from PIL import Image, ImageTk
from datetime import datetime

# Import necessary functions from chatbot.py
from chatbot import generate_response, speech_to_text, text_to_speech


class ModernChatbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Chat Interface")
        self.root.geometry("400x600")

        # Initialize microphone animation variables
        self.mic_active = False
        self.animation_frame = 0

        # Language selection (default to English)
        self.current_language = "en"

        # Theme settings
        self.dark_mode = False
        self.PRIMARY_COLOR = "#0084ff"  # Blue
        self.SECONDARY_COLOR = "#f0f2f5"  # Light grey
        self.BG_COLOR = "#f5f5f5"  # Very light grey
        self.DARK_BG_COLOR = "#121212"  # Dark background
        self.TEXT_COLOR = "#000000"  # Black text
        self.DARK_TEXT_COLOR = "#ffffff"  # White text

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Main frame for the entire UI
        self.main_frame = Frame(self.root, bg=self.BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header_frame = Frame(self.main_frame, bg=self.PRIMARY_COLOR, height=60)
        self.header_frame.pack(fill=tk.X, pady=(0, 1))
        self.header_frame.pack_propagate(False)

        # Profile icon and name
        self.profile_frame = Frame(self.header_frame, bg=self.PRIMARY_COLOR)
        self.profile_frame.pack(side=tk.LEFT, padx=5)

        # Bot Avatar
        try:
            bot_avatar = Image.open("bot_avatar.png").resize((40, 40))
            self.bot_avatar_photo = ImageTk.PhotoImage(bot_avatar)
            self.ai_icon = tk.Label(self.profile_frame, image=self.bot_avatar_photo, bg=self.PRIMARY_COLOR)
            self.ai_icon.image = self.bot_avatar_photo
            self.ai_icon.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error loading bot avatar: {e}")
            self.ai_icon = tk.Label(self.profile_frame, text="AI", font=("Verdana", 14, "bold"), bg=self.PRIMARY_COLOR, fg="#ffffff")
            self.ai_icon.pack(side=tk.LEFT, padx=5)

        self.profile_label = tk.Label(self.profile_frame, text="AI Assistant", font=("Verdana", 14, "bold"), bg=self.PRIMARY_COLOR, fg="#ffffff")
        self.profile_label.pack(side=tk.LEFT, padx=5)

        # Language selector and Dark Mode button
        self.lang_frame = Frame(self.header_frame, bg=self.PRIMARY_COLOR)
        self.lang_frame.pack(side=tk.RIGHT, padx=10)

        # Language selector button
        self.lang_button = Button(
            self.lang_frame,
            text="🌍 EN",
            font=("Verdana", 10),
            bg=self.PRIMARY_COLOR,
            fg="#ffffff",
            activebackground="#0066cc",
            activeforeground="#ffffff",
            relief="flat",
            command=self.toggle_language
        )
        self.lang_button.pack(side=tk.RIGHT, padx=5)

        # Dark mode toggle button
        self.dark_mode_button = Button(
            self.lang_frame,
            text="🌙",
            font=("Verdana", 10),
            bg=self.PRIMARY_COLOR,
            fg="#ffffff",
            activebackground="#0066cc",
            activeforeground="#ffffff",
            relief="flat",
            command=self.toggle_dark_mode
        )
        self.dark_mode_button.pack(side=tk.RIGHT, padx=5)

        # Chat display area
        self.chat_frame = Frame(self.main_frame, bg=self.BG_COLOR)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for scrolling
        self.messages_canvas = tk.Canvas(self.chat_frame, bg=self.BG_COLOR, highlightthickness=0)
        self.messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame inside the canvas for messages
        self.messages_frame = Frame(self.messages_canvas, bg=self.BG_COLOR)
        self.messages_frame_window = self.messages_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        # Scrollbar for messages
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.messages_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Configure canvas scrolling and fix the width
        self.messages_frame.bind("<Configure>", self.on_frame_configure)
        self.messages_canvas.bind("<Configure>", self.on_canvas_configure)

        # Enable mouse wheel scrolling
        self.messages_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Input area
        self.input_frame = Frame(self.main_frame, bg="#ffffff", height=60)
        self.input_frame.pack(fill=tk.X, pady=(1, 10))
        self.input_frame.pack_propagate(False)

        # Message input with rounded corners
        self.input_outer_frame = Frame(self.input_frame, bg=self.SECONDARY_COLOR, bd=1, relief="flat")
        self.input_outer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)

        self.input_box = tk.Entry(
            self.input_outer_frame,
            font=("Segoe UI", 11),
            bg=self.SECONDARY_COLOR,
            fg="#1a1a1a",
            border=0,
            insertbackground="#1a1a1a",
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Microphone button
        self.mic_button = tk.Button(
            self.input_frame,
            text="🎤",
            font=("Segoe UI", 16),
            bg="#ffffff",
            fg=self.PRIMARY_COLOR,
            relief="flat",
            bd=0,
            command=self.toggle_voice_input
        )
        self.mic_button.pack(side=tk.RIGHT, padx=(0, 5), pady=15)

        # Send button
        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            font=("Verdana", 10, "bold"),
            bg=self.PRIMARY_COLOR,
            fg="#ffffff",
            activebackground="#0066cc",
            activeforeground="#ffffff",
            relief="flat",
            command=self.process_query
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 10), pady=15)

        # Bind Enter key to send message
        self.input_box.bind("<Return>", lambda e: self.process_query())

        # Add a welcome message
        self.add_message("Hi, Howard! How can I assist you today?", "bot")

    def on_frame_configure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update the width of the canvas window
        self.messages_canvas.itemconfig(self.messages_frame_window, width=event.width)

    def on_mousewheel(self, event):
        # Scroll the canvas with the mousewheel
        self.messages_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_language(self):
        if self.current_language == "en":
            self.current_language = "es"  # Switch to Spanish
            self.lang_button.config(text="🌍 ES")
        else:
            self.current_language = "en"  # Switch to English
            self.lang_button.config(text="🌍 EN")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            # Switch to dark mode
            self.main_frame.config(bg=self.DARK_BG_COLOR)
            self.messages_canvas.config(bg=self.DARK_BG_COLOR)
            self.messages_frame.config(bg=self.DARK_BG_COLOR)
            self.input_outer_frame.config(bg=self.DARK_BG_COLOR)
            self.input_box.config(bg=self.DARK_BG_COLOR, fg=self.DARK_TEXT_COLOR)
            self.profile_frame.config(bg=self.PRIMARY_COLOR)
            self.ai_icon.config(bg=self.PRIMARY_COLOR)
            self.profile_label.config(bg=self.PRIMARY_COLOR, fg=self.DARK_TEXT_COLOR)
            self.lang_frame.config(bg=self.PRIMARY_COLOR)
            self.lang_button.config(bg=self.PRIMARY_COLOR, fg=self.DARK_TEXT_COLOR)
            self.dark_mode_button.config(bg=self.PRIMARY_COLOR, fg=self.DARK_TEXT_COLOR)
            self.send_button.config(bg=self.PRIMARY_COLOR, fg=self.DARK_TEXT_COLOR)
            self.mic_button.config(bg=self.DARK_BG_COLOR, fg=self.PRIMARY_COLOR)
        else:
            # Switch to light mode
            self.main_frame.config(bg=self.BG_COLOR)
            self.messages_canvas.config(bg=self.BG_COLOR)
            self.messages_frame.config(bg=self.BG_COLOR)
            self.input_outer_frame.config(bg=self.SECONDARY_COLOR)
            self.input_box.config(bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR)
            self.profile_frame.config(bg=self.PRIMARY_COLOR)
            self.ai_icon.config(bg=self.PRIMARY_COLOR)
            self.profile_label.config(bg=self.PRIMARY_COLOR, fg=self.TEXT_COLOR)
            self.lang_frame.config(bg=self.PRIMARY_COLOR)
            self.lang_button.config(bg=self.PRIMARY_COLOR, fg=self.TEXT_COLOR)
            self.dark_mode_button.config(bg=self.PRIMARY_COLOR, fg=self.TEXT_COLOR)
            self.send_button.config(bg=self.PRIMARY_COLOR, fg=self.TEXT_COLOR)
            self.mic_button.config(bg=self.BG_COLOR, fg=self.PRIMARY_COLOR)

    def toggle_voice_input(self, event=None):
        self.mic_active = not self.mic_active
        if self.mic_active:
            self.start_voice_input()
            self.mic_button.config(fg="#ff4444")  # Change to red when active
        else:
            self.stop_voice_input()
            self.mic_button.config(fg=self.PRIMARY_COLOR)  # Change back to blue when inactive

    def start_voice_input(self):
        self.animation_frame = 0
        self.animate_microphone()
        # Start voice input processing here
        threading.Thread(target=self.voice_input, daemon=True).start()

    def stop_voice_input(self):
        self.mic_active = False
        self.mic_button.config(fg=self.PRIMARY_COLOR)

    def animate_microphone(self):
        if self.mic_active:
            self.animation_frame += 1
            # Pulsing effect
            if self.animation_frame % 20 < 10:
                self.mic_button.config(fg="#ff4444")
            else:
                self.mic_button.config(fg="#ff0000")
            self.root.after(100, self.animate_microphone)

    def process_query(self):
        user_input = self.input_box.get().strip()
        if not user_input:
            return

        self.input_box.delete(0, tk.END)
        self.add_message(user_input, "user")

        # Simulate typing indicator
        self.typing_indicator = self.add_typing_indicator()

        # Process response in separate thread
        threading.Thread(target=self.fetch_response, args=(user_input,), daemon=True).start()

    def add_message(self, message, sender):
        msg_frame = self.create_message_bubble(message, sender)
        # Update canvas scroll region after adding message
        self.messages_frame.update_idletasks()
        self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
        # Scroll to the bottom
        self.messages_canvas.yview_moveto(1.0)
        return msg_frame

    def create_message_bubble(self, message, sender):
        msg_frame = Frame(self.messages_frame, bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR)
        msg_frame.pack(fill=tk.X, padx=10, pady=5)

        if sender == "user":
            bubble_frame = Frame(msg_frame, bg=self.PRIMARY_COLOR)
            bubble_frame.pack(side=tk.RIGHT)

            # User avatar
            try:
                user_avatar = Image.open("user_avatar.png").resize((32, 32))
                user_avatar_photo = ImageTk.PhotoImage(user_avatar)
                avatar_label = tk.Label(msg_frame, image=user_avatar_photo, bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR)
                avatar_label.image = user_avatar_photo
                avatar_label.pack(side=tk.RIGHT, padx=(0, 8))
            except Exception as e:
                print(f"Error loading user avatar: {e}")

            # Message text
            message_label = tk.Label(
                bubble_frame,
                text=message,
                wraplength=250,
                justify=tk.LEFT,
                bg=self.PRIMARY_COLOR,
                fg="#ffffff",
                font=("Verdana", 10),
                padx=12,
                pady=8
            )
            message_label.pack()

        else:
            container_frame = Frame(msg_frame, bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR)
            container_frame.pack(side=tk.LEFT, anchor="nw")

            # Bot avatar
            try:
                bot_avatar = Image.open("bot_avatar.png").resize((32, 32))
                bot_avatar_photo = ImageTk.PhotoImage(bot_avatar)
                avatar_label = tk.Label(container_frame, image=bot_avatar_photo, bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR)
                avatar_label.image = bot_avatar_photo
                avatar_label.pack(side=tk.LEFT, padx=(8, 0))
            except Exception as e:
                print(f"Error loading bot avatar: {e}")

            bubble_frame = Frame(container_frame, bg="#ffffff" if not self.dark_mode else "#424242")
            bubble_frame.pack(side=tk.RIGHT)

            # Message text
            message_label = tk.Label(
                bubble_frame,
                text=message,
                wraplength=250,
                justify=tk.LEFT,
                bg="#ffffff" if not self.dark_mode else "#424242",
                fg="#333333" if not self.dark_mode else "#ffffff",
                font=("Verdana", 10),
                padx=12,
                pady=8
            )
            message_label.pack()

        # Add timestamp
        timestamp = datetime.now().strftime("%I:%M %p")
        timestamp_label = tk.Label(
            msg_frame,
            text=timestamp,
            font=("Verdana", 8),
            fg="#a0a0a0" if not self.dark_mode else "#606060",
            bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR
        )
        timestamp_label.pack(side=tk.BOTTOM, pady=(0, 5))

        return msg_frame

    def add_typing_indicator(self):
        typing_frame = self.create_message_bubble("Typing...", "bot")
        # Update canvas scroll region after adding typing indicator
        self.messages_frame.update_idletasks()
        self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
        # Scroll to the bottom
        self.messages_canvas.yview_moveto(1.0)
        return typing_frame

    def remove_typing_indicator(self):
        if hasattr(self, 'typing_indicator') and self.typing_indicator:
            self.typing_indicator.destroy()
            self.typing_indicator = None

    def fetch_response(self, user_input):
        # Generate response using chatbot.py
        try:
            result = generate_response(user_input, self.current_language)
            response = result["response"]
            follow_up_needed = result.get("follow_up_needed", False)  # Default to False if not provided
        except Exception as e:
            response = f"Error: {str(e)}"
            follow_up_needed = False  # No follow-up needed in case of an error

        # Update UI
        def update_ui():
            self.remove_typing_indicator()
            self.add_message(response, "bot")
            # Add follow-up question only if needed
            if follow_up_needed:
                self.add_follow_up_question()

        # Schedule UI update on main thread
        self.root.after(0, update_ui)

    def add_follow_up_question(self):
        """Add a follow-up question with Yes/No buttons."""
        follow_up_frame = Frame(self.messages_frame, bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR)
        follow_up_frame.pack(fill=tk.X, padx=10, pady=5)

        # Follow-up question text
        follow_up_label = tk.Label(
            follow_up_frame,
            text="Is there anything else I can assist you with?",
            wraplength=250,
            justify=tk.LEFT,
            bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR,
            fg="#333333" if not self.dark_mode else "#ffffff",
            font=("Verdana", 10),
            padx=12,
            pady=8
        )
        follow_up_label.pack(side=tk.LEFT)

        # Yes button
        yes_button = Button(
            follow_up_frame,
            text="Yes",
            font=("Verdana", 9, "bold"),
            bg=self.PRIMARY_COLOR,
            fg="#000000",
            activebackground="#0066cc",
            activeforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            command=lambda: self.handle_yes(yes_button, no_button)
        )
        yes_button.pack(side=tk.LEFT, padx=5)

        # No button
        no_button = Button(
            follow_up_frame,
            text="No",
            font=("Verdana", 9, "bold"),
            bg=self.PRIMARY_COLOR,
            fg="#000000",
            activebackground="#0066cc",
            activeforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            command=lambda: self.handle_no(yes_button, no_button)
        )
        no_button.pack(side=tk.LEFT, padx=5)

        # Update canvas scroll region after adding follow-up question
        self.messages_frame.update_idletasks()
        self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
        self.messages_canvas.yview_moveto(1.0)

    def handle_yes(self, yes_button, no_button):
        """Handle the 'Yes' button click."""
        # Disable both buttons
        no_button.config(state=tk.DISABLED)
        yes_button.config(state=tk.DISABLED)

        # Change the appearance of the "Yes" button to indicate selection
        yes_button.config(bg="#4caf50", fg="#000000", relief="flat", text="✓ Yes", font=("Verdana", 9, "bold"))

        # Replace the "No" button with a static label
        no_button.pack_forget()  # Remove the "No" button
        no_label = tk.Label(
            no_button.master,
            text="[No]",
            font=("Verdana", 9, "bold"),
            bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR,
            fg="#a0a0a0",  # Grayed-out text
        )
        no_label.pack(side=tk.LEFT, padx=5)

        # Clear the input box for the next query
        self.input_box.delete(0, tk.END)

        # Add a message indicating readiness for the next query
        self.add_message("Sure! Please let me know how I can help.", "bot")

    def handle_no(self, yes_button, no_button):
        """Handle the 'No' button click."""
        # Disable both buttons
        yes_button.config(state=tk.DISABLED)
        no_button.config(state=tk.DISABLED)

        # Change the appearance of the "No" button to indicate selection
        no_button.config(bg="#f44336", fg="#000000", relief="flat", text="✓ No", font=("Verdana", 9, "bold"))

        # Replace the "Yes" button with a static label
        yes_button.pack_forget()  # Remove the "Yes" button
        yes_label = tk.Label(
            yes_button.master,
            text="[Yes]",
            font=("Verdana", 9, "bold"),
            bg=self.BG_COLOR if not self.dark_mode else self.DARK_BG_COLOR,
            fg="#a0a0a0",  # Grayed-out text
        )
        yes_label.pack(side=tk.LEFT, padx=5)

        # Add a closing message
        self.add_message("I hope I was able to assist your query. Thank you! Have a great day!", "bot")

    def voice_input(self):
        voice_text = speech_to_text()
        if voice_text and voice_text != "Sorry, I didn't understand that." and not voice_text.startswith("Error:"):
            self.input_box.insert(tk.END, voice_text)
            self.process_query()
        elif voice_text.startswith("Error:") or voice_text == "Sorry, I didn't understand that.":
            self.add_message("I couldn't understand that. Please try again.", "bot")
        self.stop_voice_input()


# For testing the UI
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernChatbotUI(root)
    root.mainloop()