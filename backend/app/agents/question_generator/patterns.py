"""Question pattern banks — each pattern uses a distinct interview question shape."""

from __future__ import annotations

from app.models.enums import InterviewCategory, InterviewDifficulty

# Pattern ids used per slot so questions do not all read as "How would you…"
DSA_PATTERNS_BEGINNER = [
    "coding_walkthrough",
    "concept_explain",
    "compare_structures",
    "debug_scenario",
    "trace_example",
    "tradeoff_choice",
    "real_world_apply",
    "estimation",
]

DSA_PATTERNS_INTERMEDIATE = DSA_PATTERNS_BEGINNER + [
    "complexity_deep_dive",
    "optimization_challenge",
]

DSA_PATTERNS_ADVANCED = DSA_PATTERNS_INTERMEDIATE + [
    "system_scale",
    "design_algorithm",
]

TECHNICAL_PATTERNS = [
    "system_design",
    "api_contract",
    "debug_scenario",
    "tradeoff_choice",
    "security_review",
    "testing_strategy",
    "observability",
    "real_world_apply",
]

BEHAVIORAL_PATTERNS = [
    "star_story",
    "situational",
    "conflict_resolution",
    "leadership",
    "failure_lesson",
    "feedback",
    "prioritization",
]

HR_PATTERNS = [
    "motivation",
    "culture_fit",
    "career_goals",
    "strengths_gaps",
    "self_awareness",
]

RESUME_PATTERNS = [
    "deep_dive",
    "metrics_impact",
    "redo_decision",
    "teach_back",
    "stakeholder",
    "tradeoff_choice",
]

MIXED_PATTERNS = [
    "coding_walkthrough",
    "star_story",
    "motivation",
    "system_design",
    "deep_dive",
    "debug_scenario",
    "compare_structures",
    "situational",
]

# Each pattern only applies to its interview category (strict wizard selection).
_PATTERN_CATEGORY: dict[str, frozenset[InterviewCategory]] = {}
_all_dsa = set(DSA_PATTERNS_BEGINNER) | set(DSA_PATTERNS_INTERMEDIATE) | set(DSA_PATTERNS_ADVANCED)
for _p in _all_dsa:
    _PATTERN_CATEGORY[_p] = frozenset({InterviewCategory.DSA, InterviewCategory.MIXED})
for _p in TECHNICAL_PATTERNS:
    _PATTERN_CATEGORY[_p] = frozenset({InterviewCategory.TECHNICAL, InterviewCategory.MIXED})
for _p in BEHAVIORAL_PATTERNS:
    _PATTERN_CATEGORY[_p] = frozenset({InterviewCategory.BEHAVIORAL, InterviewCategory.MIXED})
for _p in HR_PATTERNS:
    _PATTERN_CATEGORY[_p] = frozenset({InterviewCategory.HR, InterviewCategory.MIXED})
for _p in RESUME_PATTERNS:
    _PATTERN_CATEGORY[_p] = frozenset({InterviewCategory.RESUME_BASED, InterviewCategory.MIXED})


def pattern_allowed_for_category(pattern: str, category: InterviewCategory) -> bool:
    allowed = _PATTERN_CATEGORY.get(pattern)
    if allowed is None:
        return category == InterviewCategory.MIXED
    return category in allowed


def patterns_for_session(
    category: InterviewCategory,
    difficulty: InterviewDifficulty,
) -> list[str]:
    if category == InterviewCategory.DSA:
        if difficulty == InterviewDifficulty.ADVANCED:
            return list(DSA_PATTERNS_ADVANCED)
        if difficulty == InterviewDifficulty.INTERMEDIATE:
            return list(DSA_PATTERNS_INTERMEDIATE)
        return list(DSA_PATTERNS_BEGINNER)
    if category == InterviewCategory.TECHNICAL:
        return list(TECHNICAL_PATTERNS)
    if category == InterviewCategory.BEHAVIORAL:
        return list(BEHAVIORAL_PATTERNS)
    if category == InterviewCategory.HR:
        return list(HR_PATTERNS)
    if category == InterviewCategory.RESUME_BASED:
        return list(RESUME_PATTERNS)
    return list(MIXED_PATTERNS)


