"""Static reference data for local/demo seeding.

Question wording is behavioural, not diagnostic. High agreement on an
item contributes to the named category score during feature engineering.
"""

from app.models.enums import PersonalityCode

DISCLAIMER = (
    "This assessment is intended for educational, research and "
    "personal-development purposes and should not be considered a "
    "clinical psychological diagnosis."
)

PERSONALITY_TYPES = [
    {
        "code": PersonalityCode.CHOLERIC.value,
        "name": "Choleric",
        "tagline": "Direct, decisive, and oriented toward goals.",
        "description": (
            "An assessment pattern in the Choleric range often indicates a "
            "preference for taking initiative, setting direction, and moving "
            "quickly from decision to action. This is a description of "
            "tendencies, not a fixed identity."
        ),
        "characteristics": [
            "decisive",
            "goal-oriented",
            "independent",
            "assertive",
            "confident",
            "leadership-focused",
        ],
        "strengths": [
            "Comfortable making timely decisions",
            "Keeps groups moving toward a stated goal",
            "Willing to take responsibility for outcomes",
        ],
        "development_areas": [
            "May benefit from pausing to hear other viewpoints",
            "Can practise patience when progress is incremental",
            "May need to soften delivery when giving direction",
        ],
        "communication_style": (
            "Tends to be concise and task-focused. Others may experience this "
            "as clarity, or as abruptness if pace is high."
        ),
        "work_style": (
            "Often prefers ownership, visible progress, and environments "
            "where decisions can be made without lengthy delay."
        ),
        "career_environments": (
            "Settings that reward initiative — for example operations, "
            "project leadership, entrepreneurship, or roles with clear "
            "accountability. These are possible fits, not prescriptions."
        ),
        "development_suggestions": (
            "Build in a short consultation step before high-impact decisions, "
            "and practise naming the contribution of quieter colleagues."
        ),
        "disclaimer": DISCLAIMER,
    },
    {
        "code": PersonalityCode.MELANCHOLIC.value,
        "name": "Melancholic",
        "tagline": "Thoughtful, organised, and attentive to quality.",
        "description": (
            "An assessment pattern in the Melancholic range often indicates "
            "a preference for analysis, planning, and careful standards. "
            "Sensitivity here means noticing detail and risk, not a clinical "
            "mood diagnosis."
        ),
        "characteristics": [
            "analytical",
            "thoughtful",
            "detail-oriented",
            "organised",
            "sensitive",
            "perfection-oriented",
        ],
        "strengths": [
            "Notices inconsistencies others may miss",
            "Plans work in a structured way",
            "Holds a high bar for quality",
        ],
        "development_areas": [
            "May delay action while seeking a more complete picture",
            "Can be self-critical when results are imperfect",
            "May benefit from sharing work before it feels finished",
        ],
        "communication_style": (
            "Tends to be precise and considered. Others may experience this "
            "as thoroughness, or as caution if every detail is discussed."
        ),
        "work_style": (
            "Often prefers clear standards, time to prepare, and roles where "
            "accuracy matters."
        ),
        "career_environments": (
            "Settings that value analysis and quality — for example research, "
            "finance, quality assurance, design, or documentation-heavy work. "
            "These are possible fits, not prescriptions."
        ),
        "development_suggestions": (
            "Agree a 'good enough' checkpoint in advance, and schedule "
            "recovery time after intense review work."
        ),
        "disclaimer": DISCLAIMER,
    },
    {
        "code": PersonalityCode.PHLEGMATIC.value,
        "name": "Phlegmatic",
        "tagline": "Calm, dependable, and steady in a group.",
        "description": (
            "An assessment pattern in the Phlegmatic range often indicates "
            "a preference for harmony, patience, and reliable follow-through. "
            "This describes a working style, not a lack of ambition."
        ),
        "characteristics": [
            "calm",
            "patient",
            "dependable",
            "peaceful",
            "supportive",
            "cooperative",
        ],
        "strengths": [
            "Stabilises a team when pressure rises",
            "Follows through on commitments",
            "Makes space for other people to contribute",
        ],
        "development_areas": [
            "May postpone difficult conversations",
            "Can be overlooked if they do not self-advocate",
            "May benefit from stating a preference more explicitly",
        ],
        "communication_style": (
            "Tends to be measured and diplomatic. Others may experience this "
            "as calm, or as reserve if opinions are held back."
        ),
        "work_style": (
            "Often prefers predictable processes, collaborative roles, and "
            "time to adapt when change is introduced."
        ),
        "career_environments": (
            "Settings that reward reliability and support — for example "
            "operations support, counselling-adjacent roles, administration, "
            "or team coordination. These are possible fits, not prescriptions."
        ),
        "development_suggestions": (
            "Practise stating one clear preference in meetings, and diary a "
            "follow-up when a conflict is deferred."
        ),
        "disclaimer": DISCLAIMER,
    },
    {
        "code": PersonalityCode.SANGUINE.value,
        "name": "Sanguine",
        "tagline": "Outgoing, expressive, and energised by people.",
        "description": (
            "An assessment pattern in the Sanguine range often indicates "
            "a preference for social interaction, variety, and optimistic "
            "framing. Energy here is a tendency, not a requirement to be "
            "outgoing in every setting."
        ),
        "characteristics": [
            "outgoing",
            "expressive",
            "enthusiastic",
            "energetic",
            "social",
            "optimistic",
        ],
        "strengths": [
            "Builds rapport quickly",
            "Brings energy to group work",
            "Helps others see possibilities",
        ],
        "development_areas": [
            "May start more tasks than can be finished in one sitting",
            "Can underestimate how long detailed work will take",
            "May benefit from written follow-up after verbal agreements",
        ],
        "communication_style": (
            "Tends to be expressive and informal. Others may experience this "
            "as warmth, or as a fast pace if they need more processing time."
        ),
        "work_style": (
            "Often prefers variety, visible collaboration, and roles with "
            "frequent human contact."
        ),
        "career_environments": (
            "Settings that reward sociability — for example education, "
            "sales, facilitation, communications, or community-facing work. "
            "These are possible fits, not prescriptions."
        ),
        "development_suggestions": (
            "Capture actions in writing after conversations, and protect a "
            "short block of uninterrupted time for detail work."
        ),
        "disclaimer": DISCLAIMER,
    },
]

