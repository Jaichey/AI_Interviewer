"""
Automatic Scoring System for HireSense AI
Generates scores and hire decisions from interview data
"""
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import statistics


class AutoScoreGenerator:
    """Automatically score interview sessions based on metrics."""
    
    def __init__(self):
        # Scoring weights
        self.weights = {
            "technical": 0.40,
            "communication": 0.25,
            "clarity": 0.20,
            "confidence": 0.15
        }
        
        # Proctoring penalty configuration
        self.violation_penalties = {
            "MULTIPLE_PERSONS": 20,    # Critical violation
            "PHONE_DETECTED": 15,       # High severity
            "EXCESSIVE_LOOK_AWAY": 10,  # Medium severity
            "FACE_NOT_DETECTED": 5      # Low severity
        }
        
        # Thresholds
        self.eye_contact_good_threshold = 60  # %
        self.eye_contact_poor_threshold = 30  # %
        self.stress_keywords = ["um", "uh", "like", "you know", "I guess", "maybe", "probably"]
    
    def score_session(self, session_dir: Path) -> Dict:
        """
        Score a complete interview session.
        
        Args:
            session_dir: Path to session directory containing JSON files
        
        Returns:
            Dictionary with scores and hire decision
        """
        # Load all session data
        data = self._load_session_data(session_dir)
        
        # Score each dimension
        technical_score = self._score_technical(data)
        communication_score = self._score_communication(data)
        clarity_score = self._score_clarity(data)
        confidence_score = self._score_confidence(data)
        
        # Calculate weighted overall score (0-100 scale)
        overall_score = (
            technical_score * self.weights["technical"] +
            communication_score * self.weights["communication"] +
            clarity_score * self.weights["clarity"] +
            confidence_score * self.weights["confidence"]
        ) * 10
        
        # Apply proctoring penalties
        proctoring_penalty = self._calculate_proctoring_penalty(data)
        final_score = max(0, overall_score - proctoring_penalty)
        
        # Determine hire decision
        hire_decision = self._determine_hire_decision(final_score, data)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            hire_decision, final_score, data, proctoring_penalty
        )
        
        # Create final report
        report = {
            "session_id": data["metadata"]["session_id"],
            "candidate_name": data["metadata"].get("candidate_name", "Unknown"),
            "position": data["metadata"].get("position", "Unknown"),
            "timestamp": data["metadata"].get("timestamp", ""),
            "scores": {
                "technical_score": round(technical_score, 2),
                "communication_score": round(communication_score, 2),
                "clarity_score": round(clarity_score, 2),
                "confidence_score": round(confidence_score, 2),
                "overall_score": round(final_score, 2),
                "overall_score_before_penalties": round(overall_score, 2)
            },
            "behavioral_analysis": self._analyze_behavior(data),
            "proctoring_summary": self._summarize_proctoring(data, proctoring_penalty),
            "hire_decision": hire_decision,
            "recommendation": recommendation,
            "detailed_breakdown": {
                "strengths": self._identify_strengths(data),
                "weaknesses": self._identify_weaknesses(data),
                "interview_duration": data["metadata"].get("duration_seconds", 0)
            }
        }
        
        # Save report
        output_path = session_dir / "final_report.json"
        self._save_json(output_path, report)
        
        return report
    
    def _load_session_data(self, session_dir: Path) -> Dict:
        """Load all session JSON files."""
        data = {}
        
        files_to_load = [
            "video_metadata.json",
            "transcript.json",
            "gaze_metrics.json",
            "emotion_metrics.json",
            "proctoring_metrics.json"
        ]
        
        for filename in files_to_load:
            filepath = session_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    key = filename.replace(".json", "").replace("video_", "")
                    data[key] = json.load(f)
            else:
                print(f"Warning: {filename} not found in {session_dir}")
                data[filename.replace(".json", "")] = {}
        
        return data
    
    def _score_technical(self, data: Dict) -> float:
        """Score technical competency (0-10 scale)."""
        transcript = data.get("transcript", {})
        qa_pairs = transcript.get("qa_pairs", [])
        
        if not qa_pairs:
            return 5.0  # Default middle score
        
        # Analyze answer quality
        total_score = 0.0
        
        for qa in qa_pairs:
            answer = qa.get("candidate_answer", "")
            category = qa.get("category", "general")
            
            # Score based on answer length (proxy for depth)
            length_score = min(10, len(answer.split()) / 15)  # Longer = better (up to a point)
            
            # Score based on technical keywords
            technical_keywords = [
                "algorithm", "complexity", "data structure", "architecture",
                "design pattern", "optimization", "scalability", "performance",
                "database", "API", "framework", "system", "implementation"
            ]
            
            keyword_count = sum(1 for kw in technical_keywords if kw.lower() in answer.lower())
            keyword_score = min(10, keyword_count * 2)
            
            # Penalize vague answers
            vague_phrases = ["I think", "maybe", "probably", "not sure", "I guess"]
            vague_count = sum(1 for phrase in vague_phrases if phrase.lower() in answer.lower())
            vague_penalty = min(3, vague_count * 0.5)
            
            # Combine scores
            answer_score = (length_score * 0.4 + keyword_score * 0.6) - vague_penalty
            total_score += max(0, min(10, answer_score))
        
        return total_score / len(qa_pairs) if qa_pairs else 5.0
    
    def _score_communication(self, data: Dict) -> float:
        """Score communication skills (0-10 scale)."""
        gaze_data = data.get("gaze_metrics", {})
        emotion_data = data.get("emotion_metrics", {})
        transcript = data.get("transcript", {})
        
        score = 5.0  # Base score
        
        # Eye contact is crucial for communication
        eye_contact_pct = gaze_data.get("summary", {}).get("eye_contact_percentage", 50)
        if eye_contact_pct >= self.eye_contact_good_threshold:
            score += 3.0
        elif eye_contact_pct >= self.eye_contact_poor_threshold:
            score += 1.0
        else:
            score -= 1.0
        
        # Emotion analysis
        dominant_emotion = emotion_data.get("summary", {}).get("dominant_emotion", "neutral")
        if dominant_emotion in ["confident", "happy", "neutral"]:
            score += 1.5
        elif dominant_emotion in ["nervous", "surprised"]:
            score -= 0.5
        
        # Check for filler words
        qa_pairs = transcript.get("qa_pairs", [])
        if qa_pairs:
            total_words = sum(len(qa["candidate_answer"].split()) for qa in qa_pairs)
            filler_count = sum(
                sum(1 for kw in self.stress_keywords if kw in qa["candidate_answer"].lower())
                for qa in qa_pairs
            )
            filler_ratio = filler_count / max(total_words, 1)
            
            if filler_ratio < 0.05:
                score += 0.5
            elif filler_ratio > 0.15:
                score -= 1.0
        
        return max(0, min(10, score))
    
    def _score_clarity(self, data: Dict) -> float:
        """Score answer clarity and structure (0-10 scale)."""
        transcript = data.get("transcript", {})
        qa_pairs = transcript.get("qa_pairs", [])
        
        if not qa_pairs:
            return 5.0
        
        clarity_scores = []
        
        for qa in qa_pairs:
            answer = qa.get("candidate_answer", "")
            words = answer.split()
            
            # Score based on structure
            score = 5.0
            
            # Good length (not too short, not rambling)
            word_count = len(words)
            if 30 <= word_count <= 100:
                score += 2.0
            elif word_count < 15:
                score -= 2.0
            elif word_count > 150:
                score -= 1.0
            
            # Check for structured phrases
            structured_phrases = [
                "first", "second", "third", "firstly", "secondly",
                "for example", "specifically", "in other words",
                "to clarify", "that is", "such as"
            ]
            
            structure_count = sum(1 for phrase in structured_phrases if phrase in answer.lower())
            score += min(2.0, structure_count * 0.5)
            
            # Penalize run-on sentences
            sentence_count = answer.count('.') + answer.count('!') + answer.count('?')
            if sentence_count == 0 and word_count > 30:
                score -= 1.5
            
            clarity_scores.append(max(0, min(10, score)))
        
        return statistics.mean(clarity_scores) if clarity_scores else 5.0
    
    def _score_confidence(self, data: Dict) -> float:
        """Score confidence based on behavior and speech (0-10 scale)."""
        gaze_data = data.get("gaze_metrics", {})
        emotion_data = data.get("emotion_metrics", {})
        transcript = data.get("transcript", {})
        
        score = 5.0
        
        # Confident people maintain steady gaze
        gaze_stability = gaze_data.get("summary", {}).get("average_gaze_stability", 0.5)
        score += (gaze_stability - 0.5) * 4  # -2 to +2
        
        # Emotion confidence
        emotion_confidence = emotion_data.get("summary", {}).get("confidence_average", 0.7)
        if emotion_confidence > 0.8:
            score += 1.5
        
        # Dominant emotion
        dominant_emotion = emotion_data.get("summary", {}).get("dominant_emotion", "neutral")
        if dominant_emotion == "confident":
            score += 2.0
        elif dominant_emotion in ["nervous", "surprised"]:
            score -= 1.5
        
        # Response time (confident people respond more quickly)
        qa_pairs = transcript.get("qa_pairs", [])
        if qa_pairs:
            avg_pause = statistics.mean([qa.get("pause_before_answer", 3) for qa in qa_pairs])
            if avg_pause < 2.0:
                score += 1.0
            elif avg_pause > 5.0:
                score -= 1.0
        
        return max(0, min(10, score))
    
    def _calculate_proctoring_penalty(self, data: Dict) -> float:
        """Calculate penalty points from proctoring violations."""
        proctoring = data.get("proctoring_metrics", {})
        violations = proctoring.get("violations", [])
        
        total_penalty = 0.0
        
        for violation in violations:
            violation_type = violation.get("type", "UNKNOWN")
            penalty = self.violation_penalties.get(violation_type, 5)
            total_penalty += penalty
        
        # Additional penalty for excessive looking away
        gaze_data = data.get("gaze_metrics", {})
        eye_contact_pct = gaze_data.get("summary", {}).get("eye_contact_percentage", 50)
        
        if eye_contact_pct < 25:
            total_penalty += self.violation_penalties["EXCESSIVE_LOOK_AWAY"]
        elif eye_contact_pct < 40:
            total_penalty += self.violation_penalties["EXCESSIVE_LOOK_AWAY"] / 2
        
        return total_penalty
    
    def _determine_hire_decision(self, score: float, data: Dict) -> str:
        """Determine hire/maybe/reject decision."""
        proctoring = data.get("proctoring_metrics", {})
        violations = proctoring.get("violations", [])
        
        # Critical violations = automatic reject
        critical_violations = [v for v in violations if v.get("severity") == "CRITICAL"]
        if critical_violations:
            return "Reject"
        
        # Score-based decision
        if score >= 70:
            return "Hire"
        elif score >= 50:
            return "Maybe"
        else:
            return "Reject"
    
    def _analyze_behavior(self, data: Dict) -> Dict:
        """Analyze behavioral metrics."""
        gaze_data = data.get("gaze_metrics", {})
        emotion_data = data.get("emotion_metrics", {})
        
        return {
            "eye_contact_percentage": round(
                gaze_data.get("summary", {}).get("eye_contact_percentage", 0), 2
            ),
            "gaze_stability": round(
                gaze_data.get("summary", {}).get("average_gaze_stability", 0), 2
            ),
            "dominant_emotion": emotion_data.get("summary", {}).get("dominant_emotion", "unknown"),
            "emotion_confidence": round(
                emotion_data.get("summary", {}).get("confidence_average", 0), 2
            ),
            "blink_rate": round(
                gaze_data.get("summary", {}).get("blink_rate_per_minute", 0), 2
            ),
            "head_movement_score": round(
                gaze_data.get("summary", {}).get("head_movement_score", 0), 2
            )
        }
    
    def _summarize_proctoring(self, data: Dict, penalty: float) -> Dict:
        """Summarize proctoring findings."""
        proctoring = data.get("proctoring_metrics", {})
        violations = proctoring.get("violations", [])
        
        return {
            "total_violations": len(violations),
            "violation_types": [v.get("type") for v in violations],
            "total_penalty_points": round(penalty, 2),
            "suspicious_activity_score": round(
                proctoring.get("suspicious_activity_score", 0.0), 2
            ),
            "person_count_average": round(
                proctoring.get("person_count_average", 1.0), 2
            )
        }
    
    def _identify_strengths(self, data: Dict) -> List[str]:
        """Identify candidate strengths."""
        strengths = []
        
        gaze_data = data.get("gaze_metrics", {})
        emotion_data = data.get("emotion_metrics", {})
        
        if gaze_data.get("summary", {}).get("eye_contact_percentage", 0) > 65:
            strengths.append("Excellent eye contact and engagement")
        
        dominant_emotion = emotion_data.get("summary", {}).get("dominant_emotion", "")
        if dominant_emotion in ["confident", "happy"]:
            strengths.append("Positive and confident demeanor")
        
        if not strengths:
            strengths.append("Completed interview without major issues")
        
        return strengths
    
    def _identify_weaknesses(self, data: Dict) -> List[str]:
        """Identify areas for improvement."""
        weaknesses = []
        
        gaze_data = data.get("gaze_metrics", {})
        emotion_data = data.get("emotion_metrics", {})
        proctoring = data.get("proctoring_metrics", {})
        
        if gaze_data.get("summary", {}).get("eye_contact_percentage", 100) < 40:
            weaknesses.append("Poor eye contact - needs improvement")
        
        if proctoring.get("total_violations", 0) > 0:
            weaknesses.append("Proctoring violations detected")
        
        dominant_emotion = emotion_data.get("summary", {}).get("dominant_emotion", "")
        if dominant_emotion == "nervous":
            weaknesses.append("Appeared nervous throughout interview")
        
        if not weaknesses:
            weaknesses.append("No significant weaknesses identified")
        
        return weaknesses
    
    def _generate_recommendation(self, decision: str, score: float, 
                                 data: Dict, penalty: float) -> str:
        """Generate textual recommendation."""
        if decision == "Hire":
            return (
                f"Strong candidate with excellent overall performance (score: {score:.1f}/100). "
                f"Demonstrated good technical knowledge and professional communication. "
                f"Recommend moving forward with hire."
            )
        elif decision == "Maybe":
            rec = f"Moderate candidate (score: {score:.1f}/100). Shows potential but has areas for improvement. "
            if penalty > 0:
                rec += f"Some behavioral/proctoring concerns noted (penalty: -{penalty:.1f} points). "
            rec += "Consider for follow-up interview or alternative position."
            return rec
        else:
            rec = f"Candidate did not meet minimum requirements (score: {score:.1f}/100). "
            if penalty > 10:
                rec += f"Significant proctoring violations noted (penalty: -{penalty:.1f} points). "
            rec += "Not recommended at this time."
            return rec
    
    @staticmethod
    def _save_json(filepath: Path, data: Dict):
        """Save data as JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def score_dataset(self, dataset_dir: Path):
        """Score all sessions in a dataset."""
        sessions_dir = dataset_dir / "sessions" if (dataset_dir / "sessions").exists() else dataset_dir
        
        session_folders = [d for d in sessions_dir.iterdir() if d.is_dir() and d.name.startswith("session_")]
        
        if not session_folders:
            print(f"No sessions found in {sessions_dir}")
            return
        
        print(f"📊 Scoring {len(session_folders)} sessions...")
        
        results = []
        for i, session_dir in enumerate(session_folders):
            try:
                report = self.score_session(session_dir)
                results.append(report)
                
                if (i + 1) % 10 == 0:
                    print(f"  Scored {i + 1}/{len(session_folders)} sessions...")
            except Exception as e:
                print(f"  Error scoring {session_dir.name}: {e}")
        
        # Print summary
        hire_count = sum(1 for r in results if r["hire_decision"] == "Hire")
        maybe_count = sum(1 for r in results if r["hire_decision"] == "Maybe")
        reject_count = sum(1 for r in results if r["hire_decision"] == "Reject")
        
        avg_score = statistics.mean([r["scores"]["overall_score"] for r in results]) if results else 0
        
        print(f"\n✅ Scoring complete!")
        print(f"📈 Results:")
        print(f"   - Hire: {hire_count}")
        print(f"   - Maybe: {maybe_count}")
        print(f"   - Reject: {reject_count}")
        print(f"   - Average score: {avg_score:.2f}/100")


def main():
    """CLI interface for scoring."""
    parser = argparse.ArgumentParser(description="Auto-score interview sessions")
    parser.add_argument("--session-dir", type=str, help="Score single session")
    parser.add_argument("--dataset-dir", type=str, help="Score entire dataset")
    
    args = parser.parse_args()
    
    scorer = AutoScoreGenerator()
    
    if args.session_dir:
        session_path = Path(args.session_dir)
        if session_path.exists():
            report = scorer.score_session(session_path)
            print(f"\n✅ Session scored: {report['hire_decision']} ({report['scores']['overall_score']:.1f}/100)")
        else:
            print(f"Error: Session directory not found: {args.session_dir}")
    
    elif args.dataset_dir:
        dataset_path = Path(args.dataset_dir)
        if dataset_path.exists():
            scorer.score_dataset(dataset_path)
        else:
            print(f"Error: Dataset directory not found: {args.dataset_dir}")
    
    else:
        print("Usage: python auto_score_generator.py --session-dir <path> OR --dataset-dir <path>")


if __name__ == "__main__":
    main()
