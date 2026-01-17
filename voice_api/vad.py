"""Voice Activity Detection (VAD) module for robust speech detection."""

from __future__ import annotations

import collections
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

try:
    import webrtcvad
    HAS_WEBRTC = True
except ImportError:
    HAS_WEBRTC = False

from .config import LOGGER


class SpeechState(Enum):
    """Current state of speech detection."""
    SILENCE = "silence"
    SPEAKING = "speaking"
    SPEECH_ENDED = "speech_ended"


@dataclass
class VADConfig:
    """Configuration for Voice Activity Detection."""
    
    # WebRTC VAD aggressiveness: 0-3 (0=least aggressive, 3=most aggressive)
    # Higher values filter more aggressively but may cut off speech
    aggressiveness: int = 2
    
    # Sample rate must be 8000, 16000, 32000, or 48000 for WebRTC
    sample_rate: int = 16000
    
    # Frame duration in ms (10, 20, or 30 for WebRTC)
    frame_duration_ms: int = 30
    
    # Number of consecutive speech frames to trigger speech start
    speech_start_frames: int = 3
    
    # Number of consecutive silence frames to trigger speech end
    speech_end_frames: int = 10
    
    # Minimum speech duration in seconds (ignore very short bursts)
    min_speech_duration: float = 0.3
    
    # Maximum speech duration in seconds (force cutoff for very long speech)
    max_speech_duration: float = 30.0
    
    # Energy threshold for simple fallback detection (0-1, or None to disable)
    energy_threshold: Optional[float] = 0.02
    
    def __post_init__(self):
        """Validate configuration."""
        if HAS_WEBRTC:
            if self.aggressiveness not in (0, 1, 2, 3):
                raise ValueError("aggressiveness must be 0, 1, 2, or 3")
            if self.sample_rate not in (8000, 16000, 32000, 48000):
                raise ValueError("sample_rate must be 8000, 16000, 32000, or 48000")
            if self.frame_duration_ms not in (10, 20, 30):
                raise ValueError("frame_duration_ms must be 10, 20, or 30")
    
    @property
    def frame_size(self) -> int:
        """Calculate frame size in bytes for the given duration and sample rate."""
        # 16-bit PCM = 2 bytes per sample
        return int(self.sample_rate * self.frame_duration_ms / 1000) * 2


