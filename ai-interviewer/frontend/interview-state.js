/**
 * Interview State Management
 * Centralized state for mode, subject, company, and avatar control
 */

export class InterviewState {
  constructor() {
    this.mode = 'individual'; // 'individual' or 'multi'
    this.subject = ''; // DAA, OS, CN, SE, WEB, DBMS, OOPS, SYSTEM_DESIGN
    this.company = ''; // Google, Amazon, Meta, Microsoft, Apple, Netflix, Startup
    this.activeAvatarIndex = 0;
    this.avatarCount = 1; // 1 for individual, up to 3 for multi
    this.isInterviewActive = false;
    this.questionCount = 0;
  }

  setMode(mode) {
    if (mode === 'individual' || mode === 'multi') {
      this.mode = mode;
      this.avatarCount = mode === 'multi' ? 3 : 1;
      this.activeAvatarIndex = 0;
      return true;
    }
    return false;
  }

  setSubject(subject) {
    const validSubjects = ['DAA', 'OS', 'CN', 'SE', 'WEB', 'DBMS', 'OOPS', 'SYSTEM_DESIGN'];
    if (validSubjects.includes(subject)) {
      this.subject = subject;
      return true;
    }
    return false;
  }

  setCompany(company) {
    const validCompanies = ['Google', 'Amazon', 'Meta', 'Microsoft', 'Apple', 'Netflix', 'Startup'];
    if (validCompanies.includes(company)) {
      this.company = company;
      return true;
    }
    return false;
  }

  nextAvatar() {
    if (this.mode === 'multi') {
      this.activeAvatarIndex = (this.activeAvatarIndex + 1) % this.avatarCount;
    }
    return this.activeAvatarIndex;
  }

  startInterview() {
    this.isInterviewActive = true;
    this.questionCount = 0;
  }

  endInterview() {
    this.isInterviewActive = false;
  }

  isValid() {
    return this.mode && this.subject && this.company;
  }

  getMissingFields() {
    const missing = [];
    if (!this.mode) missing.push('Mode');
    if (!this.subject) missing.push('Subject');
    if (!this.company) missing.push('Company');
    return missing;
  }

  reset() {
    this.activeAvatarIndex = 0;
    this.questionCount = 0;
    this.isInterviewActive = false;
  }
}

/**
 * Question Bank - Subject and Company specific
 */
