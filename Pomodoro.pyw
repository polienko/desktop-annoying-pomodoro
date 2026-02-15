# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Dmitriy Polienko <polienko.dd@gmail.com>

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import time
import random
import textwrap
import json
import os
import winsound
import sys
import traceback
import threading
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum

# ============================================
# Default settings
# ============================================

class DebugMode:
    """Debug mode settings"""
    ENABLED = False
    
    # Time in seconds (for debug)
    WORK_TIME = 10
    BREAK_TIME = 10
    LONG_BREAK_TIME = 10

class Defaults:
    """Default values"""
    SETTINGS_FILE = "settings.json"
    
    # Time in minutes
    WORK_TIME = 25
    BREAK_TIME = 5
    LONG_BREAK_TIME = 15
    POMODOROS_FOR_LONG_BREAK = 4
    
    # Colors
    PROGRESS_COLOR = "#ff5353"
    BG_COLOR = "#242424"
    BREAK_BG_COLOR = "#696969"
    CONTROLS_BG_COLOR = "#242424"
    TEXT_COLOR = "white"
    ERROR_COLOR = "#ff4444"
    SUCCESS_COLOR = "#4CAF50"
    
    # Sizes
    BAR_HEIGHT = 3
    BAR_BORDER_WIDTH = 0
    CONTROLS_PADDING = 0
    WINDOW_Y_OFFSET = 0
    
    # Flags
    BAR_BORDERS = True
    AUTO_START = True
    
    # Other
    LANGUAGE = "RU"
    NOTIFICATION_SIZE = (1024, 768)
    CONTROLS_HEIGHT = 40
    CONTROLS_WIDTH = 450

class TimerState(Enum):
    """Timer states"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"

# ============================================
# Translations and texts
# ============================================

class Translations:
    UI_TEXTS = {
        "RU": {
            "initial_text": "Сделайте перерыв 5 минут",
            "long_break_text": "Сделайте длинный перерыв",
            "take_break": "Сделайте перерыв!",
            "settings_title": "Настройки Pomodoro",
            "time_settings": "Время",
            "work_time": "Рабочее время (1-120 мин):",
            "break_time": "Время перерыва (1-60 мин):",
            "long_break_time": "Длинный перерыв (1-60 мин):",
            "pomodoros_for_long_break": "Помидоров до длинного перерыва (2-10):",
            "appearance_settings": "Внешний вид",
            "progress_color": "Цвет прогресс бара:",
            "bg_color": "Цвет фона прогресс бара:",
            "break_bg_color": "Цвет фона экрана отдыха:",
            "bar_height": "Высота панели (1-50 px):",
            "border_width": "Ширина рамок (0-10 px):",
            "show_borders": "Показывать рамки",
            "auto_start": "Автозапуск таймера при старте приложения",
            "save_btn": "Сохранить",
            "cancel_btn": "Отмена",
            "choose_color": "Выбрать",
            "skip_break": "Срочно надо работать (отдохну больше потом)!",
            "confirm_instruction_text": "Чтобы работать дальше, ты должен ввести текст:",
            "confirm_skip_button_text": "Пропустить отдых",
            "time_to_work": "Пора за работу!",
            "lets_go": "Наконец-то!",
            "language_label": "Язык:"
        },
        "EN": {
            "initial_text": "Take a 5-minute break",
            "long_break_text": "Take a long break",
            "take_break": "Take a break!",
            "settings_title": "Pomodoro Settings",
            "time_settings": "Time",
            "work_time": "Work time (1-120 min):",
            "break_time": "Break time (1-60 min):",
            "long_break_time": "Long break (1-60 min):",
            "pomodoros_for_long_break": "Pomodoros until long break (2-10):",
            "appearance_settings": "Appearance",
            "progress_color": "Progress bar color:",
            "bg_color": "Progress bar background:",
            "break_bg_color": "Break screen background:",
            "bar_height": "Panel height (1-50 px):",
            "border_width": "Border width (0-10 px):",
            "show_borders": "Show borders",
            "auto_start": "Auto-start timer on app launch",
            "save_btn": "Save",
            "cancel_btn": "Cancel",
            "choose_color": "Choose",
            "skip_break": "Urgent work needed (I'll rest more later)!",
            "confirm_instruction_text": "To continue working, you must enter the text:",
            "confirm_skip_button_text": "Skip break",
            "time_to_work": "Time to work!",
            "lets_go": "Finally!",
            "language_label": "Language:"
        }
    }
    
    SKIP_PHRASES = {
        "RU": [
            "Я не устал, это мои глаза просто так слезятся!",
            "Выгорание? Не, не слышал!",
            "Я не прерываю поток. Я в нём тону, но красиво!",
            "Мой девиз: никаких пауз, только хардкор!",
            "Система хочет, чтобы я отдыхал. Я не поддамся!",
            "Отдохну в следующем квартале!",
            "Чай подождёт. А вот дедлайн - нет!",
            "Не сегодня, отдых, не сегодня!",
            "Выгорание - это просто миф, который я сегодня развею!",
            "Перерыв? Это когда я переключаюсь на другую задачу!",
            "Мой внутренний работорговец сказал сделать ещё один спринт!",
            "Это не трудоголизм, это марафон выживания!",
            "Я не избегаю отдыха. Я исследую пределы человеческих возможностей!",
            "Мой дух силён, и он велит мне игнорировать нужды тела!",
            "Мне платят за время, а не за самочувствие!",
            "Отдыхают мои конкуренты. А я - нет.",
        ],
        "EN": [
            "I'm not tired, my eyes are just watering on their own!",
            "Burnout? Never heard of it!",
            "I'm not interrupting the flow. I'm drowning in it, but stylishly!",
            "My motto: no pauses, only hardcore!",
            "The system wants me to rest. I won't give in!",
            "I'll rest next quarter!",
            "Tea can wait. But the deadline? Nope!",
            "Not today, rest, not today!",
            "Burnout is just a myth I'm going to debunk today!",
            "A break? That's when I switch to another task!",
            "My inner slave driver said to do one more sprint!",
            "This isn't workaholism, it's a survival marathon!",
            "I'm not avoiding rest. I'm exploring the limits of human potential!",
            "My spirit is strong, and it commands me to ignore my body's needs!",
            "I get paid for my time, not my well-being!",
            "My competitors are resting. But not me.",
        ]
    }
    
    @classmethod
    def get_text(cls, key: str, language: str) -> str:
        """Get text by key for specified language"""
        return cls.UI_TEXTS.get(language, cls.UI_TEXTS["EN"]).get(key, key)
    
    @classmethod
    def get_skip_phrases(cls, language: str) -> List[str]:
        """Get skip phrases for specified language"""
        return cls.SKIP_PHRASES.get(language, cls.SKIP_PHRASES["EN"])
    
    @classmethod
    def get_random_skip_phrase(cls, language: str) -> str:
        """Get random skip phrase"""
        phrases = cls.get_skip_phrases(language)
        return random.choice(phrases) if phrases else ""

# ============================================
# Data models
# ============================================

@dataclass
class TimerSettings:
    """Timer settings"""
    work_time: int = Defaults.WORK_TIME
    break_time: int = Defaults.BREAK_TIME
    long_break_time: int = Defaults.LONG_BREAK_TIME
    pomodoros_for_long_break: int = Defaults.POMODOROS_FOR_LONG_BREAK
    bar_height: int = Defaults.BAR_HEIGHT
    bar_border_width: int = Defaults.BAR_BORDER_WIDTH
    bar_borders: bool = Defaults.BAR_BORDERS
    auto_start: bool = Defaults.AUTO_START
    progress_color: str = Defaults.PROGRESS_COLOR
    bg_color: str = Defaults.BG_COLOR
    break_bg_color: str = Defaults.BREAK_BG_COLOR
    language: str = Defaults.LANGUAGE
    window_y_offset: int = Defaults.WINDOW_Y_OFFSET
    controls_padding: int = Defaults.CONTROLS_PADDING

@dataclass
class TimerStateData:
    """Current timer state"""
    current_pomodoro: int = 1
    total_pomodoros: int = 0
    is_long_break: bool = False
    extra_break_time: int = 0
    time_left: int = 0
    total_time: int = 0
    state: TimerState = TimerState.STOPPED
    start_time: Optional[float] = None
    is_resting: bool = False
    remaining_break_time: int = 0

# ============================================
# Model
# ============================================

class SettingsManager:
    """Settings manager"""
    
    @staticmethod
    def load_settings() -> TimerSettings:
        """Load settings from file"""
        if os.path.exists(Defaults.SETTINGS_FILE):
            try:
                with open(Defaults.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return TimerSettings(**data)
            except:
                return TimerSettings()
        return TimerSettings()
    
    @staticmethod
    def save_settings(settings: TimerSettings) -> bool:
        """Save settings to file"""
        try:
            with open(Defaults.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(settings), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Settings save error: {e}")
            return False

class TimerModel:
    """Pomodoro timer model"""
    
    def __init__(self, settings: TimerSettings):
        self.settings = settings
        self.state = TimerStateData()
        self.paused_elapsed = 0
        self._calculate_actual_height()
        self._update_timer_constants()
        
    def _calculate_actual_height(self):
        """Calculate actual panel height"""
        self.actual_bar_height = self.settings.bar_height
        if self.settings.bar_borders and self.settings.bar_border_width > 0:
            self.actual_bar_height = (self.settings.bar_height + 
                                     (self.settings.bar_border_width * 2))
    
    def _update_timer_constants(self):
        """Update timer constants based on mode"""
        if DebugMode.ENABLED:
            self.WORK_TIME = DebugMode.WORK_TIME
            self.BREAK_TIME = DebugMode.BREAK_TIME
            self.LONG_BREAK_TIME = DebugMode.LONG_BREAK_TIME
        else:
            self.WORK_TIME = self.settings.work_time * 60
            self.BREAK_TIME = self.settings.break_time * 60
            self.LONG_BREAK_TIME = self.settings.long_break_time * 60
        
        if not self.state.time_left:
            self.state.time_left = self.WORK_TIME
            self.state.total_time = self.WORK_TIME
    
    def get_break_time(self) -> int:
        """Get break time including extra time"""
        base_time = (self.LONG_BREAK_TIME if self.state.is_long_break 
                    else self.BREAK_TIME)
        return base_time + self.state.extra_break_time
    
    def start_timer(self):
        """Start timer"""
        if self.state.state != TimerState.RUNNING:
            self.state.state = TimerState.RUNNING
            if not self.state.start_time:
                self.state.start_time = time.time() - (
                    self.state.total_time - self.state.time_left)
            else:
                self.state.start_time = time.time() - self.paused_elapsed
    
    def pause_timer(self):
        """Pause timer"""
        if self.state.state == TimerState.RUNNING:
            self.state.state = TimerState.PAUSED
            if self.state.start_time is not None:
                self.paused_elapsed = time.time() - self.state.start_time
    
    def stop_timer(self):
        """Stop timer"""
        self.state.state = TimerState.STOPPED
        self.state.time_left = self.state.total_time
        self.state.start_time = None
        self.paused_elapsed = 0
    
    def update_timer(self):
        """Update timer state"""
        if (self.state.state == TimerState.RUNNING and 
            self.state.start_time is not None):
            elapsed = time.time() - self.state.start_time
            self.state.time_left = max(0, self.state.total_time - elapsed)
            
            if self.state.time_left <= 0:
                self.stop_timer()
                return True  # Signal to show notification
        return False
    
    def reset_for_work(self, after_skip: bool = False):
        """Reset for work"""
        if after_skip or not self.state.is_long_break:
            self.state.current_pomodoro += 1
            if self.state.current_pomodoro > self.settings.pomodoros_for_long_break:
                self.state.current_pomodoro = 1
            self.state.total_pomodoros += 1
        else:
            self.state.current_pomodoro = 1
            self.state.total_pomodoros += 1
        
        self.state.time_left = self.WORK_TIME
        self.state.total_time = self.WORK_TIME
        self.state.state = TimerState.STOPPED
        self.state.start_time = None
        self.state.is_long_break = False
        self.paused_elapsed = 0
    
    def format_time(self, seconds: int) -> str:
        """Format time as MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress(self) -> float:
        """Get progress from 0 to 1"""
        if self.state.total_time == 0:
            return 0
        return self.state.time_left / self.state.total_time
    
    def get_time_details_text(self, language: str) -> str:
        """Get text with break time details"""
        base_time = (self.LONG_BREAK_TIME if self.state.is_long_break 
                    else self.BREAK_TIME)
        base_min = base_time // 60
        base_sec = base_time % 60
        
        if self.state.extra_break_time > 0:
            extra_min = self.state.extra_break_time // 60
            extra_sec = self.state.extra_break_time % 60
            
            if language == "RU":
                return f"({base_min}:{base_sec:02d} за помидор + {extra_min}:{extra_sec:02d} за пропущенный отдых)"
            else:
                return f"({base_min}:{base_sec:02d} for pomodoro + {extra_min}:{extra_sec:02d} for missed break)"
        else:
            if language == "RU":
                return f"({base_min}:{base_sec:02d} за помидор)"
            else:
                return f"({base_min}:{base_sec:02d} for pomodoro)"

