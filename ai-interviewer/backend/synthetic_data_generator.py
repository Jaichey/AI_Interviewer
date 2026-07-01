"""
Synthetic Dataset Generator for HireSense AI
Generates realistic interview sessions for testing and development
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import numpy as np


class SyntheticDataGenerator:
    """Generate synthetic interview session data."""
    
    def __init__(self, output_dir: str = "dataset/synthetic"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.roles = [
            "Software Engineer", "Data Scientist", "Frontend Developer",
            "Backend Developer", "Full Stack Developer", "DevOps Engineer",
            "Machine Learning Engineer", "Product Manager", "QA Engineer",
            "System Architect", "Cloud Engineer", "Mobile Developer"
        ]
        
        self.companies = [
            "TechCorp", "InnovateLabs", "DataFlow", "CloudSystems", "AI Ventures",
            "StartupHub", "Enterprise Solutions", "Digital Dynamics", "Code Factory",
            "Future Tech", "Smart Solutions", "Quantum Computing Inc"
        ]
        
        self.subjects = [
            "Python", "JavaScript", "Java", "React", "Node.js", "AWS",
            "Machine Learning", "Data Structures", "System Design", "Docker",
            "Kubernetes", "SQL", "MongoDB", "REST API", "Microservices"
        ]
        
        self.emotions = ["neutral", "happy", "confident", "nervous", "thinking", "surprised"]
        
        self.gaze_directions = ["center", "left", "right", "up", "down"]
        
        # Sample question-answer pairs by category
        self.qa_library = {
            "technical": [
                {
                    "question": "Explain the difference between SQL and NoSQL databases.",
                    "good_answer": "SQL databases are relational and use structured schemas with ACID properties, while NoSQL databases are more flexible, schema-less, and designed for horizontal scaling. SQL is better for complex queries and transactions, NoSQL excels at handling large volumes of unstructured data.",
                    "poor_answer": "SQL has tables, NoSQL doesn't. SQL is old, NoSQL is new."
                },
                {
                    "question": "What is the time complexity of binary search?",
                    "good_answer": "Binary search has O(log n) time complexity because it divides the search space in half with each iteration. It requires a sorted array and is much faster than linear search for large datasets.",
                    "poor_answer": "It's like, pretty fast I think. Better than regular search."
                },
                {
                    "question": "Describe the concept of RESTful APIs.",
                    "good_answer": "REST is an architectural style for distributed systems. It uses HTTP methods (GET, POST, PUT, DELETE) to perform CRUD operations on resources identified by URLs. RESTful APIs are stateless, cacheable, and use standard status codes.",
                    "poor_answer": "It's an API that uses HTTP. You send requests and get responses."
                }
            ],
            "behavioral": [
                {
                    "question": "Tell me about a time you handled a difficult team conflict.",
                    "good_answer": "In my previous role, two team members disagreed on architecture. I organized a meeting where each presented their approach. We evaluated pros and cons objectively, then combined the best elements. This taught me the value of structured conflict resolution.",
                    "poor_answer": "I don't really have conflicts. Everyone usually agrees with me."
                },
                {
                    "question": "How do you handle tight deadlines?",
                    "good_answer": "I prioritize tasks using impact vs effort analysis, communicate transparently with stakeholders about realistic timelines, and break large tasks into manageable chunks. I also maintain code quality even under pressure.",
                    "poor_answer": "I just work faster and skip some testing if needed."
                }
            ],
            "problem_solving": [
                {
                    "question": "Design a URL shortening service like bit.ly.",
                    "good_answer": "I'd use a hash function or base62 encoding to convert long URLs to short codes. Store mappings in a fast key-value store like Redis for quick lookups. For scalability, implement load balancing, caching, and database sharding. Add analytics tracking and expiration policies.",
                    "poor_answer": "Just make the URL shorter and save it somewhere."
                }
            ]
        }
    
    def generate_session(self, session_id: str = None, quality: str = "mixed") -> Dict:
        """
        Generate a complete synthetic interview session.
        
        Args:
            session_id: Optional session ID (generates UUID if not provided)
            quality: 'good', 'poor', or 'mixed' - determines candidate performance
        
        Returns:
            Dictionary with all session data
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Create session directory
        session_dir = self.output_dir / f"session_{session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate metadata
        metadata = self._generate_metadata(session_id, quality)
        
        # Generate transcript
        transcript = self._generate_transcript(quality)
        
        # Generate gaze metrics (aligned with transcript timeline)
        gaze_metrics = self._generate_gaze_metrics(transcript, quality)
        
        # Generate emotion metrics
        emotion_metrics = self._generate_emotion_metrics(transcript, quality)
        
        # Generate proctoring metrics
        proctoring_metrics = self._generate_proctoring_metrics(quality)
        
        # Generate final report
        final_report = self._generate_final_report(
            metadata, transcript, gaze_metrics, 
            emotion_metrics, proctoring_metrics, quality
        )
        
        # Save all files
        self._save_json(session_dir / "video_metadata.json", metadata)
        self._save_json(session_dir / "transcript.json", transcript)
        self._save_json(session_dir / "gaze_metrics.json", gaze_metrics)
        self._save_json(session_dir / "emotion_metrics.json", emotion_metrics)
        self._save_json(session_dir / "proctoring_metrics.json", proctoring_metrics)
        self._save_json(session_dir / "final_report.json", final_report)
        
        return {
            "session_id": session_id,
            "session_dir": str(session_dir),
            "metadata": metadata,
            "final_report": final_report
        }
    
    def generate_dataset(self, num_sessions: int = 100):
        """Generate complete synthetic dataset with multiple sessions."""
        print(f"🤖 Generating {num_sessions} synthetic interview sessions...")
        
        sessions = []
        
        # Distribution: 40% good, 30% mixed, 30% poor
        qualities = (
            ["good"] * int(num_sessions * 0.4) +
            ["mixed"] * int(num_sessions * 0.3) +
            ["poor"] * int(num_sessions * 0.3)
        )
        random.shuffle(qualities)
        
        for i in range(num_sessions):
            quality = qualities[i]
            session = self.generate_session(quality=quality)
            sessions.append(session)
            
            if (i + 1) % 10 == 0:
                print(f"  Generated {i + 1}/{num_sessions} sessions...")
        
        # Generate index file
        index = {
            "generated_at": datetime.now().isoformat(),
            "total_sessions": num_sessions,
            "sessions": [
                {
                    "session_id": s["session_id"],
                    "quality": s["final_report"]["hire_decision"],
                    "overall_score": s["final_report"]["scores"]["overall_score"]
                }
                for s in sessions
            ]
        }
        
        self._save_json(self.output_dir / "index.json", index)
        
        print(f"✅ Dataset generation complete!")
        print(f"📁 Location: {self.output_dir}")
        print(f"📊 Summary:")
        print(f"   - Good candidates: {sum(1 for s in sessions if s['final_report']['hire_decision'] == 'Hire')}")
        print(f"   - Maybe candidates: {sum(1 for s in sessions if s['final_report']['hire_decision'] == 'Maybe')}")
        print(f"   - Poor candidates: {sum(1 for s in sessions if s['final_report']['hire_decision'] == 'Reject')}")
        
        return sessions
    
    def _generate_metadata(self, session_id: str, quality: str) -> Dict:
        """Generate session metadata."""
        start_time = datetime.now() - timedelta(days=random.randint(1, 30))
        duration = random.randint(1200, 2400)  # 20-40 minutes
        
        return {
            "session_id": session_id,
            "candidate_name": f"Candidate_{session_id[:8]}",
            "position": random.choice(self.roles),
            "company": random.choice(self.companies),
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "interview_type": "technical",
            "experience_level": random.choice(["junior", "mid", "senior"]),
            "target_subjects": random.sample(self.subjects, k=random.randint(2, 4))
        }
    
    def _generate_transcript(self, quality: str) -> Dict:
        """Generate interview transcript."""
        num_qa = random.randint(8, 15)
        
        qa_pairs = []
        current_time = 0.0
        
        for i in range(num_qa):
            # Select random category
            category = random.choice(list(self.qa_library.keys()))
            qa_template = random.choice(self.qa_library[category])
            
            # Determine answer quality
            if quality == "good":
                use_good = random.random() > 0.2  # 80% good answers
            elif quality == "poor":
                use_good = random.random() > 0.7  # 30% good answers
            else:  # mixed
                use_good = random.random() > 0.5  # 50% good answers
            
            answer = qa_template["good_answer"] if use_good else qa_template["poor_answer"]
            
            # Add some variation
            if random.random() > 0.7:
                answer = answer + " " + random.choice([
                    "Does that make sense?",
                    "Let me know if you need clarification.",
                    "I hope that answers your question.",
                    "That's based on my experience."
                ])
            
            qa_pair = {
                "question_number": i + 1,
                "timestamp": current_time,
                "category": category,
                "interviewer_question": qa_template["question"],
                "candidate_answer": answer,
                "answer_duration": random.uniform(15, 45),
                "pause_before_answer": random.uniform(1, 5)
            }
            
            qa_pairs.append(qa_pair)
            current_time += qa_pair["pause_before_answer"] + qa_pair["answer_duration"] + random.uniform(5, 10)
        
        return {
            "session_id": "synthetic",
            "total_questions": num_qa,
            "qa_pairs": qa_pairs
        }
    
    def _generate_gaze_metrics(self, transcript: Dict, quality: str) -> Dict:
        """Generate realistic gaze tracking metrics."""
        total_duration = sum(qa["answer_duration"] + qa["pause_before_answer"] for qa in transcript["qa_pairs"])
        
        # Generate frame-by-frame metrics (1 sample per second)
        num_samples = int(total_duration)
        
        frames = []
        for i in range(num_samples):
            # Good candidates maintain better eye contact
            if quality == "good":
                looking_at_camera = random.random() > 0.25  # 75% eye contact
                gaze_dir = "center" if looking_at_camera else random.choice(["left", "right", "up"])
                eye_contact_conf = random.uniform(0.6, 0.95)
            elif quality == "poor":
                looking_at_camera = random.random() > 0.6  # 40% eye contact
                gaze_dir = random.choice(self.gaze_directions)
                eye_contact_conf = random.uniform(0.2, 0.6)
            else:  # mixed
                looking_at_camera = random.random() > 0.45  # 55% eye contact
                gaze_dir = "center" if looking_at_camera else random.choice(["left", "right", "up", "down"])
                eye_contact_conf = random.uniform(0.4, 0.8)
            
            frame = {
                "timestamp": float(i),
                "gaze_direction": gaze_dir,
                "eye_contact_percentage": float(eye_contact_conf * 100),
                "head_pose_yaw": float(random.uniform(-15, 15)),
                "head_pose_pitch": float(random.uniform(-10, 10)),
                "head_pose_roll": float(random.uniform(-5, 5)),
                "blink_detected": random.random() > 0.95,  # ~3 blinks per minute
                "looking_away": not looking_at_camera,
                "look_away_duration": 0.0 if looking_at_camera else random.uniform(0.5, 3.0)
            }
            
            frames.append(frame)
        
        # Calculate summary statistics
        total_eye_contact = sum(1 for f in frames if not f["looking_away"])
        total_look_away_duration = sum(f["look_away_duration"] for f in frames)
        total_blinks = sum(1 for f in frames if f["blink_detected"])
        
        return {
            "total_frames": len(frames),
            "duration_seconds": total_duration,
            "frames": frames,
            "summary": {
                "eye_contact_percentage": (total_eye_contact / len(frames)) * 100 if frames else 0,
                "average_gaze_stability": random.uniform(0.6, 0.9),
                "total_look_away_duration": total_look_away_duration,
                "blink_rate_per_minute": (total_blinks / total_duration) * 60 if total_duration > 0 else 0,
                "head_movement_score": random.uniform(0.5, 0.95)
            }
        }
    
    def _generate_emotion_metrics(self, transcript: Dict, quality: str) -> Dict:
        """Generate realistic emotion detection metrics."""
        total_duration = sum(qa["answer_duration"] + qa["pause_before_answer"] for qa in transcript["qa_pairs"])
        num_samples = int(total_duration / 2)  # Sample every 2 seconds
        
        frames = []
        
        # Emotion distribution based on quality
        if quality == "good":
            emotion_dist = {"confident": 0.4, "neutral": 0.3, "happy": 0.2, "thinking": 0.1}
        elif quality == "poor":
            emotion_dist = {"nervous": 0.4, "neutral": 0.3, "thinking": 0.2, "surprised": 0.1}
        else:
            emotion_dist = {"neutral": 0.4, "confident": 0.2, "thinking": 0.2, "nervous": 0.2}
        
        for i in range(num_samples):
            emotion = random.choices(
                list(emotion_dist.keys()),
                weights=list(emotion_dist.values())
            )[0]
            
            frame = {
                "timestamp": float(i * 2),
                "dominant_emotion": emotion,
                "confidence": random.uniform(0.6, 0.95),
                "emotions": {
                    emo: random.uniform(0.1, 0.9) if emo == emotion else random.uniform(0.0, 0.3)
                    for emo in self.emotions
                }
            }
            
            frames.append(frame)
        
        return {
            "total_frames": len(frames),
            "frames": frames,
            "summary": {
                "dominant_emotion": max(emotion_dist, key=emotion_dist.get),
                "emotion_distribution": emotion_dist,
                "confidence_average": random.uniform(0.7, 0.9)
            }
        }
    
    def _generate_proctoring_metrics(self, quality: str) -> Dict:
        """Generate proctoring violation metrics."""
        
        # Good candidates have fewer violations
        if quality == "good":
            multi_person_count = 0
            phone_detected_count = 0
            excessive_movement = random.randint(0, 2)
        elif quality == "poor":
            multi_person_count = random.randint(0, 2)
            phone_detected_count = random.randint(0, 1)
            excessive_movement = random.randint(2, 5)
        else:
            multi_person_count = random.randint(0, 1)
            phone_detected_count = 0
            excessive_movement = random.randint(1, 3)
        
        violations = []
        
        if multi_person_count > 0:
            for _ in range(multi_person_count):
                violations.append({
                    "timestamp": random.uniform(100, 1500),
                    "type": "MULTIPLE_PERSONS",
                    "severity": "CRITICAL",
                    "description": "Multiple people detected in frame"
                })
        
        if phone_detected_count > 0:
            violations.append({
                "timestamp": random.uniform(100, 1500),
                "type": "PHONE_DETECTED",
                "severity": "HIGH",
                "description": "Phone or device detected"
            })
        
        return {
            "total_violations": len(violations),
            "violations": violations,
            "person_count_average": 1.0 + (multi_person_count * 0.1),
            "suspicious_activity_score": random.uniform(0.0, 0.3) if quality == "good" else random.uniform(0.4, 0.8)
        }
    
    def _generate_final_report(self, metadata: Dict, transcript: Dict, 
                               gaze: Dict, emotion: Dict, proctoring: Dict, quality: str) -> Dict:
        """Generate final interview report with scores."""
        
        # Base scores by quality
        if quality == "good":
            base_tech = random.uniform(7, 10)
            base_comm = random.uniform(7, 9)
            base_clarity = random.uniform(7, 9)
            base_confidence = random.uniform(7, 10)
        elif quality == "poor":
            base_tech = random.uniform(3, 6)
            base_comm = random.uniform(3, 6)
            base_clarity = random.uniform(3, 6)
            base_confidence = random.uniform(3, 6)
        else:
            base_tech = random.uniform(5, 8)
            base_comm = random.uniform(5, 8)
            base_clarity = random.uniform(5, 8)
            base_confidence = random.uniform(5, 8)
        
        # Apply proctoring penalties
        violation_penalty = proctoring["total_violations"] * 5
        eye_contact_bonus = (gaze["summary"]["eye_contact_percentage"] - 50) / 10
        
        technical_score = max(0, min(10, base_tech - violation_penalty * 0.2))
        communication_score = max(0, min(10, base_comm + eye_contact_bonus * 0.1))
        clarity_score = max(0, min(10, base_clarity))
        confidence_score = max(0, min(10, base_confidence + eye_contact_bonus * 0.05))
        
        overall_score = (technical_score * 0.4 + communication_score * 0.25 + 
                        clarity_score * 0.2 + confidence_score * 0.15) * 10
        
        overall_score = max(0, min(100, overall_score - violation_penalty))
        
        # Determine hire decision
        if overall_score >= 70 and proctoring["total_violations"] == 0:
            hire_decision = "Hire"
        elif overall_score >= 50:
            hire_decision = "Maybe"
        else:
            hire_decision = "Reject"
        
        return {
            "session_id": metadata["session_id"],
            "candidate_name": metadata["candidate_name"],
            "position": metadata["position"],
            "timestamp": metadata["timestamp"],
            "scores": {
                "technical_score": round(technical_score, 2),
                "communication_score": round(communication_score, 2),
                "clarity_score": round(clarity_score, 2),
                "confidence_score": round(confidence_score, 2),
                "overall_score": round(overall_score, 2)
            },
            "behavioral_analysis": {
                "eye_contact_percentage": round(gaze["summary"]["eye_contact_percentage"], 2),
                "dominant_emotion": emotion["summary"]["dominant_emotion"],
                "stress_level": "low" if quality == "good" else ("high" if quality == "poor" else "medium"),
                "engagement_score": round(random.uniform(0.6, 0.95), 2)
            },
            "proctoring_summary": {
                "total_violations": proctoring["total_violations"],
                "violation_types": [v["type"] for v in proctoring["violations"]],
                "suspicious_score": round(proctoring["suspicious_activity_score"], 2)
            },
            "hire_decision": hire_decision,
            "recommendation": self._generate_recommendation(hire_decision, overall_score, proctoring)
        }
    
    def _generate_recommendation(self, decision: str, score: float, proctoring: Dict) -> str:
        """Generate textual recommendation."""
        if decision == "Hire":
            return f"Strong candidate with excellent technical skills (score: {score:.1f}/100). Demonstrated good communication and professionalism. Recommend hiring."
        elif decision == "Maybe":
            base = f"Moderate candidate (score: {score:.1f}/100). Shows potential but has areas for improvement. "
            if proctoring["total_violations"] > 0:
                base += "Some proctoring concerns noted. "
            return base + "Consider for follow-up interview."
        else:
            return f"Candidate did not meet minimum requirements (score: {score:.1f}/100). Not recommended at this time."
    
    @staticmethod
    def _save_json(filepath: Path, data: Dict):
        """Save data as JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    """CLI interface for synthetic data generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic interview dataset")
    parser.add_argument("--num-sessions", type=int, default=100, help="Number of sessions to generate")
    parser.add_argument("--output-dir", type=str, default="dataset/synthetic", help="Output directory")
    
    args = parser.parse_args()
    
    generator = SyntheticDataGenerator(output_dir=args.output_dir)
    generator.generate_dataset(num_sessions=args.num_sessions)


if __name__ == "__main__":
    main()