export class QuestionBank {
  constructor() {
    this.questions = {
      DAA: {
        easy: [
          "Explain time and space complexity with examples.",
          "What is Big O notation and why is it important?",
          "How do you optimize a brute force solution?"
        ],
        medium: [
          "Design an algorithm to find the kth largest element in an array.",
          "Explain the difference between quicksort and mergesort.",
          "How would you approach solving a dynamic programming problem?"
        ],
        hard: [
          "Solve a complex system design problem with optimization constraints.",
          "How would you handle edge cases in a graph algorithm?"
        ]
      },
      OS: {
        easy: [
          "What is the difference between a process and a thread?",
          "Explain process scheduling and context switching.",
          "What is virtual memory?"
        ],
        medium: [
          "Explain the banker's algorithm for deadlock avoidance.",
          "How does page replacement work in memory management?",
          "What is a semaphore and how is it used?"
        ],
        hard: [
          "Design a memory management system with minimal fragmentation.",
          "How would you optimize CPU scheduling for different workloads?"
        ]
      },
      CN: {
        easy: [
          "Explain the OSI model and its layers.",
          "What is the difference between TCP and UDP?",
          "How does DNS work?"
        ],
        medium: [
          "Explain how routing protocols work (BGP, OSPF).",
          "What are the differences between IPv4 and IPv6?",
          "How does congestion control work in TCP?"
        ],
        hard: [
          "Design a protocol for reliable message delivery in unreliable networks.",
          "How would you optimize network performance for high-latency connections?"
        ]
      },
      SE: {
        easy: [
          "What is SDLC and its phases?",
          "Explain the difference between Waterfall and Agile.",
          "What is a design pattern?"
        ],
        medium: [
          "How would you design a testing strategy for an application?",
          "Explain SOLID principles.",
          "What is code refactoring and when is it necessary?"
        ],
        hard: [
          "Design a microservices architecture for a large-scale application.",
          "How would you handle technical debt in a legacy system?"
        ]
      },
      WEB: {
        easy: [
          "Explain the difference between HTML, CSS, and JavaScript.",
          "What is responsive design?",
          "How do you optimize website performance?"
        ],
        medium: [
          "Explain how React's virtual DOM works.",
          "What is REST API and how do you design one?",
          "How do you handle state management in a web application?"
        ],
        hard: [
          "Design a scalable web application architecture.",
          "How would you implement real-time features in a web app?"
        ]
      },
      DBMS: {
        easy: [
          "What is normalization and why is it important?",
          "Explain the difference between RDBMS and NoSQL.",
          "What is an index and how does it improve performance?"
        ],
        medium: [
          "Explain ACID properties.",
          "How do you design efficient database schemas?",
          "What are transactions and how do they work?"
        ],
        hard: [
          "Design a database for high-concurrency scenarios.",
          "How would you implement sharding in a distributed database?"
        ]
      },
      OOPS: {
        easy: [
          "Explain the four pillars of OOP.",
          "What is inheritance and how does it work?",
          "What is polymorphism?"
        ],
        medium: [
          "Explain the difference between abstract classes and interfaces.",
          "What is encapsulation and why is it important?",
          "How do you implement the observer pattern?"
        ],
        hard: [
          "Design a complex class hierarchy with proper OOP principles.",
          "How would you implement design patterns in real-world scenarios?"
        ]
      },
      SYSTEM_DESIGN: {
        easy: [
          "What are the key considerations in system design?",
          "Explain horizontal vs vertical scaling.",
          "What is load balancing?"
        ],
        medium: [
          "Design a URL shortening service.",
          "How would you design a real-time notification system?",
          "Explain caching strategies and when to use them."
        ],
        hard: [
          "Design a globally distributed system with consistency requirements.",
          "How would you design a system handling millions of requests per second?"
        ]
      }
    };
  }

  getDifficulty(company) {
    const difficulties = {
      Google: 'hard',
      Amazon: 'hard',
      Meta: 'medium',
      Microsoft: 'medium',
      Apple: 'hard',
      Netflix: 'medium',
      Startup: 'easy'
    };
    return difficulties[company] || 'medium';
  }

  getNextQuestion(subject, company) {
    if (!this.questions[subject]) {
      return "Tell me about your experience with this technology.";
    }

    const difficulty = this.getDifficulty(company);
    const questionsForDifficulty = this.questions[subject][difficulty] || 
                                   this.questions[subject]['medium'];
    
    // Rotate through questions
    const index = Math.floor(Math.random() * questionsForDifficulty.length);
    return questionsForDifficulty[index];
  }
}

/**
 * Company-aware behavior configuration
 */
export const COMPANY_BEHAVIORS = {
  Google: {
    tone: 'analytical',
    emphasis: 'problem-solving and optimization',
    followUp: true,
    whiteboarding: true
  },
  Amazon: {
    tone: 'practical',
    emphasis: 'leadership principles and scalability',
    followUp: true,
    whiteboarding: true
  },
  Meta: {
    tone: 'conversational',
    emphasis: 'product and practical implementation',
    followUp: true,
    whiteboarding: false
  },
  Microsoft: {
    tone: 'structured',
    emphasis: 'design and implementation details',
    followUp: true,
    whiteboarding: true
  },
  Apple: {
    tone: 'detailed',
    emphasis: 'quality and attention to detail',
    followUp: true,
    whiteboarding: false
  },
  Netflix: {
    tone: 'pragmatic',
    emphasis: 'performance and user experience',
    followUp: false,
    whiteboarding: false
  },
  Startup: {
    tone: 'friendly',
    emphasis: 'learning and flexibility',
    followUp: true,
    whiteboarding: true
  }
};