# ============================================
# View
# ============================================

class BaseView:
    """Base class for all views"""
    
    def __init__(self, controller):
        self.controller = controller
        self.model = controller.model
    
    def destroy(self):
        """Clean up resources"""
        pass

class MainWindowView(BaseView):
    """Main window with progress bar"""
    
    def __init__(self, controller, root):
        super().__init__(controller)
        self.root = root
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Window setup"""
        self.root.title("Pomodoro Timer")
        self.root.geometry(
            f"{self.root.winfo_screenwidth()}x{self.model.actual_bar_height}"
            f"+0+{self.model.settings.window_y_offset}"
        )
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.configure(bg=self.model.settings.bg_color)
        self.root.lift()
        self.root.focus_force()
    
    def create_widgets(self):
        """Create widgets"""
        self.main_frame = tk.Frame(
            self.root, 
            bg=self.model.settings.bg_color,
            height=self.model.actual_bar_height
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.create_progress_bar()
    
    def create_progress_bar(self):
        """Create custom progress bar"""
        if (self.model.settings.bar_borders and 
            self.model.settings.bar_border_width > 0):
            self.progress_canvas = tk.Canvas(
                self.main_frame,
                bg=self.model.settings.bg_color,
                highlightthickness=self.model.settings.bar_border_width,
                highlightbackground='black',
                highlightcolor='black',
                height=self.model.actual_bar_height,
                relief='flat'
            )
        else:
            self.progress_canvas = tk.Canvas(
                self.main_frame,
                bg=self.model.settings.bg_color,
                highlightthickness=0,
                height=self.model.actual_bar_height,
                relief='flat'
            )
        
        self.progress_canvas.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        y1 = (self.model.settings.bar_border_width 
              if self.model.settings.bar_borders and 
                 self.model.settings.bar_border_width > 0 
              else 0)
        y2 = self.model.actual_bar_height - y1
        
        self.progress_rect = self.progress_canvas.create_rectangle(
            0, y1, self.progress_canvas.winfo_reqwidth(), y2,
            fill=self.model.settings.progress_color,
            outline=self.model.settings.progress_color,
            width=0
        )
    
    def update_progress(self, progress_width: float):
        """Update progress bar"""
        if hasattr(self, 'progress_canvas') and self.progress_canvas:
            canvas_width = self.progress_canvas.winfo_width()
            if canvas_width <= 1:
                return
            
            y1 = (self.model.settings.bar_border_width 
                  if self.model.settings.bar_borders and 
                     self.model.settings.bar_border_width > 0 
                  else 0)
            y2 = self.model.actual_bar_height - y1
            
            self.progress_canvas.coords(
                self.progress_rect,
                0, y1, progress_width, y2
            )
    
    def update_position(self, y: int):
        """Update window position"""
        screen_width = self.root.winfo_screenwidth()
        window_height = self.model.actual_bar_height
        self.root.geometry(f"{screen_width}x{window_height}+0+{y}")

class ControlsView(BaseView):
    """Window with control elements"""
    
    def __init__(self, controller):
        super().__init__(controller)
        self.window = None
        self.widgets = {}
        self.hovered_button = None
        self.create_window()
    
    def create_window(self):
        """Create control window"""
        if self.window and self.window.winfo_exists():
            return
        
        main_window = self.controller.views['main'].root
        main_x = main_window.winfo_x()
        main_y = main_window.winfo_y()
        
        controls_height = Defaults.CONTROLS_HEIGHT
        controls_width = Defaults.CONTROLS_WIDTH
        
        controls_y = main_y - controls_height - self.model.settings.controls_padding
        if controls_y < 0:
            controls_y = main_y + self.model.actual_bar_height + self.model.settings.controls_padding
        
        controls_x = main_x + (main_window.winfo_screenwidth() - controls_width) // 2
        
        self.window = tk.Toplevel(main_window)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.configure(bg='#1a1a1a')
        
        main_frame = tk.Frame(
            self.window,
            bg='#1a1a1a',
            relief=tk.FLAT,
            bd=1,
            highlightbackground='#444444',
            highlightthickness=1
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        content_frame = tk.Frame(main_frame, bg='#1a1a1a', height=controls_height-2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=0)
        content_frame.pack_propagate(False)
        
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        inner_frame = tk.Frame(content_frame, bg='#1a1a1a')
        inner_frame.grid(row=0, column=0)
        
        self.window.geometry(f"{controls_width}x{controls_height}+{controls_x}+{controls_y}")
        self.create_widgets(inner_frame)
        self._bind_hover_events()
        self._bind_drag_events()
    
    def create_widgets(self, parent):
        """Create control widgets"""
        
        timer_frame = tk.Frame(parent, bg='#1a1a1a')
        timer_frame.pack(side=tk.LEFT)
        
        self.widgets['timer'] = tk.Label(
            timer_frame,
            text=self.model.format_time(self.model.state.time_left),
            font=('Segoe UI', 16, 'bold'), # TIMER
            fg='#ffffff',
            bg='#1a1a1a',
            width=5,
            height=1,
            anchor='center'
        )
        self.widgets['timer'].pack(side=tk.LEFT, padx=(0, 5), pady=0)
        
        self._create_vertical_separator(parent)
        
        controls_frame = tk.Frame(parent, bg='#1a1a1a')
        controls_frame.pack(side=tk.LEFT)
        
        # Start button
        self.widgets['start'] = self._create_button(
            controls_frame, "⏵", self.controller.start_resume_timer,
            active_bg='#4CAF50', state=tk.NORMAL, width=3
        )
        
        # Pause button
        self.widgets['pause'] = self._create_button(
            controls_frame, "     ⏸︎", self.controller.pause_timer,
            active_bg='#FFC107', state=tk.DISABLED, width=3
        )
        
        # Stop button
        self.widgets['stop'] = self._create_button(
            controls_frame, "◼", self.controller.stop_timer,
            active_bg='#f44336', state=tk.DISABLED, width=3
        )
        
        # Separator
        self._create_vertical_separator(parent)
        
        # Pomodoro counter frame
        pomo_frame = tk.Frame(parent, bg='#1a1a1a')
        pomo_frame.pack(side=tk.LEFT)
        
        pomo_label = tk.Label(
            pomo_frame,
            text="🍅",
            font=('Segoe UI', 12),
            fg='#ff9800',
            bg='#1a1a1a',
            anchor='center',
            width=2,
            height=1
        )
        pomo_label.pack(side=tk.LEFT, padx=(0, 5), pady=0)
        
        self.widgets['pomodoro'] = tk.Label(
            pomo_frame,
            text=f"{self.model.state.current_pomodoro}/{self.model.settings.pomodoros_for_long_break}",
            font=('Segoe UI', 16, 'bold'), # POMODORO 1/4
            fg='#ff9800',
            bg='#1a1a1a',
            anchor='center',
            height=1
        )
        self.widgets['pomodoro'].pack(side=tk.LEFT, pady=0)
        
        # Separator
        self._create_vertical_separator(parent)
        
        # Settings, language and close button frame
        right_frame = tk.Frame(parent, bg='#1a1a1a')
        right_frame.pack(side=tk.LEFT)
        
        # Settings button
        self.widgets['settings'] = self._create_button(
            right_frame, "      ⚙️ ", self.controller.show_settings,
            active_bg='#555555', width=3
        )
        
        # Language button with flags
        current_lang = self.model.settings.language
        lang_text = "ENG" if current_lang == "EN" else "РУС"
        self.widgets['language'] = self._create_button(
            right_frame, lang_text, self.controller.toggle_language,
            active_bg='#555555', width=4  # Флаги требуют больше ширины
        )
        
        # Close button
        self.widgets['close'] = self._create_button(
            right_frame, "✕", self.controller.on_closing,
            active_bg='#f44336', width=20
        )
        
        self.update_state()
    
    def _create_button(self, parent, text, command, 
                      active_bg='#3d3d3d', state=tk.NORMAL, width=2):
        """Create button with adjustable width"""
        
        # Create button with exact dimensions and perfect centering
        btn = tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 12, 'bold'),
            command=command,
            bg='#2d2d2d',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            width=width, 
            height=1, 
            cursor='hand2',
            activebackground=active_bg,
            activeforeground='#ffffff',
            state=state,
            highlightthickness=0,
            anchor='center',   
            justify='center', 
            padx=0,      
            pady=0      
        )
        btn.pack(side=tk.LEFT, padx=3, pady=0)
        
        # Store all states
        btn.normal_bg = '#2d2d2d'
        btn.normal_fg = '#ffffff'
        btn.hover_bg = active_bg
        btn.hover_fg = '#ffffff'
        btn.disabled_bg = '#333333'
        btn.disabled_fg = '#666666'
        btn.active_bg = active_bg
        
        # Store button info
        btn.button_text = text
        btn.is_hovered = False
        btn.button_width = width
        
        return btn
    
    def _create_vertical_separator(self, parent):
        """Create a vertical separator line with perfect centering"""
        separator_frame = tk.Frame(parent, bg='#1a1a1a', height=30)
        separator_frame.pack(side=tk.LEFT, padx=8, pady=0)
        separator_frame.pack_propagate(False)
        
        separator = tk.Frame(
            separator_frame,
            bg='#444444',
            width=1,
            height=24
        )
        separator.pack(expand=True)
        
        return separator
    
    def _bind_hover_events(self):
        """Bind hover events with persistent state tracking"""
        
        def on_enter(e):
            btn = e.widget
            if btn.cget('state') == tk.NORMAL:
                btn.is_hovered = True
                self.hovered_button = btn
                btn.config(
                    bg=btn.hover_bg,
                    fg=btn.hover_fg
                )
        
        def on_leave(e):
            btn = e.widget
            btn.is_hovered = False
            if self.hovered_button == btn:
                self.hovered_button = None
            
            if btn.cget('state') == tk.NORMAL:
                btn.config(
                    bg=btn.normal_bg,
                    fg=btn.normal_fg
                )
            else:
                btn.config(
                    bg=btn.disabled_bg,
                    fg=btn.disabled_fg
                )
        
        for btn_name in ['start', 'pause', 'stop', 'settings', 'language', 'close']:
            if btn_name in self.widgets:
                btn = self.widgets[btn_name]
                btn.bind('<Enter>', on_enter, add=True)
                btn.bind('<Leave>', on_leave, add=True)
                
                btn.bind('<Enter>', self.controller.cancel_hide_timer, add=True)
                btn.bind('<Leave>', self.controller.schedule_hide_controls, add=True)
    
    def _bind_drag_events(self):
        """Bind drag events to window and widgets"""
        def on_click(e):
            self.controller.on_controls_click(e)
        
        def on_drag(e):
            self.controller.on_controls_drag(e)
        
        self.window.bind('<Button-1>', on_click, add=True)
        self.window.bind('<B1-Motion>', on_drag, add=True)
        
        def bind_recursively(widget):
            widget.bind('<Button-1>', on_click, add=True)
            widget.bind('<B1-Motion>', on_drag, add=True)
            for child in widget.winfo_children():
                bind_recursively(child)
        
        bind_recursively(self.window)
    
    def update_state(self):
        """Update control elements state - preserves hover effects"""
        if not self.window or not self.window.winfo_exists():
            return
        
        # Update timer (this doesn't affect buttons)
        if 'timer' in self.widgets:
            time_text = self.model.format_time(self.model.state.time_left)
            self.widgets['timer'].config(text=time_text)
            
            if self.model.state.time_left < 60:
                self.widgets['timer'].config(fg='#ff6b6b')
            else:
                self.widgets['timer'].config(fg='#ffffff')
        
        # Update pomodoro counter
        if 'pomodoro' in self.widgets:
            pomodoro_text = f"{self.model.state.current_pomodoro}/{self.model.settings.pomodoros_for_long_break}"
            self.widgets['pomodoro'].config(text=pomodoro_text)
            
            if self.model.state.current_pomodoro == self.model.settings.pomodoros_for_long_break:
                self.widgets['pomodoro'].config(fg='#ffb74d')
            else:
                self.widgets['pomodoro'].config(fg='#ff9800')
        
        # Update button states - preserve hover effect
        is_running = self.model.state.state == TimerState.RUNNING
        is_paused = self.model.state.state == TimerState.PAUSED
        is_stopped = self.model.state.state == TimerState.STOPPED
        
        # Start button
        if 'start' in self.widgets:
            btn = self.widgets['start']
            new_state = tk.NORMAL if is_paused or is_stopped else tk.DISABLED
            
            # Only update if state changed
            if btn.cget('state') != new_state:
                btn.config(state=new_state)
                
                if new_state == tk.DISABLED:
                    btn.config(bg=btn.disabled_bg, fg=btn.disabled_fg)
                    btn.is_hovered = False
                else:
                    # Restore normal or hover state
                    if btn.is_hovered:
                        btn.config(bg=btn.hover_bg, fg=btn.hover_fg)
                    else:
                        btn.config(bg=btn.normal_bg, fg=btn.normal_fg)
        
        # Pause button
        if 'pause' in self.widgets:
            btn = self.widgets['pause']
            new_state = tk.NORMAL if is_running else tk.DISABLED
            
            if btn.cget('state') != new_state:
                btn.config(state=new_state)
                
                if new_state == tk.DISABLED:
                    btn.config(bg=btn.disabled_bg, fg=btn.disabled_fg)
                    btn.is_hovered = False
                else:
                    if btn.is_hovered:
                        btn.config(bg=btn.hover_bg, fg=btn.hover_fg)
                    else:
                        btn.config(bg=btn.normal_bg, fg=btn.normal_fg)
        
        # Stop button
        if 'stop' in self.widgets:
            btn = self.widgets['stop']
            new_state = tk.NORMAL if is_running or is_paused else tk.DISABLED
            
            if btn.cget('state') != new_state:
                btn.config(state=new_state)
                
                if new_state == tk.DISABLED:
                    btn.config(bg=btn.disabled_bg, fg=btn.disabled_fg)
                    btn.is_hovered = False
                else:
                    if btn.is_hovered:
                        btn.config(bg=btn.hover_bg, fg=btn.hover_fg)
                    else:
                        btn.config(bg=btn.normal_bg, fg=btn.normal_fg)
        
        # Settings button
        if 'settings' in self.widgets:
            btn = self.widgets['settings']
            if btn.cget('state') != tk.NORMAL:
                btn.config(state=tk.NORMAL)
                if btn.is_hovered:
                    btn.config(bg=btn.hover_bg, fg=btn.hover_fg)
                else:
                    btn.config(bg=btn.normal_bg, fg=btn.normal_fg)
        
        # Language button
        if 'language' in self.widgets:
            btn = self.widgets['language']
            current_lang = self.model.settings.language
            new_text = "ENG" if current_lang == "EN" else "РУС"
            
            # Update text if changed
            if btn.cget('text') != new_text:
                btn.config(text=new_text)
            
            if btn.cget('state') != tk.NORMAL:
                btn.config(state=tk.NORMAL)
                if btn.is_hovered:
                    btn.config(bg=btn.hover_bg, fg=btn.hover_fg)
                else:
                    btn.config(bg=btn.normal_bg, fg=btn.normal_fg)
        
        # Close button - always enabled
        if 'close' in self.widgets:
            btn = self.widgets['close']
            if btn.cget('state') != tk.NORMAL:
                btn.config(state=tk.NORMAL)
                if btn.is_hovered:
                    btn.config(bg=btn.hover_bg, fg=btn.hover_fg)
                else:
                    btn.config(bg=btn.normal_bg, fg=btn.normal_fg)
    
    def destroy(self):
        """Destroy window"""
        if self.window:
            self.window.destroy()
            self.window = None
            self.widgets = {}
            self.hovered_button = None


class NotificationView(BaseView):
    """Break notification window"""
    
    def __init__(self, controller):
        super().__init__(controller)
        self.window = None
        self.widgets = {}
        self.current_skip_phrase = ""
        self.is_break_over = False
        self.flash_id = None
        self.break_timer_id = None
        
    def show(self):
        """Show notification - always creates new window"""

        self.is_break_over = False
        
        if self.model.state.current_pomodoro >= self.model.settings.pomodoros_for_long_break:
            self.model.state.is_long_break = True
        else:
            self.model.state.is_long_break = False
        
        self.current_skip_phrase = Translations.get_random_skip_phrase(
            self.model.settings.language
        )
        
        self.window = tk.Toplevel(self.controller.views['main'].root)
        self.window.attributes('-fullscreen', True)
        self.window.overrideredirect(True)
        self.window.configure(bg=self.model.settings.break_bg_color)
        
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.controller.skip_with_alt_f4(None))
        
        self.create_content()
        
        self.start_break_timer()

        self.window.bind('<Alt-F4>', self.controller.block_alt_f4)
        self.window.protocol("WM_DELETE_WINDOW", 
                            lambda: self.controller.block_alt_f4(None))
    
    def create_content(self):
        """Create notification content"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        content_width, content_height = Defaults.NOTIFICATION_SIZE
        
        if DebugMode.ENABLED:
            # With black border
            border_frame = tk.Frame(
                self.window,
                bg='black',
                highlightthickness=1,
                highlightbackground='black',
                highlightcolor='black'
            )
            border_width = content_width + 2
            border_height = content_height + 2
            x = (screen_width - border_width) // 2
            y = (screen_height - border_height) // 2
            border_frame.place(x=x, y=y, width=border_width, height=border_height)
            
            content_frame = tk.Frame(
                border_frame,
                bg=self.model.settings.break_bg_color,
                width=content_width,
                height=content_height
            )
            content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        else:
            # Without border
            content_frame = tk.Frame(
                self.window,
                bg=self.model.settings.break_bg_color
            )
            x = (screen_width - content_width) // 2
            y = (screen_height - content_height) // 2
            content_frame.place(x=x, y=y, width=content_width, height=content_height)
        
        # Create widgets
        self.create_widgets(content_frame)
    
    def create_widgets(self, parent):
        """Create notification widgets"""
        # Title
        self.widgets['title'] = tk.Label(
            parent,
            text=Translations.get_text("take_break", self.model.settings.language),
            font=('Arial', 28, 'bold'),
            fg=Defaults.TEXT_COLOR,
            bg=self.model.settings.break_bg_color,
            pady=5
        )
        self.widgets['title'].pack(pady=(20, 5))
        
        # Time details
        time_details = self.model.get_time_details_text(self.model.settings.language)
        self.widgets['subtitle'] = tk.Label(
            parent,
            text=time_details,
            font=('Arial', 16),
            fg=Defaults.TEXT_COLOR,
            bg=self.model.settings.break_bg_color,
            pady=5
        )
        self.widgets['subtitle'].pack(pady=(0, 10))
        
        # Timer
        self.widgets['timer'] = tk.Label(
            parent,
            text=self.model.format_time(self.model.get_break_time()),
            font=('Arial', 32, 'bold'),
            fg=Defaults.TEXT_COLOR,
            bg=self.model.settings.break_bg_color,
            pady=10
        )
        self.widgets['timer'].pack(pady=20)
        
        # Skip button
        self.widgets['skip'] = tk.Label(
            parent,
            text=Translations.get_text("skip_break", self.model.settings.language),
            font=('Arial', 16),
            fg=Defaults.TEXT_COLOR,
            bg=self.model.settings.break_bg_color,
            cursor='hand2',
            pady=10
        )
        self.widgets['skip'].pack(pady=10)
        self.widgets['skip'].bind('<Button-1>', 
                                lambda e: self.controller.show_skip_confirmation())
        self.widgets['skip'].bind('<Enter>', 
                                lambda e: self.widgets['skip'].config(fg='#ffffcc'))
        self.widgets['skip'].bind('<Leave>', 
                                lambda e: self.widgets['skip'].config(fg=Defaults.TEXT_COLOR))
        
        # Confirmation frame (hidden)
        self.widgets['confirm_frame'] = tk.Frame(
            parent, 
            bg=self.model.settings.break_bg_color
        )
        
        self.create_confirmation_widgets(self.widgets['confirm_frame'])
        
        # Frame for "Finally!" button (hidden)
        self.widgets['button_frame'] = tk.Frame(
            parent,
            bg=self.model.settings.break_bg_color
        )
        
        self.widgets['ok_button'] = tk.Button(
            self.widgets['button_frame'],
            text="",
            font=('Arial', 20, 'bold'),
            command=self.controller.close_notification,
            bg=Defaults.TEXT_COLOR,
            fg=Defaults.SUCCESS_COLOR,
            relief=tk.FLAT,
            bd=0,
            padx=80,
            pady=15,
            cursor='hand2',
            activebackground='#45a049',
            activeforeground=Defaults.TEXT_COLOR
        )
    
    def create_confirmation_widgets(self, parent):
        """Create confirmation widgets"""
        # Instruction
        self.widgets['confirm_instruction'] = tk.Label(
            parent,
            text=Translations.get_text("confirm_instruction_text", 
                                      self.model.settings.language),
            font=('Arial', 16, 'bold'),
            fg=Defaults.TEXT_COLOR,
            bg=self.model.settings.break_bg_color
        )
        self.widgets['confirm_instruction'].pack(pady=5)
        
        # Phrase to enter
        self.widgets['confirm_phrase'] = tk.Label(
            parent,
            text=f'"{self.current_skip_phrase}"',
            font=('Arial', 14),
            fg='#ffffcc',
            bg=self.model.settings.break_bg_color,
            pady=10,
            wraplength=800,
            justify='center'
        )
        self.widgets['confirm_phrase'].pack(pady=5)
        
        # Entry field
        self.widgets['confirm_entry'] = tk.Entry(
            parent,
            font=('Arial', 14),
            bg=self.model.settings.break_bg_color,
            fg=Defaults.TEXT_COLOR,
            insertbackground=Defaults.TEXT_COLOR,
            relief=tk.SOLID,
            bd=2,
            width=50,
            justify='center'
        )
        self.widgets['confirm_entry'].pack(pady=15, ipady=8)
        self.widgets['confirm_entry'].bind('<KeyRelease>', 
                                         self.controller.check_skip_confirmation)
        self.widgets['confirm_entry'].bind('<Key>', 
                                         self.controller.check_skip_confirmation)
        
        # Confirmation button
        self.widgets['confirm_button'] = tk.Button(
            parent,
            text=Translations.get_text("confirm_skip_button_text", 
                                      self.model.settings.language),
            font=('Arial', 16, 'bold'),
            command=self.controller.skip_break,
            bg='#555555',
            fg=Defaults.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0,
            padx=40,
            pady=10,
            cursor='hand2',
            activebackground='#666666',
            activeforeground=Defaults.TEXT_COLOR,
            state=tk.DISABLED
        )
        self.widgets['confirm_button'].pack(pady=15)
    
    def show_confirmation(self):
        """Show skip confirmation"""
        if 'skip' in self.widgets:
            self.widgets['skip'].pack_forget()
        
        if 'confirm_frame' in self.widgets:
            self.widgets['confirm_frame'].pack(pady=20)
    
    def update_confirmation(self, entered_text: str, is_correct: bool, is_complete: bool):
        """Update confirmation state"""
        if 'confirm_entry' not in self.widgets:
            return
        
        entry = self.widgets['confirm_entry']
        button = self.widgets['confirm_button']
        
        if is_correct and not is_complete:
            entry.config(fg=Defaults.TEXT_COLOR)
        elif not is_correct:
            entry.config(fg='#A60000')
        elif is_complete:
            entry.config(fg=Defaults.TEXT_COLOR)
            button.config(
                state=tk.NORMAL,
                bg=Defaults.SUCCESS_COLOR,
                activebackground='#45a049'
            )
        else:
            button.config(
                state=tk.DISABLED,
                bg='#555555',
                activebackground='#666666'
            )
    
    def start_break_timer(self):
        """Start break timer"""
        if not self.window or not self.window.winfo_exists():
            return
        
        def update_timer():
            if self.model.state.remaining_break_time > 0:
                self.widgets['timer'].config(
                    text=self.model.format_time(self.model.state.remaining_break_time)
                )
                self.model.state.remaining_break_time -= 1
                self.break_timer_id = self.window.after(1000, update_timer)
            else:
                self.on_break_end()
        
        update_timer()
    
    def on_break_end(self):
        """Handle break end"""
        self.is_break_over = True
        
        # Hide unnecessary elements
        for key in ['timer', 'skip']:
            if key in self.widgets:
                self.widgets[key].pack_forget()
        
        if 'confirm_frame' in self.widgets and self.widgets['confirm_frame'].winfo_ismapped():
            self.widgets['confirm_frame'].pack_forget()
        
        # Update title
        self.widgets['title'].config(
            text=Translations.get_text("time_to_work", self.model.settings.language),
            pady=20
        )
        
        # Hide subtitle
        self.widgets['subtitle'].pack_forget()
        
        # Show button
        self.widgets['ok_button'].config(
            text=Translations.get_text("lets_go", self.model.settings.language)
        )
        self.widgets['ok_button'].pack()
        self.widgets['button_frame'].pack(pady=20)
        
        # Play sound
        self.controller.play_notification_sound()
        
        # Start animation
        self.start_button_flashing()
    
    def start_button_flashing(self):
        """Start button flashing"""
        colors = [
            (Defaults.SUCCESS_COLOR, Defaults.TEXT_COLOR),
            (Defaults.TEXT_COLOR, Defaults.SUCCESS_COLOR),
            (Defaults.SUCCESS_COLOR, Defaults.TEXT_COLOR),
            (Defaults.TEXT_COLOR, Defaults.SUCCESS_COLOR),
            (Defaults.SUCCESS_COLOR, Defaults.TEXT_COLOR),
        ]
        
        def change_color(bg_color, fg_color):
            if self.window and self.window.winfo_exists():
                self.widgets['ok_button'].config(bg=bg_color, fg=fg_color)
        
        for i, (bg, fg) in enumerate(colors):
            delay = i * 300
            if self.window:
                self.window.after(delay, lambda bg=bg, fg=fg: change_color(bg, fg))
        
        final_delay = len(colors) * 300
        if self.window:
            self.window.after(final_delay, lambda: self.widgets['ok_button'].config(
                bg=Defaults.SUCCESS_COLOR,
                fg=Defaults.TEXT_COLOR
            ))
    
    def destroy(self):
        """Destroy window and completely clean up"""
        if self.window:
            if self.break_timer_id:
                try:
                    self.window.after_cancel(self.break_timer_id)
                except:
                    pass
            
            if self.flash_id:
                try:
                    self.window.after_cancel(self.flash_id)
                except:
                    pass
            
            try:
                for child in self.window.winfo_children():
                    child.destroy()
            except:
                pass
            
            try:
                self.window.destroy()
            except:
                pass
            
            self.window = None
            self.widgets = {}
            self.current_skip_phrase = ""
            self.is_break_over = False
            self.break_timer_id = None
            self.flash_id = None