QUESTION_CATEGORIES = [
    ("leadership", "Leadership", "Willingness to guide a group toward a goal."),
    ("sociability", "Sociability", "Comfort with social interaction and new people."),
    ("assertiveness", "Assertiveness", "Ease in stating a position and holding a boundary."),
    (
        "emotional_sensitivity",
        "Emotional sensitivity",
        "Noticing emotional cues in oneself and others.",
    ),
    ("organisation", "Organisation", "Preference for planning, order, and structure."),
    ("decision_making", "Decision making", "Comfort reaching a conclusion with available information."),
    ("patience", "Patience", "Ability to stay steady when progress is slow."),
    ("adaptability", "Adaptability", "Ease in adjusting when circumstances change."),
    ("communication", "Communication", "Preference for expressing ideas and keeping others informed."),
    ("risk_taking", "Risk taking", "Willingness to act under uncertainty."),
    ("conflict_handling", "Conflict handling", "Approach to disagreement and tension."),
    ("teamwork", "Teamwork", "Preference for shared effort over solo work."),
    ("independence", "Independence", "Comfort working with limited supervision."),
    (
        "attention_to_detail",
        "Attention to detail",
        "Tendency to notice and correct small errors.",
    ),
    ("optimism", "Optimism", "Tendency to interpret events in a hopeful frame."),
    (
        "emotional_expression",
        "Emotional expression",
        "Comfort showing feeling in words or manner.",
    ),
]

