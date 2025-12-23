import flet as ft
import logging
import pyperclip
import time
import threading
import platform
import asyncio
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Import pynput for keyboard control 
try:
    from pynput import keyboard
    HAS_PYNPUT = True
    logger.info("pynput loaded")
except ImportError:
    HAS_PYNPUT = False
    logger.error("pynput not installed")

class AcheiriaApp(ft.Column):
    """Main application UI - Black & Oxblood Theme - NEW Flet API"""
    
    def __init__(self, page: ft.Page, config_manager):
        super().__init__()
        self.page = page
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        
        # State
        self.is_folded = False
        self.is_typing = False
        self.is_paused = False
        self.stop_typing = False
        self.current_thread = None
        self.timer_thread = None
        self.typing_start_time = None
        self.estimated_duration = 0
        
        # Platform
        self.os_type = platform.system()
        logger.info(f"running on {self.os_type}")
        
        # Initialize keyboard
        if HAS_PYNPUT:
            try:
                self.keyboard = keyboard.Controller()
                logger.info("keyboard initialized")
            except Exception as e:
                logger.error(f"keyboard init failed: {e}")
                self.keyboard = None
        else:
            self.keyboard = None
        
        # Black & Oxblood Theme
        self.bg_color = "#000000"  # Black background
        self.card_bg = "#1A0000"   # Dark oxblood
        self.text_color = "#FFFFFF" # White text
        self.oxblood = "#800020"    # Classic oxblood
        self.oxblood_light = "#A0002A" # Light oxblood
        self.oxblood_dark = "#600018"  # Dark oxblood
        self.accent_color = "#FF225D" # Bright accent
        
        # Window state
        self.window_initialized = False
        
        # Build the UI immediately (new API)
        self._build_ui()
        
        # Initialize
        self.did_mount()
    
    def _build_ui(self):
        """Build UI with Black & Oxblood theme - NEW API"""
        
        # Warning banner if pynput missing
        self.warning_banner = ft.Container(
            content=ft.Row([
                ft.Text("warning", color=self.oxblood, size=14, weight=ft.FontWeight.BOLD),
                ft.Text("pynput not installed! run: pip install pynput",
                       color=self.text_color, size=12),
            ], spacing=10),
            bgcolor=self.card_bg,
            padding=10,
            border=ft.border.all(1, self.oxblood),
            border_radius=6,
            visible=not HAS_PYNPUT,
        )
        
        # Text input with max 3 lines and scrolling
        self.text_input = ft.TextField(
            hint_text="paste or type your stuff here...",
            hint_style=ft.TextStyle(color="#666666"),
            multiline=True,
            min_lines=1,
            max_lines=3,
            border_color=self.oxblood_dark,
            focused_border_color=self.oxblood,
            text_style=ft.TextStyle(color=self.text_color, font_family="Courier New", size=13),
            border_radius=6,
            content_padding=10,
            filled=True,
            fill_color=self.card_bg,
            on_change=self.on_text_changed,
            expand=True,
        )
        
        # Container for text input with scrolling
        self.text_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.text_input,
                    expand=True,
                )
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=10,
        )
        
        # Buttons - all lowercase text
        self.paste_btn = ft.ElevatedButton(
            "paste",
            on_click=self.paste_from_clipboard,
            style=ft.ButtonStyle(
                bgcolor={"": self.oxblood_dark, "hovered": self.oxblood},
                color=self.text_color,
                padding=8,
                overlay_color={"": self.oxblood_light},
            ),
            height=36,
        )
        
        self.type_btn = ft.ElevatedButton(
            "autotype",
            on_click=self.start_typing,
            style=ft.ButtonStyle(
                bgcolor={"": self.oxblood, "hovered": self.oxblood_light, "disabled": self.oxblood_dark},
                color={"": self.text_color, "disabled": "#666666"},
                padding=8,
                overlay_color={"": self.oxblood_light},
            ),
            height=36,
            disabled=True,
        )
        
        self.pause_btn = ft.ElevatedButton(
            "pause",
            on_click=self.toggle_pause,
            style=ft.ButtonStyle(
                bgcolor={"": self.oxblood_dark, "hovered": self.oxblood},
                color=self.text_color,
                padding=8,
                overlay_color={"": self.oxblood_light},
            ),
            height=36,
            visible=False,
        )
        
        self.stop_btn = ft.ElevatedButton(
            "stop",
            on_click=self.stop_typing_action,
            style=ft.ButtonStyle(
                bgcolor={"": self.oxblood_dark, "hovered": self.oxblood},
                color=self.text_color,
                padding=8,
                overlay_color={"": self.oxblood_light},
            ),
            height=36,
            visible=False,
        )
        
        countdown_val = self.config.get('countdown_duration', 4)
        speed_val = self.config.get('typing_speed', 60)
        
        # Clamp values to slider ranges
        countdown_val = max(3, min(10, countdown_val))
        speed_val = max(50, min(1000, speed_val))
        
        # Sliders with oxblood theme
        self.countdown_slider = ft.Slider(
            min=3, max=10, divisions=7,
            value=countdown_val,
            label="{value}s",
            on_change=self.update_countdown_setting,
            active_color=self.oxblood,
            inactive_color=self.oxblood_dark,
            thumb_color=self.oxblood_light,
            expand=True,
        )
        
        self.speed_slider = ft.Slider(
            min=50, max=1000, divisions=150,
            value=speed_val,
            label="{value}",
            on_change=self.update_speed_setting,
            active_color=self.oxblood,
            inactive_color=self.oxblood_dark,
            thumb_color=self.oxblood_light,
            expand=True,
        )
        
        self.always_on_top_switch = ft.Switch(
            value=self.config.get('always_on_top', True),
            active_color=self.oxblood,
            inactive_thumb_color=self.oxblood_dark,
            on_change=self.toggle_always_on_top,
        )
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            value=0,
            color=self.oxblood,
            bgcolor=self.oxblood_dark,
            height=3,
            visible=False,
        )
        
        # Status texts
        self.progress_text = ft.Text("ready", color=self.text_color, size=11)
        self.status_text = ft.Text("you lazy thing", color=self.oxblood_light, size=10, italic=True)
        
        # Timer displays
        self.elapsed_time_text = ft.Text("", color=self.oxblood, size=10, weight=ft.FontWeight.BOLD)
        self.estimated_time_text = ft.Text("", color=self.oxblood_light, size=10)
        
        # Header - Always visible
        self.header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Text("acheiria[by_phemi]", size=15, weight=ft.FontWeight.BOLD, color=self.accent_color),
                ], spacing=8),
                ft.Row([
                    ft.Text("always on top", size=10, color=self.text_color),
                    self.always_on_top_switch,
                ], spacing=6),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            bgcolor=self.card_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, self.oxblood)),
        )
        
        # Main content area
        self.main_content = ft.Container(
            content=ft.Column([
                # Warning banner
                ft.Container(
                    content=self.warning_banner,
                    padding=ft.padding.only(left=10, right=10, top=10),
                    visible=not HAS_PYNPUT,
                ),
                
                # Text area container with scrolling
                self.text_container,
                
                # Buttons
                ft.Container(
                    content=ft.Row([
                        self.paste_btn,
                        self.type_btn,
                        ft.Container(expand=True),
                        self.pause_btn,
                        self.stop_btn,
                    ], spacing=8),
                    padding=ft.padding.only(left=10, right=10, bottom=5),
                ),
                
                # Settings panel
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("delay", size=10, color=self.text_color, 
                                   weight=ft.FontWeight.BOLD, width=80),
                            self.countdown_slider,
                        ], spacing=10),
                        ft.Row([
                            ft.Text("speed", size=10, color=self.text_color,
                                   weight=ft.FontWeight.BOLD, width=80),
                            self.speed_slider,
                            ft.Text("wpm", size=10, color=self.oxblood_light),
                        ], spacing=10),
                    ], spacing=8),
                    padding=10,
                    bgcolor=self.card_bg,
                    border_radius=6,
                    margin=10,
                    border=ft.border.all(1, self.oxblood_dark),
                ),
                
                # Progress area
                ft.Container(
                    content=ft.Column([
                        self.progress_bar,
                        ft.Row([
                            self.progress_text,
                            ft.Container(expand=True),
                            self.status_text,
                        ]),
                    ], spacing=4),
                    padding=ft.padding.only(left=10, right=10, bottom=5),
                ),
                
                # Timer area
                ft.Container(
                    content=ft.Row([
                        self.elapsed_time_text,
                        ft.Container(expand=True),
                        self.estimated_time_text,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.only(left=10, right=10, bottom=10),
                    visible=True,
                ),
            ], spacing=0),
        )
        
        # Set the controls for the Column (self)
        self.controls = [
            ft.Container(
                content=ft.Column([
                    self.header,
                    self.main_content,
                ], spacing=0),
                bgcolor=self.bg_color,
                expand=True,
            )
        ]
        self.expand = True
    
    def did_mount(self):
        """Initialize window and check permissions - called automatically"""
        self._check_and_request_permissions()
        self._calculate_window_size(initial=True)
        self.window_initialized = True
    
    def will_unmount(self):
        """Clean up resources"""
        self.stop_typing = True
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=1)
    
    # Rest of the methods remain the same (on_text_changed, paste_from_clipboard, etc.)
    # Only change is remove the old build() method and use _build_ui() instead
    
    def on_text_changed(self, e):
        """Handle text changes without auto-positioning window"""
        has_text = bool(self.text_input.value and self.text_input.value.strip())
        self.type_btn.disabled = not has_text or not HAS_PYNPUT
        
        # Auto-adjust window height based on content without repositioning
        self._calculate_window_size()
        
        self.update()
    
    def paste_from_clipboard(self, e):
        """Paste from clipboard without auto-positioning window"""
        try:
            text = pyperclip.paste()
            if text:
                self.text_input.value = text
                self.type_btn.disabled = not HAS_PYNPUT
                self.show_status(f"pasted {len(text)} characters")
                logger.info(f"pasted {len(text)} chars")
                
                # Auto-adjust window height after pasting without repositioning
                self._calculate_window_size()
            else:
                self.show_status("clipboard is empty", True)
        except Exception as ex:
            logger.error(f"paste error: {ex}")
            self.show_status(f"paste failed: {str(ex)}", True)
        self.update()
    
    def start_typing(self, e):
        """Start typing process"""
        if not HAS_PYNPUT or not self.keyboard:
            self.show_status("please install pynput first", True)
            self._show_permission_dialog()
            return
        
        text = self.text_input.value
        if not text:
            return
        
        countdown = int(self.countdown_slider.value)
        speed = int(self.speed_slider.value)
        
        # Calculate estimated duration
        total_chars = len(text)
        chars_per_sec = (speed * 5) / 60
        self.estimated_duration = total_chars / chars_per_sec
        
        # Update UI
        self.type_btn.disabled = True
        self.paste_btn.disabled = True
        self.pause_btn.visible = True
        self.stop_btn.visible = True
        self.progress_bar.visible = True
        self.status_text.value = f"starting in {countdown}s..."
        self.estimated_time_text.value = f"est. duration: {self._format_time(self.estimated_duration)}"
        self.update()
        
        # Start typing thread
        self.stop_typing = False
        self.is_typing = True
        self.is_paused = False
        
        self.current_thread = threading.Thread(
            target=self._typing_thread,
            args=(text, countdown, speed),
            daemon=True
        )
        self.current_thread.start()
        logger.info(f"started typing {len(text)} chars at {speed} wpm")
    

    def _typing_thread(self, text: str, countdown: int, speed: int):
        """Background typing thread"""
        try:
            logger.info(f"typing on {self.os_type}")
            
            # Countdown
            for i in range(countdown, 0, -1):
                if self.stop_typing:
                    logger.info("cancelled during countdown")
                    return
                
                # FIXED: Use run_thread for regular functions, not run_task
                self.page.run_thread(lambda i=i: self._update_status(
                    f" {i}s to put your cursor where you want to type"
                ))
                time.sleep(1)
            
            # Start typing
            self.typing_start_time = time.time()
            self.page.run_thread(lambda: self._update_status("typing now..."))
            
            # Start timer thread
            self.timer_thread = threading.Thread(target=self._timer_update, daemon=True)
            self.timer_thread.start()
            
            time.sleep(0.2)
            
            # Calculate speed
            total = len(text)
            chars_per_sec = (speed * 5) / 60
            delay = 1.0 / chars_per_sec
            
            logger.info(f"typing {total} chars at {speed} wpm ({chars_per_sec:.2f} chars/sec)")
            
            # Type each character
            for i, char in enumerate(text):
                if self.stop_typing:
                    logger.info(f"stopped at {i}/{total}")
                    break
                
                # Handle pause
                pause_start = None
                while self.is_paused and not self.stop_typing:
                    if pause_start is None:
                        pause_start = time.time()
                    time.sleep(0.1)
                
                if pause_start:
                    # Adjust start time to account for pause
                    self.typing_start_time += (time.time() - pause_start)
                
                if self.stop_typing:
                    break
                
                # Type using pynput
                try:
                    self.keyboard.type(char)
                except:
                    try:
                        self.keyboard.press(char)
                        self.keyboard.release(char)
                    except:
                        logger.debug(f"skipped: {repr(char)}")
                
                # Update progress - FIXED: Use run_thread
                if i % 20 == 0 or i == total - 1:
                    progress = (i + 1) / total
                    self.page.run_thread(lambda p=progress, c=i+1, t=total, s=speed:
                                        self._update_progress(p, c, t, s))
                
                # Natural typing delay
                time.sleep(delay * (0.85 + 0.3 * ((i % 50) / 50)))
            
            # Complete - FIXED: Use run_thread
            final_time = time.time() - self.typing_start_time if self.typing_start_time else 0
            if not self.stop_typing:
                logger.info(f"completed {total} chars in {final_time:.1f}s")
                self.page.run_thread(lambda: self._complete(True, f"typed {total} characters in {self._format_time(final_time)}"))
            else:
                self.page.run_thread(lambda: self._complete(False, "stopped by user"))
        
        except Exception as e:
            logger.error(f"typing error: {e}", exc_info=True)
            # FIXED: Use run_thread for error handling
            self.page.run_thread(lambda: self._complete(False, f"error: {str(e)}"))


    def _timer_update(self):
        """Update timer display while typing"""
        while self.is_typing and not self.stop_typing:
            if self.typing_start_time and not self.is_paused:
                elapsed = time.time() - self.typing_start_time
                remaining = max(0, self.estimated_duration - elapsed)
                
                # FIXED: Use run_thread for timer updates
                self.page.run_thread(lambda e=elapsed, r=remaining: self._update_timer(e, r))
            
            time.sleep(0.5)
    
    def _update_timer(self, elapsed: float, remaining: float):
        """Update timer displays"""
        self.elapsed_time_text.value = f"elapsed: {self._format_time(elapsed)}"
        self.estimated_time_text.value = f"remaining: ~{self._format_time(remaining)}"
        self.update()
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds to readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        else:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
    
    def _update_status(self, text: str):
        """Update status (thread-safe)"""
        self.progress_text.value = text
        self.update()
    
    def _update_progress(self, progress: float, current: int, total: int, speed: int):
        """Update progress (thread-safe)"""
        self.progress_bar.value = progress
        self.progress_text.value = f"doing something... {current}/{total} chars"
        self.status_text.value = f"{int(progress * 100)}% complete • {speed} wpm"
        self.update()
    
    def _complete(self, success: bool, message: str):
        """Complete typing"""
        self.is_typing = False
        self.is_paused = False
        self.typing_start_time = None
        self.type_btn.disabled = not bool(self.text_input.value and self.text_input.value.strip())
        self.paste_btn.disabled = False
        self.pause_btn.visible = False
        self.stop_btn.visible = False
        self.progress_bar.visible = False
        self.progress_bar.value = 0
        self.progress_text.value = "ready"
        
        self.status_text.value = message
        self.status_text.color = self.oxblood if success else "#FF3B30"
        
        self.elapsed_time_text.value = ""
        self.estimated_time_text.value = ""
        
        logger.info(f"complete: {message}")
        self.update()
    
    def toggle_pause(self, e):
        """Toggle pause"""
        self.is_paused = not self.is_paused
        self.pause_btn.text = "resume" if self.is_paused else "pause"
        self.status_text.value = "paused - click to resume" if self.is_paused else "typing resumed..."
        logger.info(f"{'paused' if self.is_paused else 'resumed'}")
        self.update()
    
    def stop_typing_action(self, e):
        """Stop typing"""
        self.stop_typing = True
        logger.info("stop button pressed")
    
    def update_countdown_setting(self, e):
        """Update countdown"""
        value = int(self.countdown_slider.value)
        self.config['countdown_duration'] = value
        self.config_manager.save_config(self.config)
        self.show_status(f"delay set to {value}s")
    
    def update_speed_setting(self, e):
        """Update speed"""
        value = int(self.speed_slider.value)
        self.config['typing_speed'] = value
        self.config_manager.save_config(self.config)
        self.show_status(f"speed set to {value} wpm")
    
    def toggle_always_on_top(self, e):
        """Toggle always on top"""
        self.page.window.always_on_top = self.always_on_top_switch.value
        self.config['always_on_top'] = self.always_on_top_switch.value
        self.config_manager.save_config(self.config)
        status = "enabled" if self.always_on_top_switch.value else "disabled"
        self.show_status(f"always on top {status}")
        self.page.update()
    
    def show_status(self, message: str, is_error: bool = False):
        """Show status message"""
        self.status_text.value = message
        self.status_text.color = "#FF3B30" if is_error else self.oxblood_light
        self.update()
    
    def _calculate_window_size(self, initial=False):
        """Calculate optimal window size based on content without auto-positioning"""
        # Base height for fixed elements
        base_height = 318
        
        # Text area height
        line_height = 20
        text_lines = len(self.text_input.value.split('\n')) if self.text_input.value else 1
        visible_lines = min(3, text_lines)
        text_area_height = visible_lines * line_height + 25
        
        if text_lines > 3:
            text_area_height += 15
        
        total_height = base_height + text_area_height
        
        if initial:
            self.page.window.width = 600
            self.page.window.height = max(350, min(600, total_height))
        else:
            self.page.window.height = max(350, min(600, total_height))
        
        self.page.window.min_width = 500
        self.page.window.min_height = 350
        self.page.window.resizable = True
        
        if not self.window_initialized:
            self.window_initialized = True
        
        self.page.update()
    
    def _check_and_request_permissions(self):
        """Check and request accessibility permissions on macOS"""
        if self.os_type == "Darwin" and HAS_PYNPUT:
            try:
                test = keyboard.Controller()
                test.press(keyboard.Key.shift)
                test.release(keyboard.Key.shift)
                logger.info("accessibility permissions granted")
            except Exception as e:
                logger.warning(f"accessibility permissions needed: {e}")
                self.page.run_thread(self._show_permission_dialog)
    
    def _show_permission_dialog(self):
        """Show dialog requesting accessibility permissions"""
        if self.os_type == "Darwin":
            import subprocess
            
            def open_settings(e):
                subprocess.run(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
                dlg.open = False
                self.page.update()
            
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("accessibility permission required", weight=ft.FontWeight.BOLD, color=self.text_color),
                content=ft.Column([
                    ft.Text("acheiria needs accessibility permissions to type on your behalf.", size=13, color=self.text_color),
                    ft.Text("\n1. click 'open settings' below", size=12, color=self.text_color),
                    ft.Text("2. find and enable this app", size=12, color=self.text_color),
                    ft.Text("3. restart acheiria", size=12, color=self.text_color),
                ], tight=True, spacing=8),
                bgcolor=self.card_bg,
                actions=[
                    ft.TextButton("cancel", on_click=lambda e: setattr(dlg, 'open', False) or self.page.update()),
                    ft.ElevatedButton("open settings", on_click=open_settings, bgcolor=self.oxblood, color=self.text_color),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()