class SettingsView(BaseView):
    """Settings window"""
    
    def __init__(self, controller):
        super().__init__(controller)
        self.window = None
        self.widgets = {}
        self.vars = {}
        self.labels = {} 
        self.frames = {} 
    
    def show(self):
        """Show settings window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.create_window()
        self.create_widgets()
        self.center_window()
    
    def create_window(self):
        """Create settings window"""
        self.window = tk.Toplevel(self.controller.views['main'].root)
        self.window.title("Pomodoro Settings")
        self.window.geometry("420x600")
        self.window.resizable(False, False)
        self.window.configure(bg=Defaults.CONTROLS_BG_COLOR)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)

        self.window.bind('<Alt-F4>', self.controller.block_alt_f4)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def create_widgets(self):
        """Create settings widgets"""
        
        self.create_title_bar()

        main_frame = tk.Frame(self.window, bg=Defaults.CONTROLS_BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_language_selector(main_frame)

        self.create_time_settings(main_frame)

        self.create_appearance_settings(main_frame)

        self.create_buttons(main_frame)
    
    def create_title_bar(self):
        """Create window title bar"""
        title_frame = tk.Frame(self.window, bg='#333333', height=40)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        title_frame.pack_propagate(False)
        
        title_frame.bind('<Button-1>', self.controller.on_settings_click)
        title_frame.bind('<B1-Motion>', self.controller.on_settings_drag)
        
        # Title
        title_label = tk.Label(
            title_frame,
            text=Translations.get_text("settings_title", self.model.settings.language),
            font=('Arial', 14, 'bold'),
            fg=Defaults.TEXT_COLOR,
            bg='#333333'
        )
        title_label.pack(side=tk.LEFT, padx=15)
        title_label.bind('<Button-1>', self.controller.on_settings_click)
        title_label.bind('<B1-Motion>', self.controller.on_settings_drag)
        
        # Close button
        close_btn = tk.Button(
            title_frame,
            text="×",
            font=('Arial', 20, 'bold'),
            command=self.close,
            bg='#333333',
            fg=Defaults.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=0,
            cursor='hand2',
            activebackground=Defaults.ERROR_COLOR,
            activeforeground=Defaults.TEXT_COLOR
        )
        close_btn.pack(side=tk.RIGHT)
    
    def create_language_selector(self, parent):
        """Create language selector"""
        language_frame = tk.Frame(parent, bg=Defaults.CONTROLS_BG_COLOR)
        language_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        buttons_frame = tk.Frame(language_frame, bg=Defaults.CONTROLS_BG_COLOR)
        buttons_frame.pack(side=tk.RIGHT)
        
        selected_color = self.model.settings.progress_color
        unselected_color = '#444444'
        
        # Language buttons
        self.widgets['ru_btn'] = tk.Button(
            buttons_frame,
            text="РУС",
            font=('Arial', 12, 'bold'),
            command=lambda: self.controller.set_language("RU"),
            bg=selected_color if self.model.settings.language == "RU" else unselected_color,
            fg=Defaults.TEXT_COLOR,
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        self.widgets['ru_btn'].pack(side=tk.LEFT)
        
        self.widgets['en_btn'] = tk.Button(
            buttons_frame,
            text="ENG",
            font=('Arial', 12, 'bold'),
            command=lambda: self.controller.set_language("EN"),
            bg=selected_color if self.model.settings.language == "EN" else unselected_color,
            fg=Defaults.TEXT_COLOR,
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        self.widgets['en_btn'].pack(side=tk.LEFT, padx=(5, 0))
    
    def create_time_settings(self, parent):
        """Create time settings"""
        time_frame = tk.LabelFrame(
            parent,
            text=Translations.get_text("time_settings", self.model.settings.language),
            font=('Arial', 12, 'bold'),
            fg=Defaults.TEXT_COLOR,
            bg=Defaults.CONTROLS_BG_COLOR,
            relief=tk.GROOVE,
            bd=2
        )
        time_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        self.frames['time_frame'] = time_frame  # сохраняем frame
        
        self.vars['work'] = tk.StringVar(value=str(self.model.settings.work_time))
        self.vars['break'] = tk.StringVar(value=str(self.model.settings.break_time))
        self.vars['long_break'] = tk.StringVar(value=str(self.model.settings.long_break_time))
        self.vars['pomodoros'] = tk.StringVar(value=str(self.model.settings.pomodoros_for_long_break))
        
        # Input fields for time settings
        settings = [
            ("work_time", self.vars['work'], 1, 120),
            ("break_time", self.vars['break'], 1, 60),
            ("long_break_time", self.vars['long_break'], 1, 60),
            ("pomodoros_for_long_break", self.vars['pomodoros'], 2, 10),
        ]
        
        for key, var, from_, to in settings:
            self.create_spinbox_row(time_frame, key, var, from_, to)
          
          
        # Checkbox "auto-start timer"
        self.vars['auto_start'] = tk.BooleanVar(value=self.model.settings.auto_start)
        
        checkbox_frame = tk.Frame(time_frame, bg=Defaults.CONTROLS_BG_COLOR)
        checkbox_frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.widgets['auto_start_check'] = tk.Checkbutton(
            checkbox_frame,
            text=Translations.get_text("auto_start", self.model.settings.language),
            variable=self.vars['auto_start'],
            font=('Arial', 10),
            fg=Defaults.TEXT_COLOR,
            bg=Defaults.CONTROLS_BG_COLOR,
            selectcolor='black'
        )
        self.widgets['auto_start_check'].pack(anchor=tk.W)    
    
    def create_appearance_settings(self, parent):
        """Create appearance settings"""
        appearance_frame = tk.LabelFrame(
            parent,
            text=Translations.get_text("appearance_settings", self.model.settings.language),
            font=('Arial', 12, 'bold'),
            fg=Defaults.TEXT_COLOR,
            bg=Defaults.CONTROLS_BG_COLOR,
            relief=tk.GROOVE,
            bd=2
        )
        appearance_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        self.frames['appearance_frame'] = appearance_frame
        
        self.vars['height'] = tk.StringVar(value=str(self.model.settings.bar_height))
        self.vars['border'] = tk.StringVar(value=str(self.model.settings.bar_border_width))
        
        colors = [
            ("progress_color", self.model.settings.progress_color),
            ("bg_color", self.model.settings.bg_color),
            ("break_bg_color", self.model.settings.break_bg_color),
        ]
        
        for key, color in colors:
            self.create_color_row(appearance_frame, key, color)
        
        # Sizes
        self.create_spinbox_row(appearance_frame, "bar_height", self.vars['height'], 1, 50)
        self.create_spinbox_row(appearance_frame, "border_width", self.vars['border'], 0, 10)
        
    
    def create_spinbox_row(self, parent, text_key, var, from_, to):
        """Create row with Spinbox"""
        frame = tk.Frame(parent, bg=Defaults.CONTROLS_BG_COLOR)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        label = tk.Label(
            frame,
            text=Translations.get_text(text_key, self.model.settings.language),
            font=('Arial', 10),
            fg=Defaults.TEXT_COLOR,
            bg=Defaults.CONTROLS_BG_COLOR
        )
        label.pack(side=tk.LEFT)
        
        self.labels[f"{text_key}_label"] = label
        
        spinbox = tk.Spinbox(
            frame,
            from_=from_,
            to=to,
            textvariable=var,
            width=10,
            font=('Arial', 10)
        )
        spinbox.pack(side=tk.RIGHT)
        
        self.widgets[f"{text_key}_spinbox"] = spinbox
    
    def create_color_row(self, parent, text_key, color):
        """Create color selection row"""
        frame = tk.Frame(parent, bg=Defaults.CONTROLS_BG_COLOR)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        label = tk.Label(
            frame,
            text=Translations.get_text(text_key, self.model.settings.language),
            font=('Arial', 10),
            fg=Defaults.TEXT_COLOR,
            bg=Defaults.CONTROLS_BG_COLOR
        )
        label.pack(side=tk.LEFT)
        
        self.labels[f"{text_key}_label"] = label
        
        # Color preview
        preview = tk.Label(
            frame,
            text="   ",
            font=('Arial', 10),
            bg=color,
            relief=tk.SUNKEN,
            bd=2
        )
        preview.pack(side=tk.RIGHT, padx=(5, 0))
        self.widgets[f"{text_key}_preview"] = preview
        
        # Color choose button
        btn = tk.Button(
            frame,
            text=Translations.get_text("choose_color", self.model.settings.language),
            font=('Arial', 10),
            command=lambda k=text_key, p=preview: self.controller.choose_color(k, p),
            bg='#444444',
            fg=Defaults.TEXT_COLOR
        )
        btn.pack(side=tk.RIGHT, padx=(10, 0))
        self.widgets[f"{text_key}_btn"] = btn
    
    def create_buttons(self, parent):
        """Create save/cancel buttons"""
        buttons_frame = tk.Frame(parent, bg=Defaults.CONTROLS_BG_COLOR)
        buttons_frame.pack(fill=tk.X, pady=(10,5))
        
        self.widgets['save_btn'] = tk.Button(
            buttons_frame,
            text=Translations.get_text("save_btn", self.model.settings.language),
            font=('Arial', 12, 'bold'),
            command=self.controller.save_settings,
            bg=Defaults.SUCCESS_COLOR,
            fg=Defaults.TEXT_COLOR,
            padx=20,
            pady=5
        )
        self.widgets['save_btn'].pack(side=tk.LEFT, padx=(0, 10))
        
        self.widgets['cancel_btn'] = tk.Button(
            buttons_frame,
            text=Translations.get_text("cancel_btn", self.model.settings.language),
            font=('Arial', 12),
            command=self.close,
            bg=Defaults.ERROR_COLOR,
            fg=Defaults.TEXT_COLOR,
            padx=20,
            pady=5
        )
        self.widgets['cancel_btn'].pack(side=tk.RIGHT)
    
    def update_color_preview(self, key, color):
        """Update color preview"""
        if f"{key}_preview" in self.widgets:
            self.widgets[f"{key}_preview"].config(bg=color)
    
    def update_language_buttons(self):
        """Update language buttons"""
        selected_color = self.model.settings.progress_color
        unselected_color = '#444444'
        
        if 'ru_btn' in self.widgets and 'en_btn' in self.widgets:
            if self.model.settings.language == "RU":
                self.widgets['ru_btn'].config(bg=selected_color)
                self.widgets['en_btn'].config(bg=unselected_color)
            else:
                self.widgets['ru_btn'].config(bg=unselected_color)
                self.widgets['en_btn'].config(bg=selected_color)
    
    def update_texts(self):
        """Update all texts after language change"""
        if not self.window or not self.window.winfo_exists():
            return
        
        # Update title
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_height() == 40:
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(
                            text=Translations.get_text("settings_title", 
                                                      self.model.settings.language)
                        )
                        break
        
        # Update LabelFrame texts
        if 'time_frame' in self.frames:
            self.frames['time_frame'].config(
                text=Translations.get_text("time_settings", self.model.settings.language)
            )
        
        if 'appearance_frame' in self.frames:
            self.frames['appearance_frame'].config(
                text=Translations.get_text("appearance_settings", self.model.settings.language)
            )
        
        # Update all labels from labels dictionary
        label_keys = [
            ("work_time_label", "work_time"),
            ("break_time_label", "break_time"),
            ("long_break_time_label", "long_break_time"),
            ("pomodoros_for_long_break_label", "pomodoros_for_long_break"),
            ("progress_color_label", "progress_color"),
            ("bg_color_label", "bg_color"),
            ("break_bg_color_label", "break_bg_color"),
            ("bar_height_label", "bar_height"),
            ("border_width_label", "border_width"),
        ]
        
        for label_key, text_key in label_keys:
            if label_key in self.labels:
                self.labels[label_key].config(
                    text=Translations.get_text(text_key, self.model.settings.language)
                )
        
        # Update buttons
        for key in ['progress_color_btn', 'bg_color_btn', 'break_bg_color_btn']:
            if key in self.widgets:
                self.widgets[key].config(
                    text=Translations.get_text("choose_color", self.model.settings.language)
                )
        
        if 'auto_start_check' in self.widgets:
            self.widgets['auto_start_check'].config(
                text=Translations.get_text("auto_start", self.model.settings.language)
            )
        
        if 'save_btn' in self.widgets:
            self.widgets['save_btn'].config(
                text=Translations.get_text("save_btn", self.model.settings.language)
            )
        
        if 'cancel_btn' in self.widgets:
            self.widgets['cancel_btn'].config(
                text=Translations.get_text("cancel_btn", self.model.settings.language))
    
    def center_window(self):
        """Center window"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def close(self):
        """Close window"""
        if self.window:
            self.window.destroy()
            self.window = None
            self.widgets = {}
            self.vars = {}
    
    def destroy(self):
        """Destroy window"""
        self.close()