# (category_code, personality_code, reverse_scored, question_text)
QUESTIONS = [
    (
        "leadership",
        "CHOLERIC",
        False,
        "I am comfortable taking charge when a group needs direction.",
    ),
    (
        "leadership",
        "CHOLERIC",
        False,
        "I step forward to organise people when a task has no clear owner.",
    ),
    (
        "sociability",
        "SANGUINE",
        False,
        "I enjoy meeting new people in work or study settings.",
    ),
    (
        "sociability",
        "SANGUINE",
        False,
        "I gain energy from group conversation rather than long stretches alone.",
    ),
    (
        "assertiveness",
        "CHOLERIC",
        False,
        "I state my view clearly even when others may disagree.",
    ),
    (
        "assertiveness",
        "CHOLERIC",
        True,
        "I usually stay quiet rather than risk a difference of opinion.",
    ),
    (
        "emotional_sensitivity",
        "MELANCHOLIC",
        False,
        "I notice small changes in other people's mood or tone.",
    ),
    (
        "emotional_sensitivity",
        "MELANCHOLIC",
        False,
        "Criticism stays with me for a while after a conversation ends.",
    ),
    (
        "organisation",
        "MELANCHOLIC",
        False,
        "I prefer to plan my work before I begin a substantial task.",
    ),
    (
        "organisation",
        "MELANCHOLIC",
        False,
        "I keep my notes, files, or workspace in a consistent order.",
    ),
    (
        "decision_making",
        "CHOLERIC",
        False,
        "I can choose a course of action even when some details are still unknown.",
    ),
    (
        "decision_making",
        "MELANCHOLIC",
        True,
        "I delay decisions until I have gathered as much information as possible.",
    ),
    (
        "patience",
        "PHLEGMATIC",
        False,
        "I stay calm when a task takes longer than I expected.",
    ),
    (
        "patience",
        "PHLEGMATIC",
        False,
        "I can wait for others to finish speaking before I respond.",
    ),
    (
        "adaptability",
        "SANGUINE",
        False,
        "I adjust reasonably well when plans change at short notice.",
    ),
    (
        "adaptability",
        "PHLEGMATIC",
        False,
        "I can continue working steadily after a disruption to my routine.",
    ),
    (
        "communication",
        "SANGUINE",
        False,
        "I find it easy to explain my ideas out loud to a group.",
    ),
    (
        "communication",
        "SANGUINE",
        False,
        "I keep other people informed about progress without being asked.",
    ),
    (
        "risk_taking",
        "CHOLERIC",
        False,
        "I am willing to try an approach that has no guaranteed outcome.",
    ),
    (
        "risk_taking",
        "MELANCHOLIC",
        True,
        "I prefer a familiar method even when a new option might be faster.",
    ),
    (
        "conflict_handling",
        "PHLEGMATIC",
        False,
        "I look for a compromise when people around me disagree.",
    ),
    (
        "conflict_handling",
        "CHOLERIC",
        False,
        "I address a problem directly rather than hoping it will pass.",
    ),
    (
        "teamwork",
        "PHLEGMATIC",
        False,
        "I work well when success depends on the group, not only on me.",
    ),
    (
        "teamwork",
        "PHLEGMATIC",
        False,
        "I offer help when a teammate is under pressure.",
    ),
    (
        "independence",
        "CHOLERIC",
        False,
        "I am comfortable completing a task with little supervision.",
    ),
    (
        "independence",
        "CHOLERIC",
        False,
        "I prefer to own a piece of work from start to finish.",
    ),
    (
        "attention_to_detail",
        "MELANCHOLIC",
        False,
        "I notice small errors in documents or processes before others do.",
    ),
    (
        "attention_to_detail",
        "MELANCHOLIC",
        False,
        "I check my work against a standard before I consider it finished.",
    ),
    (
        "optimism",
        "SANGUINE",
        False,
        "I usually expect that a setback can still lead to a useful outcome.",
    ),
    (
        "optimism",
        "SANGUINE",
        False,
        "I look for what is working before I focus on what is wrong.",
    ),
    (
        "emotional_expression",
        "SANGUINE",
        False,
        "Other people can usually tell how I feel from what I say or how I sound.",
    ),
    (
        "emotional_expression",
        "PHLEGMATIC",
        True,
        "I keep my feelings to myself in most professional or academic settings.",
    ),
]
