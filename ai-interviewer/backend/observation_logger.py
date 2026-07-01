"""
Observation logging and final behavioral report generation.
Accumulates observations throughout interview and saves to structured dataset.
"""
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import os
import uuid
from pathlib import Path


class ObservationLogger:
    """Logs observations and generates final behavioral analysis report."""

    def __init__(self, session_id: str = None, dataset_path: str = "dataset"):
        self.observations = []
        self.violations = defaultdict(int)
        self.session_start = time.time()
        self.eye_contact_periods = []
        self.stress_timeline = []
        self.voice_confidence_scores = []
        self.expression_scores = defaultdict(list)
        self.looking_away_cumulative = 0
        self.total_observation_time = 0
        
        # Session management for dataset
        self.session_id = session_id or str(uuid.uuid4())
        self.dataset_path = Path(dataset_path)
        self.session_dir = self.dataset_path / "sessions" / f"session_{self.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Transcript storage (will be populated by interview engine)
        self.transcript_data = {
            "session_id": self.session_id,
            "total_questions": 0,
            "qa_pairs": []
        }
        
        # Create log file for facial expressions
        self.log_file = "facial_expressions.txt"
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Initialize the facial expressions log file."""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write("FACIAL EXPRESSION ANALYSIS LOG\n")
                f.write(f"Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
            print(f"[INFO] Facial expression log file created: {self.log_file}")
        except Exception as e:
            print(f"[ERROR] Failed to create log file: {e}")

    def log_observation(self, observation: Dict):
        """Log a single behavioral observation."""
        obs_entry = {
            "timestamp": time.time() - self.session_start,
            **observation
        }
        self.observations.append(obs_entry)
        self._update_analytics(observation)
        self._log_facial_data_to_file(observation)

    def _update_analytics(self, observation: Dict):
        """Update running analytics from observation."""
        # Debug: Print observation structure periodically
        if len(self.observations) % 50 == 1:
            print(f"[DEBUG] Observation structure sample: face_detected={observation.get('face_detected')}, face keys={list(observation.get('face', {}).keys())}")
        
        # Eye contact tracking
        face_data = observation.get("face", {})
        if face_data.get("face_detected"):
            looking_away = face_data.get("looking_away", False)
            eye_contact = not looking_away
            self.eye_contact_periods.append({
                "timestamp": time.time() - self.session_start,
                "eye_contact": eye_contact
            })
            if looking_away:
                self.looking_away_cumulative += 1
        
        # Stress timeline
        audio_data = observation.get("audio", {})
        if audio_data.get("stress_level"):
            self.stress_timeline.append({
                "timestamp": time.time() - self.session_start,
                "stress_level": audio_data["stress_level"],
                "pitch_spike": audio_data.get("pitch_spike", False),
                "silence": audio_data.get("silence_detected", False)
            })
        
        # Voice confidence
        if "voice_confidence" in audio_data:
            self.voice_confidence_scores.append(audio_data["voice_confidence"])
        
        # Expression tracking
        emotion_data = observation.get("emotion", {})
        if emotion_data.get("emotion"):
            self.expression_scores[emotion_data["emotion"]].append(
                emotion_data.get("confidence", 0.0)
            )
        
        # Violation tracking
        if face_data.get("looking_away"):
            self.violations["looked_away"] += 1
        if audio_data.get("stress_level") == "high":
            self.violations["high_stress"] += 1
        if audio_data.get("silence_detected") and audio_data.get("silence_duration", 0) > 5:
            self.violations["long_silence"] += 1
        if not face_data.get("face_detected"):
            self.violations["face_not_detected"] += 1
    
    def _log_facial_data_to_file(self, observation: Dict):
        """Log facial expression data to text file."""
        try:
            timestamp = time.time() - self.session_start
            face_data = observation.get("face", {})
            emotion_data = observation.get("emotion", {})
            audio_data = observation.get("audio", {})
            
            # Check if face is detected in the face data
            if not face_data.get("face_detected", False):
                return
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp:.2f}s] Timestamp: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write("-" * 80 + "\n")
                
                # Face data
                f.write("FACE DETECTION:\n")
                f.write(f"  Face Detected: {face_data.get('face_detected', False)}\n")
                f.write(f"  Looking at Camera: {face_data.get('looking_at_camera', False)}\n")
                f.write(f"  Eye Contact Confidence: {face_data.get('eye_contact_confidence', 0):.2f}\n")
                f.write(f"  Looking Away: {face_data.get('looking_away', False)}\n")
                f.write(f"  Head Pose - Yaw: {face_data.get('yaw', 0):.1f}°, Pitch: {face_data.get('pitch', 0):.1f}°\n")
                
                # Emotion data
                f.write("\nEMOTION ANALYSIS:\n")
                f.write(f"  Primary Emotion: {emotion_data.get('emotion', 'N/A')}\n")
                f.write(f"  Confidence: {emotion_data.get('confidence', 0):.2f}/10\n")
                f.write(f"  Stress Level: {emotion_data.get('stress_level', 'N/A')}\n")
                
                if emotion_data.get('emotion_scores'):
                    f.write("  All Emotion Scores:\n")
                    for emotion, score in emotion_data['emotion_scores'].items():
                        f.write(f"    - {emotion}: {score:.2f}/10\n")
                
                # Audio/Voice data
                f.write("\nVOICE ANALYSIS:\n")
                f.write(f"  Stress Level: {audio_data.get('stress_level', 'N/A')}\n")
                f.write(f"  Voice Confidence: {audio_data.get('voice_confidence', 0):.1f}/10\n")
                f.write(f"  Pitch: {audio_data.get('pitch', 0):.1f} Hz\n")
                f.write(f"  Energy: {audio_data.get('energy', 0):.4f}\n")
                f.write(f"  Silence Detected: {audio_data.get('silence_detected', False)}\n")
                
                # Violations
                if face_data.get('multiple_faces'):
                    f.write("\n⚠️  VIOLATION: Multiple persons detected!\n")
                
                f.write("\n" + "=" * 80 + "\n")
                
        except Exception as e:
            print(f"[ERROR] Failed to write to log file: {e}")
            import traceback
            traceback.print_exc()

    def generate_report(self) -> Dict:
        """Generate final behavioral analysis report."""
        self.total_observation_time = time.time() - self.session_start
        
        # Calculate scores
        eye_contact_score = self._calculate_eye_contact_score()
        focus_score = self._calculate_focus_score()
        stress_level = self._calculate_stress_level()
        voice_confidence = self._calculate_voice_confidence()
        
        # Extract insights
        strengths = self._identify_strengths(eye_contact_score, voice_confidence, focus_score)
        improvements = self._identify_improvements()
        
        # Overall readiness
        readiness = self._calculate_overall_readiness(
            eye_contact_score, focus_score, voice_confidence, stress_level
        )
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "session_duration": float(self.total_observation_time),
            "eye_contact_score": float(eye_contact_score),
            "focus_score": float(focus_score),
            "stress_level": stress_level,
            "voice_confidence": float(voice_confidence),
            "violations": dict(self.violations),
            "behavioral_strengths": strengths,
            "behavioral_improvements": improvements,
            "overall_interview_readiness": readiness,
            "detailed_metrics": {
                "total_observations": len(self.observations),
                "looking_away_incidents": int(self.violations.get("looked_away", 0)),
                "high_stress_incidents": int(self.violations.get("high_stress", 0)),
                "long_silence_incidents": int(self.violations.get("long_silence", 0)),
                "face_not_detected": int(self.violations.get("face_not_detected", 0)),
                "avg_voice_confidence": float(np.mean(self.voice_confidence_scores)) if self.voice_confidence_scores else 0.0,
                "dominant_expressions": dict(self._get_dominant_expressions()),
            }
        }
        
        return report

    def _calculate_eye_contact_score(self) -> float:
        """Calculate eye contact score (0-10)."""
        if not self.eye_contact_periods:
            # Fallback: check all observations for face data
            total_frames = 0
            looking_at_camera_frames = 0
            
            for obs in self.observations:
                face_data = obs.get("face", {})
                if face_data.get("face_detected"):
                    total_frames += 1
                    if face_data.get("looking_at_camera"):
                        looking_at_camera_frames += 1
                    # Also use eye contact confidence if available
                    elif face_data.get("eye_contact_confidence", 0) > 0.7:
                        looking_at_camera_frames += 1
            
            if total_frames == 0:
                return 0.0
            
            score = (looking_at_camera_frames / total_frames) * 10
            return float(np.clip(score, 0, 10))
        
        eye_contact_count = sum(1 for p in self.eye_contact_periods if p["eye_contact"])
        total = len(self.eye_contact_periods)
        score = (eye_contact_count / total) * 10 if total > 0 else 0
        return float(np.clip(score, 0, 10))

    def _calculate_focus_score(self) -> float:
        """Calculate focus/consistency score (0-10)."""
        if not self.observations:
            return 5.0
        
        # Focus = consistent eye contact + low looking away incidents + face detected
        total_frames = len(self.observations)
        face_detected_count = 0
        looking_away_count = 0
        
        for obs in self.observations:
            face_data = obs.get("face", {})
            if face_data.get("face_detected"):
                face_detected_count += 1
                if face_data.get("looking_away"):
                    looking_away_count += 1
        
        if total_frames == 0:
            return 5.0
        
        # Calculate focus: presence (face detected) + attention (not looking away)
        presence_score = (face_detected_count / total_frames) * 10
        
        if face_detected_count > 0:
            attention_ratio = 1 - (looking_away_count / face_detected_count)
            attention_score = attention_ratio * 10
        else:
            attention_score = 0
        
        # Weighted average: 40% presence, 60% attention
        focus_score = (presence_score * 0.4) + (attention_score * 0.6)
        
        return float(np.clip(focus_score, 0, 10))

    def _calculate_stress_level(self) -> str:
        """Determine overall stress level from timeline."""
        if not self.stress_timeline:
            # Fallback: check observations
            stress_counts = {"low": 0, "medium": 0, "high": 0, "calibrating": 0}
            
            for obs in self.observations:
                audio_data = obs.get("audio", {})
                emotion_data = obs.get("emotion", {})
                
                stress = audio_data.get("stress_level") or emotion_data.get("stress_level")
                if stress and stress in stress_counts:
                    stress_counts[stress] += 1
            
            # Remove calibrating from consideration
            del stress_counts["calibrating"]
            
            if sum(stress_counts.values()) == 0:
                return "low"
            
            # Return the most common stress level
            return max(stress_counts, key=stress_counts.get)
        
        high_stress_count = sum(1 for s in self.stress_timeline if s["stress_level"] == "high")
        medium_stress_count = sum(1 for s in self.stress_timeline if s["stress_level"] == "medium")
        total = len(self.stress_timeline)
        
        high_ratio = high_stress_count / total if total > 0 else 0
        medium_ratio = medium_stress_count / total if total > 0 else 0
        
        if high_ratio > 0.3:
            return "high"
        elif medium_ratio > 0.4 or (high_ratio + medium_ratio) > 0.5:
            return "medium"
        else:
            return "low"

    def _calculate_voice_confidence(self) -> float:
        """Calculate average voice confidence (0-10)."""
        if not self.voice_confidence_scores:
            # Fallback: extract from all observations
            voice_scores = []
            for obs in self.observations:
                audio_data = obs.get("audio", {})
                if "voice_confidence" in audio_data and audio_data["voice_confidence"] > 0:
                    voice_scores.append(audio_data["voice_confidence"])
            
            if not voice_scores:
                return 5.0  # Neutral score if no data
            
            return float(np.clip(np.mean(voice_scores), 0, 10))
        
        return float(np.clip(np.mean(self.voice_confidence_scores), 0, 10))

    def _identify_strengths(self, eye_contact: float, voice: float, focus: float) -> List[str]:
        """Identify behavioral strengths."""
        strengths = []
        
        if eye_contact >= 7:
            strengths.append("Good eye contact maintained throughout interview")
        if voice >= 7:
            strengths.append("Confident and clear voice projection")
        if focus >= 8:
            strengths.append("Excellent focus and attention to interviewer")
        if not self.violations.get("long_silence", 0) or self.violations["long_silence"] < 2:
            strengths.append("Minimal awkward silences")
        if self.violations.get("high_stress", 0) < 3:
            strengths.append("Maintained composure under pressure")
        
        return strengths if strengths else ["Completed interview successfully"]

    def _identify_improvements(self) -> List[str]:
        """Identify specific, actionable areas for improvement based on observed behaviors."""
        improvements = []
        
        # Calculate metrics
        eye_contact_score = self._calculate_eye_contact_score()
        voice_avg = np.mean(self.voice_confidence_scores) if self.voice_confidence_scores else 5.0
        looked_away_count = self.violations.get("looked_away", 0)
        face_not_detected = self.violations.get("face_not_detected", 0)
        high_stress_count = self.violations.get("high_stress", 0)
        long_silence_count = self.violations.get("long_silence", 0)
        total_observations = max(len(self.observations), 1)
        
        # Eye contact improvements (priority 1)
        if eye_contact_score < 5.0:
            improvements.append("🎯 CRITICAL: Maintain direct eye contact with camera - looked away " + 
                              f"{looked_away_count} times. Practice speaking while looking at camera lens.")
        elif eye_contact_score < 7.0:
            improvements.append("👁️  Improve eye contact consistency - try to look at camera for 80% of interview. " +
                              f"You looked away {looked_away_count} times.")
        elif looked_away_count > 5:
            improvements.append("✓ Good eye contact overall, but minimize looking away during answers " +
                              f"({looked_away_count} instances detected)")
        
        # Camera positioning and framing
        face_not_detected_pct = (face_not_detected / total_observations) * 100
        if face_not_detected_pct > 15:
            improvements.append(f"📸 CRITICAL: Face not visible {face_not_detected_pct:.1f}% of time - " +
                              "adjust camera position to keep face centered in frame")
        elif face_not_detected_pct > 5:
            improvements.append(f"📸 Ensure you stay centered in camera frame - face not detected " +
                              f"{face_not_detected_pct:.1f}% of time")
        
        # Voice confidence (priority 2)
        if voice_avg < 4.0:
            improvements.append(f"🎤 CRITICAL: Voice confidence very low ({voice_avg:.1f}/10) - " +
                              "practice speaking clearly, loudly, and at steady pace. Consider voice coaching.")
        elif voice_avg < 6.0:
            improvements.append(f"🎤 Build voice confidence ({voice_avg:.1f}/10) - speak with more authority, " +
                              "project your voice, avoid trailing off at end of sentences")
        elif voice_avg < 7.5:
            improvements.append(f"🗣️  Good voice delivery ({voice_avg:.1f}/10), but can improve by varying tone " +
                              "and speaking with more conviction on key points")
        
        # Stress management (priority 3)
        if high_stress_count > 10:
            improvements.append(f"😰 CRITICAL: High stress detected {high_stress_count} times - " +
                              "practice deep breathing, pausing before answers, mock interviews to build comfort")
        elif high_stress_count > 5:
            improvements.append(f"😓 Moderate stress detected {high_stress_count} times - " +
                              "work on relaxation techniques, remember to breathe, stay hydrated")
        elif high_stress_count > 2:
            improvements.append(f"😊 Mostly calm but showed stress {high_stress_count} times - " +
                              "practice staying composed during difficult questions")
        
        # Response timing
        if long_silence_count > 5:
            improvements.append(f"⏱️  Reduce long pauses - {long_silence_count} extended silences detected. " +
                              "Practice saying 'That's a great question, let me think...' instead of silence.")
        elif long_silence_count > 2:
            improvements.append(f"⏱️  {long_silence_count} long pauses detected - work on responding more promptly, " +
                              "it's okay to take a moment but acknowledge the question first")
        
        # Emotion/engagement
        if hasattr(self, 'emotion_timeline') and len(self.emotion_timeline) > 0:
            emotions = [e['emotion'] for e in self.emotion_timeline if 'emotion' in e]
            if emotions.count('Confused') > len(emotions) * 0.3:
                improvements.append("❓ Frequently appeared confused - ask for clarification when needed, " +
                                  "prepare for common interview questions")
            if emotions.count('Stressed') > len(emotions) * 0.4:
                improvements.append("😌 Work on appearing more relaxed - practice power poses before interview, " +
                                  "smile naturally, remember interviewer wants you to succeed")
        
        # Positive reinforcement if excellent performance
        if not improvements:
            return ["🌟 EXCELLENT: All metrics show strong performance! You're interview-ready. " +
                   "Maintain this confidence and consistency in real interviews."]
        elif len(improvements) <= 2:
            improvements.append("💪 Overall strong performance - addressing these minor points will make you exceptional")
        
        return improvements

    def _calculate_overall_readiness(self, eye_contact: float, focus: float, voice: float, stress: str) -> str:
        """Calculate overall interview readiness."""
        # Calculate composite score with stress impact
        stress_score_map = {"low": 10, "medium": 6, "high": 3}
        stress_score = stress_score_map.get(stress, 7)
        
        # Weighted average: 30% eye contact, 25% focus, 25% voice, 20% stress
        composite = (
            eye_contact * 0.30 +
            focus * 0.25 +
            voice * 0.25 +
            stress_score * 0.20
        )
        
        # Determine readiness level with descriptive feedback
        if composite >= 8.0:
            return "Excellent - Ready for senior roles"
        elif composite >= 7.0:
            return "Very Good - Ready for most positions"
        elif composite >= 6.0:
            return "Good - Ready with minor improvements"
        elif composite >= 5.0:
            return "Moderate - Practice recommended"
        elif composite >= 3.5:
            return "Developing - Significant practice needed"
        else:
            return "Beginner - Extensive preparation required"

    def _get_dominant_expressions(self) -> Dict[str, float]:
        """Get average confidence for each emotion detected."""
        dominant = {}
        for emotion, scores in self.expression_scores.items():
            if scores:
                dominant[emotion] = float(np.mean(scores))
        return dominant

    def to_json(self) -> str:
        """Serialize report to JSON."""
        report = self.generate_report()
        return json.dumps(report, indent=2)
    
    def close_log_file(self):
        """Close the log file and save all dataset files."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write("\n\n" + "="*80 + "\n")
                f.write("SESSION COMPLETED\n")
                f.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Duration: {self.total_observation_time:.2f} seconds\n")
                f.write(f"Total Observations: {len(self.observations)}\n")
                f.write("="*80 + "\n")
            print(f"[INFO] Facial expression log file closed: {self.log_file}")
        except Exception as e:
            print(f"[ERROR] Failed to close log file: {e}")
        
        # Save all dataset files
        self.save_dataset_files()
    
    def save_dataset_files(self):
        """Save all observation data to structured dataset files."""
        try:
            # 1. Video metadata
            metadata = {
                "session_id": self.session_id,
                "timestamp": datetime.fromtimestamp(self.session_start).isoformat(),
                "duration_seconds": self.total_observation_time,
                "total_observations": len(self.observations)
            }
            self._save_json(self.session_dir / "video_metadata.json", metadata)
            
            # 2. Transcript (if available)
            if self.transcript_data["qa_pairs"]:
                self._save_json(self.session_dir / "transcript.json", self.transcript_data)
            
            # 3. Gaze metrics
            gaze_metrics = self._extract_gaze_metrics()
            self._save_json(self.session_dir / "gaze_metrics.json", gaze_metrics)
            
            # 4. Emotion metrics
            emotion_metrics = self._extract_emotion_metrics()
            self._save_json(self.session_dir / "emotion_metrics.json", emotion_metrics)
            
            # 5. Proctoring metrics
            proctoring_metrics = self._extract_proctoring_metrics()
            self._save_json(self.session_dir / "proctoring_metrics.json", proctoring_metrics)
            
            # 6. Final report
            final_report = self.generate_report()
            self._save_json(self.session_dir / "final_report.json", final_report)
            
            print(f"[INFO] Dataset files saved to {self.session_dir}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save dataset files: {e}")
            import traceback
            traceback.print_exc()
    
    def _extract_gaze_metrics(self) -> Dict:
        """Extract gaze tracking metrics from observations."""
        frames = []
        total_eye_contact = 0
        total_look_away_duration = 0
        total_blinks = 0
        
        for obs in self.observations:
            face_data = obs.get("face", {})
            timestamp = obs.get("timestamp", 0)
            
            frame = {
                "timestamp": float(timestamp),
                "gaze_direction": face_data.get("gaze_direction", "unknown"),
                "eye_contact_percentage": float(face_data.get("eye_contact_confidence", 0)) * 100,
                "head_pose_yaw": float(face_data.get("head_yaw", 0)),
                "head_pose_pitch": float(face_data.get("head_pitch", 0)),
                "head_pose_roll": float(face_data.get("head_roll", 0)),
                "blink_detected": face_data.get("blink_detected", False),
                "looking_away": face_data.get("looking_away", False),
                "look_away_duration": 0.0 if not face_data.get("looking_away") else 1.0
            }
            
            frames.append(frame)
            
            if not face_data.get("looking_away"):
                total_eye_contact += 1
            else:
                total_look_away_duration += 1.0
            
            if face_data.get("blink_detected"):
                total_blinks += 1
        
        duration = self.total_observation_time or 1.0
        
        return {
            "total_frames": len(frames),
            "duration_seconds": duration,
            "frames": frames,
            "summary": {
                "eye_contact_percentage": (total_eye_contact / len(frames)) * 100 if frames else 0,
                "average_gaze_stability": 0.7,  # Placeholder
                "total_look_away_duration": total_look_away_duration,
                "blink_rate_per_minute": (total_blinks / duration) * 60 if duration > 0 else 0,
                "head_movement_score": 0.8  # Placeholder
            }
        }
    
    def _extract_emotion_metrics(self) -> Dict:
        """Extract emotion tracking metrics from observations."""
        frames = []
        emotion_counts = defaultdict(int)
        
        for obs in self.observations:
            emotion_data = obs.get("emotion", {})
            timestamp = obs.get("timestamp", 0)
            
            emotion = emotion_data.get("emotion", "unknown")
            confidence = emotion_data.get("confidence", 0)
            
            frame = {
                "timestamp": float(timestamp),
                "dominant_emotion": emotion,
                "confidence": float(confidence),
                "emotions": emotion_data.get("emotion_scores", {})
            }
            
            frames.append(frame)
            emotion_counts[emotion] += 1
        
        # Calculate dominant emotion
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "unknown"
        
        # Calculate emotion distribution
        total = sum(emotion_counts.values()) or 1
        emotion_distribution = {k: v / total for k, v in emotion_counts.items()}
        
        return {
            "total_frames": len(frames),
            "frames": frames,
            "summary": {
                "dominant_emotion": dominant_emotion,
                "emotion_distribution": emotion_distribution,
                "confidence_average": 0.75  # Placeholder
            }
        }
    
    def _extract_proctoring_metrics(self) -> Dict:
        """Extract proctoring violation metrics."""
        violations = []
        
        # Check for multiple persons
        multi_person_count = self.violations.get("multiple_persons", 0)
        if multi_person_count > 0:
            violations.append({
                "timestamp": 0,
                "type": "MULTIPLE_PERSONS",
                "severity": "CRITICAL",
                "description": f"Multiple people detected {multi_person_count} times"
            })
        
        # Check for excessive looking away
        looked_away = self.violations.get("looked_away", 0)
        if looked_away > 20:
            violations.append({
                "timestamp": 0,
                "type": "EXCESSIVE_LOOK_AWAY",
                "severity": "HIGH",
                "description": f"Looked away {looked_away} times"
            })
        
        # Calculate suspicious activity score
        suspicious_score = min(1.0, (multi_person_count * 0.3 + looked_away * 0.01))
        
        return {
            "total_violations": len(violations),
            "violations": violations,
            "person_count_average": 1.0,
            "suspicious_activity_score": suspicious_score
        }
    
    def add_transcript_qa(self, question: str, answer: str, category: str = "general"):
        """Add question-answer pair to transcript."""
        qa_pair = {
            "question_number": len(self.transcript_data["qa_pairs"]) + 1,
            "timestamp": time.time() - self.session_start,
            "category": category,
            "interviewer_question": question,
            "candidate_answer": answer,
            "answer_duration": 0,
            "pause_before_answer": 0
        }
        
        self.transcript_data["qa_pairs"].append(qa_pair)
        self.transcript_data["total_questions"] = len(self.transcript_data["qa_pairs"])
    
    @staticmethod
    def _save_json(filepath: Path, data: Dict):
        """Save data as JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


import numpy as np  # Import at end to avoid circular imports