def templates_for_pattern(
    pattern: str,
    category: InterviewCategory,
    difficulty: InterviewDifficulty,
    *,
    has_anchor: bool,
    has_weak: bool,
    resume_source: str | None = None,
) -> list[str]:
    """Return question templates for one pattern (distinct shape from other patterns)."""
    if not pattern_allowed_for_category(pattern, category):
        return []

    role = "{role}"
    anchor = "{anchor}"
    skill = "{skill}"
    weak = "{weak}"
    name = "{name}"

    # Resume-based: tailor wording to the resume section (not only projects).
    if category == InterviewCategory.RESUME_BASED and resume_source:
        section_templates = _resume_section_templates(pattern, resume_source, difficulty)
        if section_templates:
            return section_templates

    # --- DSA / algorithmic patterns ---
    if pattern == "coding_walkthrough":
        return [
            f"Given an unsorted array of integers, how would you find all pairs that sum to a target? Talk through your approach step by step.",
            f"Walk me through how you would detect a cycle in a linked list. What would you write on the whiteboard first?",
            f"Suppose you must group anagrams from a list of strings. Describe your algorithm before optimizing.",
        ]

    if pattern == "concept_explain":
        return [
            f"Explain recursion vs iteration to a junior {role}. Use a simple example, not jargon.",
            f"What is the difference between mutable and immutable data structures? When does it matter for a {role}?",
            f"In plain language, explain Big-O notation and why interviewers care about it for this role.",
        ]

    if pattern == "compare_structures":
        return [
            f"Compare using a hash map versus a binary search tree for fast lookups. When would you regret each choice?",
            f"Stack vs queue: give two real situations where picking the wrong one causes bugs.",
            f"BFS vs DFS — pick one for exploring a social graph feed and defend your choice.",
        ]

    if pattern == "debug_scenario":
        if has_anchor:
            return [
                f"After shipping {anchor}, users report intermittent wrong counts in the UI. How do you isolate the bug?",
                f"Production logs show timeouts only on Mondays for {anchor}. Walk through your investigation.",
            ]
        return [
            f"A {role} sees memory climbing after each navigation in a SPA. Outline your debugging plan in order.",
            f"Tests pass locally but fail in CI for a sorting utility. What do you check first, second, third?",
        ]

    if pattern == "trace_example":
        return [
            "Trace this by hand: input [2,7,11,15], target 9 — which indices do you return with a one-pass hash approach?",
            "On paper, walk through binary search on [1,3,5,7,9] looking for 6. Where does it stop and why?",
            f"Dry-run a queue-based level-order traversal on a small tree. State the output order.",
        ]

    if pattern == "tradeoff_choice":
        return [
            f"Would you ship {anchor} with client-side caching or server-side caching? Argue both sides, then pick one.",
            f"For a {role} MVP: optimize for delivery speed or code perfection? What do you sacrifice either way?",
            f"Choose: O(n) extra memory for O(1) lookups, or O(1) memory with O(n) scans. When is each acceptable?",
        ]

    if pattern == "real_world_apply":
        if has_anchor:
            return [
                f"Your PM asks for type-ahead search on {anchor} with <100ms feel. Sketch the data flow.",
                f"Debounce vs throttle for {anchor}: which do you use for scroll vs search, and why?",
            ]
        return [
            f"Design autocomplete for a {role} portfolio site: what structures and events do you need?",
            f"How would you implement undo/redo in a form editor? Name the core data structure.",
        ]

    if pattern == "estimation":
        return [
            f"Estimate how many API calls a busy {role} dashboard might make per session. Show your reasoning.",
            "Roughly how much memory might 10,000 DOM nodes use? Is that a problem? How would you verify?",
            f"If each user action triggers 3 re-renders, how would you measure and reduce that?",
        ]

    if pattern == "complexity_deep_dive":
        return [
            f"You sort 1M records for {anchor}. Compare merge sort, quicksort, and radix sort here.",
            f"What breaks if you use a nested loop on 50k items in {anchor}? Propose a better bound.",
        ]

    if pattern == "optimization_challenge":
        return [
            f"Your solution for {anchor} is O(n²). How do you get to O(n log n) or O(n) without losing correctness?",
            f"Can you solve two-sum in one pass? What invariant does your pointer or hash strategy maintain?",
        ]

    if pattern == "system_scale":
        return [
            f"How would you shard data if {anchor} outgrows a single Postgres instance?",
            f"Design a rate limiter for public APIs behind {anchor}. Token bucket or sliding window?",
        ]

    if pattern == "design_algorithm":
        return [
            f"Design an LRU cache for {anchor}. What operations must be O(1)?",
            f"Build a scheduler that picks the next job for {anchor}. Heap, queue, or something else?",
        ]

    # --- Technical / system patterns ---
    if pattern == "system_design":
        return [
            f"Sketch a high-level architecture for {anchor} as a {role}. Boxes and arrows are fine.",
            f"How would you split {anchor} into services if the team doubles next quarter?",
        ]

    if pattern == "api_contract":
        return [
            f"Define the REST contract for creating and listing resources in {anchor}. Status codes and errors included.",
            f"What versioning strategy would you use for APIs consumed by {anchor}?",
        ]

    if pattern == "security_review":
        return [
            f"What are the top three security risks in {anchor} and how would you mitigate them?",
            f"How do you store tokens and secrets when building features like {anchor}?",
        ]

    if pattern == "testing_strategy":
        return [
            f"What test pyramid would you use for {anchor}? Unit, integration, E2E — give examples.",
            f"How do you test async UI flows in {anchor} without flaky CI?",
        ]

    if pattern == "observability":
        return [
            f"What metrics, logs, and traces would you add on day one for {anchor}?",
            f"An alert fires: p95 latency doubled on {anchor}. What dashboards do you open first?",
        ]

    # --- Behavioral patterns ---
    if pattern == "star_story":
        return [
            f"Tell me about a time you delivered under a tight deadline as a {role}. Situation, task, action, result.",
            f"Describe a project where you exceeded expectations. What did you do differently?",
        ]

    if pattern == "situational":
        return [
            f"If two senior engineers disagree on the approach for {anchor}, what do you do?",
            f"You join a team mid-sprint as {role}. How do you ramp up without blocking others?",
        ]

    if pattern == "conflict_resolution":
        return [
            f"Describe a disagreement about technical quality on {anchor}. How was it resolved?",
            "Tell me about a time you had to say no to a stakeholder. What happened?",
        ]

    if pattern == "leadership":
        return [
            f"Give an example of mentoring someone while working on {anchor}.",
            f"When did you unblock others on a {role} team without being the official lead?",
        ]

    if pattern == "failure_lesson":
        return [
            f"Tell me about a bug or outage related to {anchor}. What did you learn?",
            f"Describe a decision you would reverse on {anchor} and what you would do instead.",
        ]

    if pattern == "feedback":
        return [
            f"Share a time you received harsh code review feedback on {anchor}. How did you respond?",
            f"How do you ask for feedback as a {role} when you are unsure about your approach?",
        ]

    if pattern == "prioritization":
        return [
            f"You can only ship one of: performance, accessibility, or new features for {anchor}. Choose and justify.",
            "Your backlog has 20 items and one week. How do you prioritize?",
        ]

    # --- HR patterns ---
    if pattern == "motivation":
        return [
            f"Why this company and this {role} — what specifically excites you?",
            f"What would make you choose this {role} over another offer?",
        ]

    if pattern == "culture_fit":
        return [
            f"What kind of team environment helps you do your best work as a {role}?",
            "How do you prefer to receive direction — and give it to peers?",
        ]

    if pattern == "career_goals":
        return [
            f"Where do you want your career to be in three years after this {role}?",
            f"What skills are you deliberately building toward your next step after {role}?",
        ]

    if pattern == "strengths_gaps":
        return [
            f"What is your strongest skill for this {role}, with evidence?",
            f"What gap are you actively closing before starting as {role}?",
        ]

    if pattern == "self_awareness":
        return [
            f"What type of work drains you, and how do you stay effective as a {role}?",
            f"How do colleagues describe your working style?",
        ]

    # --- Resume-based patterns ---
    if pattern == "deep_dive":
        return [
            f"Walk me through {anchor} end-to-end as if I am the hiring manager for {role}.",
            f"What was the hardest technical decision on {anchor}?",
        ]

    if pattern == "metrics_impact":
        return [
            f"What measurable impact did you have on {anchor}? Numbers matter.",
            f"If {anchor} disappeared tomorrow, what business metric would suffer?",
        ]

    if pattern == "redo_decision":
        return [
            f"If you rebuilt {anchor} today, what would you not repeat?",
            f"What one library or pattern would you drop from {anchor} and why?",
        ]

    if pattern == "teach_back":
        return [
            f"Teach me how {skill} was used in {anchor} as if I am new to the stack.",
            f"Explain {anchor} to a product manager in two minutes.",
        ]

    if pattern == "stakeholder":
        return [
            f"How did non-engineers collaborate with you on {anchor}?",
            f"Tell me about pushing back on scope for {anchor}.",
        ]

    return [
        f"As a {role}, walk me through how you would approach work related to {anchor}.",
        f"What is one strong opinion you hold about best practices for a {role}?",
    ]


