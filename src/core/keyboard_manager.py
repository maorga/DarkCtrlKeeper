"""
Keyboard Manager
================

Handles virtual keyboard control and hotkey detection.
"""

from typing import Callable, Optional

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("ERROR: 'pynput' is not installed. Run: pip install pynput")


class KeyboardManager:
    """Manages CTRL key simulation and hotkey listening."""
    
    def __init__(self, on_hotkey_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize keyboard manager.
        
        Args:
            on_hotkey_callback: Callback function when hotkey is pressed
        """
        if not PYNPUT_AVAILABLE:
            raise ImportError("pynput is required for keyboard control")
            
        self.ctrl_controller = keyboard.Controller()
        self.simulated_ctrl_held = False
        self.selected_hotkey = '5'
        self.on_hotkey_callback = on_hotkey_callback
        self.listener: Optional[keyboard.Listener] = None
    
    def start_listening(self) -> None:
        """Start keyboard listener for hotkey detection."""
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
            print("✓ Keyboard listener started")
    
    def stop_listening(self) -> None:
        """Stop keyboard listener."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            print("✓ Keyboard listener stopped")
    
    def press_ctrl(self) -> bool:
        """
        Press and hold CTRL key.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ctrl_controller.press(keyboard.Key.ctrl_l)
            self.simulated_ctrl_held = True
            print("✓ CTRL key pressed and held virtually")
            return True
        except Exception as e:
            print(f"Warning: Could not simulate CTRL press: {e}")
            return False
    
    def release_ctrl(self) -> bool:
        """
        Release CTRL key.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.simulated_ctrl_held:
                self.ctrl_controller.release(keyboard.Key.ctrl_l)
                self.simulated_ctrl_held = False
                print("✓ CTRL key released")
            return True
        except Exception as e:
            print(f"Warning: Could not release CTRL: {e}")
            return False
    
    def set_hotkey(self, key: str) -> None:
        """
        Set the hotkey to listen for.
        
        Args:
            key: The hotkey character (e.g., '4' or '5')
        """
        self.selected_hotkey = key
        print(f"✓ Hotkey set to: {key}")
    
    def _on_key_press(self, key) -> None:
        """
        Internal callback for key press events.
        
        Args:
            key: The key that was pressed
        """
        try:
            # Character detection
            if hasattr(key, 'char') and key.char == self.selected_hotkey:
                if self.on_hotkey_callback:
                    self.on_hotkey_callback(self.selected_hotkey)
                print(f"✓ Key {self.selected_hotkey} pressed (char detection)")
                return
            
            # VK code detection for CTRL+number combinations
            if hasattr(key, 'vk'):
                if self.selected_hotkey == '4' and key.vk == 0x34:
                    if self.on_hotkey_callback:
                        self.on_hotkey_callback('4')
                    print("✓ Key 4 pressed (vk detection)")
                elif self.selected_hotkey == '5' and key.vk == 0x35:
                    if self.on_hotkey_callback:
                        self.on_hotkey_callback('5')
                    print("✓ Key 5 pressed (vk detection)")
        except AttributeError:
            pass
        except Exception as e:
            print(f"Keyboard listener error: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources and release any held keys."""
        self.release_ctrl()
        self.stop_listening()