class VoiceActivityDetector:
    """
    Robust voice activity detection using WebRTC VAD with fallback.
    
    This detector uses a state machine approach:
    1. SILENCE: Waiting for speech to start
    2. SPEAKING: Active speech detected
    3. SPEECH_ENDED: Speech has ended (signals to stop recording)
    """
    
    def __init__(self, config: Optional[VADConfig] = None):
        """Initialize the VAD with the given configuration."""
        self.config = config or VADConfig()
        
        # Initialize WebRTC VAD if available
        self.vad = None
        if HAS_WEBRTC:
            self.vad = webrtcvad.Vad(self.config.aggressiveness)
            LOGGER.info("Initialized WebRTC VAD (aggressiveness=%d)", self.config.aggressiveness)
        else:
            LOGGER.warning(
                "webrtcvad not installed; falling back to energy-based detection. "
                "Install with: pip install webrtcvad"
            )
        
        # State tracking
        self.state = SpeechState.SILENCE
        self.speech_frames = collections.deque(maxlen=self.config.speech_start_frames)
        self.silence_frames = collections.deque(maxlen=self.config.speech_end_frames)
        
        # Timing
        self.speech_start_time: Optional[float] = None
        self.last_speech_time: Optional[float] = None
        
    def reset(self):
        """Reset the detector state."""
        self.state = SpeechState.SILENCE
        self.speech_frames.clear()
        self.silence_frames.clear()
        self.speech_start_time = None
        self.last_speech_time = None
        LOGGER.debug("VAD state reset")
    
    def process_frame(self, audio_frame: bytes) -> SpeechState:
        """
        Process a single audio frame and return the current speech state.
        
        Args:
            audio_frame: Raw PCM audio data (16-bit, mono)
            
        Returns:
            Current SpeechState (SILENCE, SPEAKING, or SPEECH_ENDED)
        """
        current_time = time.time()
        
        # Check frame size
        expected_size = self.config.frame_size
        if len(audio_frame) != expected_size:
            LOGGER.debug(
                "Frame size mismatch: got %d bytes, expected %d. Padding/truncating.",
                len(audio_frame), expected_size
            )
            if len(audio_frame) < expected_size:
                audio_frame = audio_frame + b'\x00' * (expected_size - len(audio_frame))
            else:
                audio_frame = audio_frame[:expected_size]
        
        # Detect speech in this frame
        is_speech = self._is_speech_frame(audio_frame)
        
        # Update rolling windows
        self.speech_frames.append(is_speech)
        if self.state == SpeechState.SPEAKING:
            self.silence_frames.append(not is_speech)
        
        # State machine logic
        if self.state == SpeechState.SILENCE:
            # Check if we have enough consecutive speech frames to start
            if len(self.speech_frames) == self.config.speech_start_frames and all(self.speech_frames):
                self.state = SpeechState.SPEAKING
                self.speech_start_time = current_time
                self.last_speech_time = current_time
                self.silence_frames.clear()
                LOGGER.info("Speech started")
        
        elif self.state == SpeechState.SPEAKING:
            if is_speech:
                self.last_speech_time = current_time
            
            speech_duration = current_time - (self.speech_start_time or current_time)
            
            # Check for maximum duration exceeded
            if speech_duration > self.config.max_speech_duration:
                LOGGER.info("Maximum speech duration reached (%.1fs)", speech_duration)
                self.state = SpeechState.SPEECH_ENDED
            
            # Check for end of speech (consecutive silence frames)
            elif len(self.silence_frames) == self.config.speech_end_frames and all(self.silence_frames):
                # Verify minimum duration
                if speech_duration >= self.config.min_speech_duration:
                    LOGGER.info("Speech ended (duration: %.2fs)", speech_duration)
                    self.state = SpeechState.SPEECH_ENDED
                else:
                    LOGGER.debug("Ignoring short speech burst (%.2fs)", speech_duration)
                    self.reset()
        
        return self.state
    
    def _is_speech_frame(self, audio_frame: bytes) -> bool:
        """
        Determine if a single frame contains speech.
        
        Uses WebRTC VAD if available, otherwise falls back to energy detection.
        """
        # Try WebRTC VAD first
        if self.vad:
            try:
                return self.vad.is_speech(audio_frame, self.config.sample_rate)
            except Exception as exc:
                LOGGER.error("WebRTC VAD error: %s. Falling back to energy detection.", exc)
                self.vad = None  # Disable on error
        
        # Fallback: simple energy-based detection
        if self.config.energy_threshold is not None:
            return self._energy_based_detection(audio_frame)
        
        # No detection method available
        LOGGER.warning("No VAD method available; assuming speech")
        return True
    
    def _energy_based_detection(self, audio_frame: bytes) -> bool:
        """Simple energy-based speech detection (fallback method)."""
        # Convert bytes to 16-bit integers
        import struct
        samples = struct.unpack(f'{len(audio_frame) // 2}h', audio_frame)
        
        # Calculate RMS energy
        energy = sum(s * s for s in samples) / len(samples)
        normalized_energy = energy / (32768.0 ** 2)  # Normalize to 0-1
        
        return normalized_energy > (self.config.energy_threshold or 0.02)
    
    def should_send_audio(self) -> bool:
        """
        Check if audio should be sent to the API.
        
        Returns:
            True if currently speaking or just finished, False otherwise
        """
        return self.state in (SpeechState.SPEAKING, SpeechState.SPEECH_ENDED)
    
    def is_speech_complete(self) -> bool:
        """Check if a complete speech segment has been detected."""
        return self.state == SpeechState.SPEECH_ENDED