# ============================================
# Controller
# ============================================

class PomodoroController:
    """Main application controller"""
    
    def __init__(self, root):
        self.root = root
        self.model = None
        self.views = {}
        self.hover_timer = None
        self.show_controls_scheduled = False
        self.hide_controls_scheduled = False
        self.controls_check_id = None
        self.skip_confirmed = False
        
        self.initialize()
    
    def initialize(self):
        """Initialize application"""

        settings = SettingsManager.load_settings()
        self.model = TimerModel(settings)

        self.views['main'] = MainWindowView(self, self.root)
        self.views['notification'] = NotificationView(self)
        self.views['settings'] = SettingsView(self)

        self.views['controls'] = ControlsView(self)
        
        if self.views['controls'].window:
            self.views['controls'].window.withdraw()
        
        self.disable_alt_f4_globally()

        self.bind_events()

        self.update_timer()
        self.keep_window_on_top()
        self.start_controls_check()

        if self.model.settings.auto_start:
            self.start_resume_timer()

    def disable_alt_f4_globally(self):
        """Disable Alt+F4 completely in the entire application"""

        self.root.bind_all('<Alt-F4>', self.block_alt_f4)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.disable_alt_f4_in_all_windows()

    def block_alt_f4(self, event=None):
        """Completely block Alt+F4 - do nothing"""
        print("Alt+F4 blocked")
        return "break"

    def disable_alt_f4_in_all_windows(self):
        """Disable Alt+F4 in all existing windows"""
        self.root.bind('<Alt-F4>', self.block_alt_f4)

        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.bind('<Alt-F4>', self.block_alt_f4)
                child.protocol("WM_DELETE_WINDOW", 
                            lambda w=child: self.on_window_close(w))        
    
    def bind_events(self):
        """Bind events"""
        # Main window events
        main_frame = self.views['main'].main_frame
        main_frame.bind('<Button-1>', self.on_main_click)
        main_frame.bind('<B1-Motion>', self.on_main_drag)
        main_frame.bind('<Enter>', self.schedule_show_controls)
        main_frame.bind('<Leave>', self.schedule_hide_controls)
        
        # Progress bar events
        canvas = self.views['main'].progress_canvas
        canvas.bind('<Button-1>', self.on_main_click)
        canvas.bind('<B1-Motion>', self.on_main_drag)
        canvas.bind('<Enter>', self.schedule_show_controls)
        canvas.bind('<Leave>', self.schedule_hide_controls)
        
        # Handle closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # ========== Control management ==========

    def cancel_hide_timer(self, event=None):
        """Cancel hide timer when mouse enters controls"""
        if self.hide_controls_scheduled:
            self.root.after_cancel(self.hide_controls_scheduled)
            self.hide_controls_scheduled = None

    def show_controls_delayed(self):
        """Show controls after delay"""
        self.show_controls_scheduled = None
        
        if 'controls' in self.views and self.views['controls'].window:
            if not self.views['controls'].window.winfo_viewable():
                self.update_controls_position()
                self.views['controls'].window.deiconify()
                self.views['controls'].window.lift()
                self.views['controls'].window.attributes('-topmost', True)
    
    def schedule_show_controls(self, event=None):
        """Schedule showing controls with 300ms delay"""
        if self.hide_controls_scheduled:
            self.root.after_cancel(self.hide_controls_scheduled)
            self.hide_controls_scheduled = None
        
        # Show control panel after 300 ms on mouse hover
        if not self.show_controls_scheduled:
            self.show_controls_scheduled = self.root.after(300, self.show_controls_delayed)   
    
    def update_controls_position(self):
        """Update control panel position"""
        if 'controls' not in self.views or not self.views['controls'].window:
            return
        
        main_window = self.views['main'].root
        main_x = main_window.winfo_x()
        main_y = main_window.winfo_y()
        
        # Positioning (logic from ControlsView.create_window)
        controls_height = Defaults.CONTROLS_HEIGHT
        controls_y = main_y - controls_height - self.model.settings.controls_padding
        
        if controls_y < 0:
            controls_y = main_y + self.model.actual_bar_height + self.model.settings.controls_padding
        
        controls_width = Defaults.CONTROLS_WIDTH
        controls_x = main_x + (main_window.winfo_screenwidth() - controls_width) // 2
        
        # Set new position
        self.views['controls'].window.geometry(f"+{controls_x}+{controls_y}")
    
    def hide_controls_delayed(self):
        """Hide controls after delay"""
        self.hide_controls_scheduled = None
        
        if 'controls' in self.views and self.views['controls'].window:
            x, y = self.views['controls'].window.winfo_pointerxy()
            
            window_x = self.views['controls'].window.winfo_x()
            window_y = self.views['controls'].window.winfo_y()
            window_width = self.views['controls'].window.winfo_width()
            window_height = self.views['controls'].window.winfo_height()
            
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            
            over_controls = (window_x <= x <= window_x + window_width and 
                            window_y <= y <= window_y + window_height)
            over_main_panel = (main_x <= x <= main_x + main_width and 
                              main_y <= y <= main_y + main_height)
            
            if not over_controls and not over_main_panel:
                self.views['controls'].window.withdraw()    
    
    def schedule_hide_controls(self, event=None):
        """Schedule hiding controls with 200ms delay"""
        if self.show_controls_scheduled:
            self.root.after_cancel(self.show_controls_scheduled)
            self.show_controls_scheduled = None
        
        # Hide control panel after 200 ms on mouse left
        if 'controls' in self.views and self.views['controls'].window:
            if not self.hide_controls_scheduled:
                self.hide_controls_scheduled = self.root.after(200, self.hide_controls_delayed)
    
    def hide_controls(self):
        """Immediately hide controls"""
        if 'controls' in self.views and self.views['controls'].window:
            self.views['controls'].window.withdraw()
    
    def start_controls_check(self):
        """Start checking control visibility"""
        self.check_controls_visibility()
        self.controls_check_id = self.root.after(1000, self.start_controls_check)
    
    def check_controls_visibility(self):
        """Check control visibility"""
        if 'controls' not in self.views or not self.views['controls'].window:
            return
        
        # If panel is visible, check if it needs to be hidden
        if self.views['controls'].window.winfo_viewable():
            self.schedule_hide_controls()
    
    # ========== Timer methods ==========
    
    def update_timer(self):
        """Update timer"""
        if self.model.update_timer():  # Returns True if time is up
            self.show_notification()
        
        self.update_views()
        self.root.after(100, self.update_timer)
    
    def keep_window_on_top(self):
        """Keep window on top"""
        if not self.model.state.is_resting:
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.wm_attributes('-topmost', True)
        else:
            self.root.attributes('-topmost', False)
            self.root.wm_attributes('-topmost', False)
        
        self.root.after(2000, self.keep_window_on_top)
    
    def update_views(self):
        """Update all views"""
        # Update progress bar
        if 'main' in self.views:
            canvas_width = self.views['main'].progress_canvas.winfo_width()
            if canvas_width > 1:  # Check that canvas is initialized
                progress_width = canvas_width * self.model.get_progress()
                self.views['main'].update_progress(progress_width)
        
        # Update controls if they are visible
        if 'controls' in self.views and self.views['controls'].window and self.views['controls'].window.winfo_viewable():
            self.views['controls'].update_state()
    
    # ========== Event handlers ==========
    
    def on_main_click(self, event):
        """Main window click handler"""
        self._main_offset = event.y_root - self.root.winfo_y()
    
    def on_main_drag(self, event):
        """Main window drag handler"""
        y = event.y_root - self._main_offset
        screen_height = self.root.winfo_screenheight()
        window_height = self.model.actual_bar_height
        
        if y < 0:
            y = 0
        elif y > screen_height - window_height:
            y = screen_height - window_height
        
        self.views['main'].update_position(y)
        self.model.settings.window_y_offset = y
        # Update control panel position if visible
        if 'controls' in self.views and self.views['controls'].window and self.views['controls'].window.winfo_viewable():
            self.update_controls_position()
    
    def on_controls_click(self, event):
        """Control window click handler"""
        if 'controls' in self.views:
            controls_view = self.views['controls']
            self._controls_offset = (
                event.x_root - controls_view.window.winfo_x(),
                event.y_root - controls_view.window.winfo_y()
            )
    
    def on_controls_drag(self, event):
        """Control window drag handler"""
        if 'controls' not in self.views:
            return
        
        controls_view = self.views['controls']
        if not controls_view.window or not controls_view.window.winfo_exists():
            return
        
        new_x = event.x_root - self._controls_offset[0]
        new_y = event.y_root - self._controls_offset[1]
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = controls_view.window.winfo_width()
        window_height = controls_view.window.winfo_height()
        
        if new_x < 0:
            new_x = 0
        elif new_x > screen_width - window_width:
            new_x = screen_width - window_width
        
        if new_y < 0:
            new_y = 0
        elif new_y > screen_height - window_height:
            new_y = screen_height - window_height
        
        controls_view.window.geometry(f"+{new_x}+{new_y}")
    
    def on_settings_click(self, event):
        """Settings window click handler"""
        if 'settings' in self.views:
            settings_view = self.views['settings']
            if settings_view.window:
                self._settings_offset = (
                    event.x_root - settings_view.window.winfo_x(),
                    event.y_root - settings_view.window.winfo_y()
                )
    
    def on_settings_drag(self, event):
        """Settings window drag handler"""
        if 'settings' not in self.views:
            return
        
        settings_view = self.views['settings']
        if not settings_view.window or not settings_view.window.winfo_exists():
            return
        
        new_x = event.x_root - self._settings_offset[0]
        new_y = event.y_root - self._settings_offset[1]
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = settings_view.window.winfo_width()
        window_height = settings_view.window.winfo_height()
        
        if new_x < 0:
            new_x = 0
        elif new_x > screen_width - window_width:
            new_x = screen_width - window_width
        
        if new_y < 0:
            new_y = 0
        elif new_y > screen_height - window_height:
            new_y = screen_height - window_height
        
        settings_view.window.geometry(f"+{new_x}+{new_y}")
    
    # ========== Timer control ==========
    
    def start_resume_timer(self):
        """Start or resume timer"""
        self.model.start_timer()
        if 'controls' in self.views and self.views['controls'].window and self.views['controls'].window.winfo_viewable():
            self.views['controls'].update_state()
    
    def pause_timer(self):
        """Pause timer"""
        self.model.pause_timer()
        if 'controls' in self.views and self.views['controls'].window and self.views['controls'].window.winfo_viewable():
            self.views['controls'].update_state()
    
    def stop_timer(self):
        """Stop timer"""
        self.model.stop_timer()
        if 'controls' in self.views and self.views['controls'].window and self.views['controls'].window.winfo_viewable():
            self.views['controls'].update_state()
    
    # ========== Notifications ==========
    
    def show_notification(self):
        """Show notification"""
        if 'notification' in self.views:
            self.model.state.is_resting = True
            self.model.state.remaining_break_time = self.model.get_break_time()
            self.views['notification'].show()
            # Start checking notification window position
            self.keep_notification_on_top()
            self.views['notification'].window.protocol("WM_DELETE_WINDOW", self.skip_with_alt_f4)
    
    def keep_notification_on_top(self):
        """Keep notification window on top of all windows"""
        if 'notification' in self.views and self.views['notification'].window:
            if self.views['notification'].window.winfo_exists():
                if self.model.state.is_resting:
                    # During break - notification window on top of all windows
                    self.views['notification'].window.lift()
                    self.views['notification'].window.attributes('-topmost', True)
                    self.views['notification'].window.wm_attributes('-topmost', True)
                else:
                    # During work - remove topmost from notification window
                    self.views['notification'].window.attributes('-topmost', False)
                    self.views['notification'].window.wm_attributes('-topmost', False)
                
                # Continue checking every second
                self.root.after(1000, self.keep_notification_on_top)
    
    def show_skip_confirmation(self):
        """Show skip confirmation"""
        self.skip_confirmed = True
        if 'notification' in self.views:
            self.views['notification'].show_confirmation()
    
    def check_skip_confirmation(self, event=None):
        """Check skip confirmation"""
        if 'notification' not in self.views:
            return
        
        notification_view = self.views['notification']
        entered_text = notification_view.widgets['confirm_entry'].get().strip()
        
        if not entered_text:
            notification_view.update_confirmation("", True, False)
            return
        
        # Check character by character
        correct_phrase = notification_view.current_skip_phrase
        is_correct = True
        is_complete = False
        
        for i in range(len(entered_text)):
            if i >= len(correct_phrase) or entered_text[i] != correct_phrase[i]:
                is_correct = False
                break
        
        if entered_text == correct_phrase:
            is_complete = True
        
        notification_view.update_confirmation(entered_text, is_correct, is_complete)
    
    def skip_break(self):
        """Skip break"""
        if 'notification' in self.views:
            notification_view = self.views['notification']
            if notification_view.window and notification_view.window.winfo_exists():
                # Save remaining break time
                self.model.state.extra_break_time = self.model.state.remaining_break_time
                
                # Close notification
                notification_view.destroy()
                self.model.state.is_resting = False
                
                # Restart timer
                self.model.reset_for_work(after_skip=True)
                self.start_resume_timer()
                self.skip_confirmed = False
    
    def skip_with_alt_f4(self, event=None):
        """Skip break with Alt+F4 - recreate window with same timer"""
        if 'notification' not in self.views:
            return "break"
        
        notification_view = self.views['notification']
        
        if notification_view.is_break_over:
            self.close_notification()
            return "break"
        
        remaining_time = max(0, self.model.state.remaining_break_time + 1)
        
        self.replace_notification_view(remaining_time)
        
        return "break"

    def replace_notification_view(self, remaining_time):
        """Replace the notification view with a new one"""
        
        self.model.state.remaining_break_time = remaining_time

        if 'notification' in self.views:
            if self.views['notification'].window:
                try:
                    if self.views['notification'].break_timer_id:
                        self.views['notification'].window.after_cancel(
                            self.views['notification'].break_timer_id
                        )
                    if self.views['notification'].flash_id:
                        self.views['notification'].window.after_cancel(
                            self.views['notification'].flash_id
                        )
                    
                    self.views['notification'].window.destroy()
                except:
                    pass
            
            del self.views['notification']
        
        self.views['notification'] = NotificationView(self)
        
        self.model.state.is_resting = True

        self.views['notification'].show()


    def recreate_break_window(self, remaining_time):
        """Recreate break window with the same remaining time"""

        if 'notification' in self.views:
            self.views['notification'].destroy()
            del self.views['notification']
        
        self.views['notification'] = NotificationView(self)
        
        self.model.state.is_resting = True
        self.model.state.remaining_break_time = remaining_time
        
        self.views['notification'].show()

        self.views['notification'].start_break_timer()
    
    def restart_work_timer_skip(self):
        """Restart work timer after skipping break"""

        self.model.state.current_pomodoro += 1
        if self.model.state.current_pomodoro > self.model.settings.pomodoros_for_long_break:
            self.model.state.current_pomodoro = 1
        self.model.state.total_pomodoros += 1
        
        self.model.state.time_left = self.model.WORK_TIME
        self.model.state.total_time = self.model.WORK_TIME
        
        self.model.state.state = TimerState.STOPPED
        self.model.state.start_time = None
        self.model.state.is_long_break = False
        
        self.update_views()
        
        self.start_resume_timer()
    
    def close_notification(self):
        """Close notification"""
        if 'notification' in self.views:
            notification_view = self.views['notification']
            if notification_view.is_break_over:
                self.model.reset_for_work()
                self.start_resume_timer()
            
            notification_view.destroy()
            self.model.state.is_resting = False
            self.skip_confirmed = False
            self.model.state.is_resting = False
    
    # ========== Settings ==========
    
    def show_settings(self):
        """Show settings"""
        if 'settings' in self.views:
            self.views['settings'].show()
    
    def set_language(self, language: str):
        """Set language"""
        self.model.settings.language = language
        if 'settings' in self.views:
            self.views['settings'].update_language_buttons()
            self.views['settings'].update_texts()
    
    def toggle_language(self):
        """Toggle language - FIXED: doesn't restart timer"""
        new_lang = "EN" if self.model.settings.language == "RU" else "RU"
        self.model.settings.language = new_lang
        
        # Update texts without restarting
        self.update_language_ui()
        
        # Save settings
        SettingsManager.save_settings(self.model.settings)
    
    def update_language_ui(self):
        """Update interface when language changes"""
        # Update language in model
        current_language = self.model.settings.language
        
        # Update texts in control panel
        if 'controls' in self.views and self.views['controls'].window:
            # Update language button text
            if 'language' in self.views['controls'].widgets:
                self.views['controls'].widgets['language'].config(
                    text="ENG" if current_language == "EN" else "РУС"
                )
        
        # Update texts in settings window if open
        if 'settings' in self.views and self.views['settings'].window and self.views['settings'].window.winfo_exists():
            self.views['settings'].update_texts()
            self.views['settings'].update_language_buttons()
        
        # Update texts in notification if open
        if 'notification' in self.views and self.views['notification'].window and self.views['notification'].window.winfo_exists():
            self.update_notification_texts()
    
    def update_notification_texts(self):
        """Update texts in notification window"""
        if 'notification' not in self.views:
            return
        
        notification_view = self.views['notification']
        language = self.model.settings.language
        
        # Update title
        if 'title' in notification_view.widgets:
            if notification_view.is_break_over:
                notification_view.widgets['title'].config(
                    text=Translations.get_text("time_to_work", language)
                )
            else:
                notification_view.widgets['title'].config(
                    text=Translations.get_text("take_break", language)
                )
        
        # Update time details
        if 'subtitle' in notification_view.widgets and not notification_view.is_break_over:
            time_details = self.model.get_time_details_text(language)
            notification_view.widgets['subtitle'].config(text=time_details)
        
        # Update skip button
        if 'skip' in notification_view.widgets:
            notification_view.widgets['skip'].config(
                text=Translations.get_text("skip_break", language)
            )
        
        # Update confirmation texts
        if 'confirm_instruction' in notification_view.widgets:
            notification_view.widgets['confirm_instruction'].config(
                text=Translations.get_text("confirm_instruction_text", language)
            )
        
        if 'confirm_button' in notification_view.widgets:
            notification_view.widgets['confirm_button'].config(
                text=Translations.get_text("confirm_skip_button_text", language)
            )
        
        # Update "Finally!" button
        if 'ok_button' in notification_view.widgets:
            notification_view.widgets['ok_button'].config(
                text=Translations.get_text("lets_go", language)
            )
    
    def choose_color(self, setting_key: str, preview_label):
        """Choose color"""
        current_color = getattr(self.model.settings, setting_key)
        color = colorchooser.askcolor(
            title=f"Выберите цвет {setting_key}" if self.model.settings.language == "RU" 
                  else f"Choose {setting_key} color",
            initialcolor=current_color
        )[1]
        
        if color:
            setattr(self.model.settings, setting_key, color)
            preview_label.config(bg=color)
            
            # Update main window if needed
            if setting_key == "bg_color":
                self.root.configure(bg=color)
                self.views['main'].main_frame.configure(bg=color)
                self.views['main'].progress_canvas.configure(bg=color)
            elif setting_key == "progress_color":
                # Update progress bar
                if hasattr(self.views['main'], 'progress_rect'):
                    self.views['main'].progress_canvas.itemconfig(
                        self.views['main'].progress_rect,
                        fill=color,
                        outline=color
                    )
            elif setting_key == "break_bg_color":
                # Update background color for notifications
                pass
    
    def save_settings(self):
        """Save settings"""
        if 'settings' not in self.views:
            return
        
        settings_view = self.views['settings']
        
        try:
            work_time = int(settings_view.vars['work'].get())
            break_time = int(settings_view.vars['break'].get())
            long_break_time = int(settings_view.vars['long_break'].get())
            pomodoros = int(settings_view.vars['pomodoros'].get())
            bar_height = int(settings_view.vars['height'].get())
            border_width = int(settings_view.vars['border'].get())

            errors = []
            
            # Work time: 1-120
            if work_time < 1 or work_time > 120:
                field_name = "Рабочее время" if self.model.settings.language == "RU" else "Work time"
                errors.append(f"{field_name}: {work_time} (должно быть 1-120)" if self.model.settings.language == "RU" 
                             else f"{field_name}: {work_time} (must be 1-120)")
            
            # Break time: 1-60
            if break_time < 1 or break_time > 60:
                field_name = "Время перерыва" if self.model.settings.language == "RU" else "Break time"
                errors.append(f"{field_name}: {break_time} (должно быть 1-60)" if self.model.settings.language == "RU" 
                             else f"{field_name}: {break_time} (must be 1-60)")
            
            # Long break time: 1-60
            if long_break_time < 1 or long_break_time > 60:
                field_name = "Длинный перерыв" if self.model.settings.language == "RU" else "Long break time"
                errors.append(f"{field_name}: {long_break_time} (должно быть 1-60)" if self.model.settings.language == "RU" 
                             else f"{field_name}: {long_break_time} (must be 1-60)")
            
            # Pomodoros count: 2-10
            if pomodoros < 2 or pomodoros > 10:
                field_name = "Помидоров до длинного перерыва" if self.model.settings.language == "RU" else "Pomodoros until long break"
                errors.append(f"{field_name}: {pomodoros} (должно быть 2-10)" if self.model.settings.language == "RU" 
                             else f"{field_name}: {pomodoros} (must be 2-10)")
            
            # Bar height: 1-50
            if bar_height < 1 or bar_height > 50:
                field_name = "Высота панели" if self.model.settings.language == "RU" else "Panel height"
                errors.append(f"{field_name}: {bar_height} (должно быть 1-50)" if self.model.settings.language == "RU" 
                             else f"{field_name}: {bar_height} (must be 1-50)")
            
            # Border width: 0-10
            if border_width < 0 or border_width > 10:
                field_name = "Ширина рамок" if self.model.settings.language == "RU" else "Border width"
                errors.append(f"{field_name}: {border_width} (должно быть 0-10)" if self.model.settings.language == "RU" 
                             else f"{field_name}: {border_width} (must be 0-10)")
            
            if errors:
                if self.model.settings.language == "RU":
                    error_title = "Ошибка в настройках"
                    error_message = "Обнаружены некорректные значения:\n\n" + "\n".join(errors)
                    error_message += "\n\nПожалуйста, исправьте указанные поля."
                else:
                    error_title = "Settings Error"
                    error_message = "Invalid values found:\n\n" + "\n".join(errors)
                    error_message += "\n\nPlease correct the highlighted fields."
                
                messagebox.showerror(error_title, error_message)
                return
            
            current_time_left = self.model.state.time_left
            current_total_time = self.model.state.total_time
            current_progress = current_time_left / current_total_time if current_total_time > 0 else 0
            
            self.model.settings.work_time = work_time
            self.model.settings.break_time = break_time
            self.model.settings.long_break_time = long_break_time
            self.model.settings.pomodoros_for_long_break = pomodoros
            self.model.settings.bar_height = bar_height
            self.model.settings.bar_border_width = border_width
            self.model.settings.auto_start = settings_view.vars['auto_start'].get()
            
            self.model._update_timer_constants()
            self.model._calculate_actual_height()
            
            if not self.model.state.is_resting and not self.model.state.is_long_break:
                new_work_time = self.model.WORK_TIME
                if current_total_time > 0:
                    self.model.state.time_left = new_work_time * current_progress
                else:
                    self.model.state.time_left = new_work_time
                self.model.state.total_time = new_work_time
                
                if self.model.state.state == TimerState.RUNNING and self.model.state.start_time:
                    self.model.state.start_time = time.time() - (new_work_time - self.model.state.time_left)
            
            SettingsManager.save_settings(self.model.settings)
            
            self.update_interface_after_settings()
            
            settings_view.close()
            
        except ValueError:
            if self.model.settings.language == "RU":
                error_message = "Пожалуйста, введите корректные числовые значения\n\n"
                error_message += "Убедитесь, что все поля содержат только цифры."
            else:
                error_message = "Please enter valid numeric values\n\n"
                error_message += "Make sure all fields contain only numbers."
            
            messagebox.showerror(
                "Ошибка ввода" if self.model.settings.language == "RU" else "Input Error",
                error_message
            )

        
    def update_interface_after_settings(self):
        """Update interface after settings change"""
        # Update window sizes
        window_height = self.model.actual_bar_height
        current_y = self.root.winfo_y()
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{window_height}+0+{current_y}")
        
        # Update main window
        self.root.configure(bg=self.model.settings.bg_color)
        self.views['main'].main_frame.configure(bg=self.model.settings.bg_color)
        self.views['main'].progress_canvas.configure(bg=self.model.settings.bg_color)
        
        # Update progress bar
        if hasattr(self.views['main'], 'progress_rect'):
            self.views['main'].progress_canvas.itemconfig(
                self.views['main'].progress_rect,
                fill=self.model.settings.progress_color,
                outline=self.model.settings.progress_color
            )
        
        # Recreate progress bar if height changed
        self.recreate_progress_bar()
        
        # Update display
        self.update_views()
        
        # Update control panel if visible
        if 'controls' in self.views and self.views['controls'].window and self.views['controls'].window.winfo_viewable():
            self.views['controls'].update_state()
    
    def recreate_progress_bar(self):
        """Recreate progress bar with new settings"""
        # Remove old progress bar
        if hasattr(self.views['main'], 'progress_canvas'):
            self.views['main'].progress_canvas.destroy()
        
        # Create new progress bar
        self.views['main'].create_progress_bar()
        
        # Rebind events for the new canvas
        canvas = self.views['main'].progress_canvas
        canvas.bind('<Button-1>', self.on_main_click)
        canvas.bind('<B1-Motion>', self.on_main_drag)
        canvas.bind('<Enter>', self.schedule_show_controls)
        canvas.bind('<Leave>', self.schedule_hide_controls)
        
        # Update progress
        canvas_width = self.views['main'].progress_canvas.winfo_width()
        if canvas_width > 1:
            progress_width = canvas_width * self.model.get_progress()
            self.views['main'].update_progress(progress_width)
    
    # ========== Helper methods ==========
    
    def play_notification_sound(self):
        """Play notification sound"""
        def play_sound():
            try:
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            except Exception as e:
                print(f"Failed to play sound: {e}")
        
        sound_thread = threading.Thread(target=play_sound, daemon=True)
        sound_thread.start()
    
    def on_closing(self):
        """Handle application closing"""
        # Stop controls check
        if self.controls_check_id:
            self.root.after_cancel(self.controls_check_id)
        
        # Save position
        self.model.settings.window_y_offset = self.root.winfo_y()
        
        # Save settings
        SettingsManager.save_settings(self.model.settings)
        
        # Close window
        self.root.destroy()