def _resume_section_templates(
    pattern: str,
    resume_source: str,
    difficulty: InterviewDifficulty,
) -> list[str]:
    """Questions tied to a specific resume section (experience, skills, etc.)."""
    anchor = "{anchor}"
    role = "{role}"
    skill = "{skill}"

    if resume_source == "experience":
        if pattern == "deep_dive":
            return [
                f"Walk me through your role at {anchor}. What were you hired to do versus what you actually delivered?",
                f"On {anchor}: what was your biggest measurable result, and how did you prove it?",
            ]
        if pattern == "metrics_impact":
            return [
                f"From your time at {anchor}, which KPI moved the most and what did you do to move it?",
                f"What would your manager at {anchor} say was your top contribution?",
            ]
        if pattern == "stakeholder":
            return [
                f"How did you work with non-technical stakeholders during {anchor}?",
            ]
        return [
            f"Why is {anchor} on your resume for a {role} role — what should I remember from it?",
        ]

    if resume_source == "skill":
        if pattern == "teach_back":
            return [
                f"You list {anchor}. Explain it as if I have never used it, then give a work example.",
                f"Where has {anchor} saved you time or prevented bugs in production?",
            ]
        return [
            f"How have you applied {anchor} in a real {role} task? Be specific about context and outcome.",
            f"What is a common mistake juniors make with {anchor}, and how do you avoid it?",
        ]

    if resume_source == "education":
        return [
            f"How does {anchor} prepare you for this {role} interview today?",
            f"What from {anchor} do you still use daily versus what was mostly theoretical?",
        ]

    if resume_source == "certification":
        return [
            f"You earned {anchor}. What practical skill did you gain that shows up on the job?",
            f"Why did you pursue {anchor}, and how does it support your {role} goals?",
        ]

    if resume_source == "achievement":
        return [
            f"Tell me about {anchor}. What was your personal contribution versus the team's?",
            f"How would you defend {anchor} if an interviewer thought it was inflated?",
        ]

    if resume_source == "internship":
        return [
            f"During {anchor}, what ownership did you have end-to-end?",
            f"What would you do differently if you repeated {anchor} as a full-time {role}?",
        ]

    # project (default)
    if pattern == "deep_dive":
        return [
            f"Walk me through project {anchor} end-to-end as if I am the hiring manager for {role}.",
            f"What was the hardest technical decision on {anchor}, and what alternatives did you reject?",
        ]
    if pattern == "metrics_impact":
        return [
            f"What measurable impact did you have on {anchor}? Numbers and timelines matter.",
            f"If {anchor} went offline for a day, what business or user impact would you expect?",
        ]
    if pattern == "redo_decision":
        return [
            f"If you rebuilt {anchor} today, what would you not repeat?",
            f"What technical debt from {anchor} still bothers you?",
        ]
    if pattern == "teach_back":
        return [
            f"Teach me {anchor} in two minutes: problem, your approach, and outcome.",
        ]
    if pattern == "stakeholder":
        return [
            f"Who were the stakeholders for {anchor}, and how did you align them?",
        ]
    if pattern == "tradeoff_choice":
        return [
            f"What trade-off on {anchor} kept you up at night — speed, quality, or scope?",
        ]
    return [
        f"On your project {anchor}: what was your specific contribution, and what metrics proved impact?",
        f"How does {anchor} demonstrate readiness for {role}?",
    ]