# ============================================
# Custom view for errors
# ============================================

def show_error_window(error_msg: str):
    """Show error window"""
    error_root = tk.Tk()
    error_root.title("Pomodoro Timer - Error")
    error_root.configure(bg=Defaults.BG_COLOR)
    error_root.resizable(True, True)
    error_root.overrideredirect(True)
    error_root.withdraw()
    
    # Variables for dragging
    _error_offset = (0, 0)
    
    def click_error_title(event):
        nonlocal _error_offset
        _error_offset = (event.x_root - error_root.winfo_x(),
                        event.y_root - error_root.winfo_y())
    
    def drag_error_window(event):
        new_x = event.x_root - _error_offset[0]
        new_y = event.y_root - _error_offset[1]
        
        screen_width = error_root.winfo_screenwidth()
        screen_height = error_root.winfo_screenheight()
        window_width = error_root.winfo_width()
        window_height = error_root.winfo_height()
        
        if new_x < 0: new_x = 0
        elif new_x > screen_width - window_width: new_x = screen_width - window_width
        
        if new_y < 0: new_y = 0
        elif new_y > screen_height - window_height: new_y = screen_height - window_height
        
        error_root.geometry(f"+{new_x}+{new_y}")
    
    # Title
    title_frame = tk.Frame(error_root, bg='#333333', height=40)
    title_frame.pack(fill=tk.X, side=tk.TOP)
    title_frame.pack_propagate(False)
    title_frame.bind('<Button-1>', click_error_title)
    title_frame.bind('<B1-Motion>', drag_error_window)
    
    title_label = tk.Label(
        title_frame,
        text="Pomodoro Timer - Error",
        font=('Arial', 14, 'bold'),
        fg=Defaults.TEXT_COLOR,
        bg='#333333'
    )
    title_label.pack(side=tk.LEFT, padx=15)
    title_label.bind('<Button-1>', click_error_title)
    title_label.bind('<B1-Motion>', drag_error_window)
    
    close_btn = tk.Button(
        title_frame,
        text="×",
        font=('Arial', 20, 'bold'),
        command=error_root.destroy,
        bg='#333333',
        fg=Defaults.TEXT_COLOR,
        relief=tk.FLAT,
        bd=0,
        padx=10,
        pady=0,
        cursor='hand2',
        activebackground=Defaults.ERROR_COLOR,
        activeforeground=Defaults.TEXT_COLOR
    )
    close_btn.pack(side=tk.RIGHT)
    
    # Error text
    text_frame = tk.Frame(error_root, bg=Defaults.BG_COLOR)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar = tk.Scrollbar(text_frame, width=0)
    
    error_text = tk.Text(
        text_frame,
        bg='#333333',
        fg=Defaults.ERROR_COLOR,
        font=('Courier New', 10),
        wrap=tk.WORD,
        yscrollcommand=scrollbar.set,
        relief=tk.FLAT,
        bd=2,
        highlightthickness=0
    )
    
    scrollbar.config(command=error_text.yview)
    error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    error_text.insert(1.0, error_msg)
    error_text.config(state=tk.DISABLED)
    
    def on_mouse_wheel(event):
        scroll_direction = -1 if event.delta > 0 else 1
        error_text.yview_scroll(scroll_direction, "units")
    
    error_text.bind("<MouseWheel>", on_mouse_wheel)
    
    # Buttons
    button_frame = tk.Frame(error_root, bg=Defaults.BG_COLOR)
    button_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
    
    copy_btn = tk.Button(
        button_frame,
        text="Copy Error",
        font=('Arial', 12, 'bold'),
        command=lambda: error_root.clipboard_append(error_msg),
        bg=Defaults.SUCCESS_COLOR,
        fg=Defaults.TEXT_COLOR,
        padx=20,
        pady=5
    )
    copy_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def restart_app():
        error_root.destroy()
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    restart_btn = tk.Button(
        button_frame,
        text="Restart App",
        font=('Arial', 12, 'bold'),
        command=restart_app,
        bg='#2196F3',
        fg=Defaults.TEXT_COLOR,
        padx=20,
        pady=5
    )
    restart_btn.pack(side=tk.LEFT)
    
    def close_app():
        try:
            error_root.destroy()
            os._exit(1)
        except:
            os._exit(1)
    
    close_app_btn = tk.Button(
        button_frame,
        text="Close App",
        font=('Arial', 12, 'bold'),
        command=close_app,
        bg=Defaults.ERROR_COLOR,
        fg=Defaults.TEXT_COLOR,
        padx=20,
        pady=5
    )
    close_app_btn.pack(side=tk.RIGHT)
    
    error_root.minsize(600, 400)
    
    def center_and_show():
        error_root.update_idletasks()
        width, height = 700, 500
        screen_width = error_root.winfo_screenwidth()
        screen_height = error_root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        error_root.geometry(f"{width}x{height}+{x}+{y}")
        error_root.attributes('-topmost', True)
        error_root.deiconify()
    
    error_root.after(10, center_and_show)
    error_root.mainloop()

# ============================================
# Entry point
# ============================================

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PomodoroController(root)
        root.mainloop()
    except Exception as e:
        error_msg = f"An error occurred in Pomodoro Timer:\n\n"
        error_msg += f"Error type: {type(e).__name__}\n"
        error_msg += f"Error message: {str(e)}\n\n"
        error_msg += "Traceback:\n"
        error_msg += traceback.format_exc()
        
        print(error_msg)
        show_error_window(error_msg)