"""Security Culture Diagnostic Survey (SCDS) content.

The survey definition below was extracted from the HavenGRC landing funnel
(https://github.com/kindlyops/havengrc, flyway/sql/V5__ipsative_data.sql).

The SCDS instrument was created by Lance Hayden, Ph.D., and is provided
under a Creative Commons Attribution-ShareAlike 4.0 International License
(https://creativecommons.org/licenses/by-sa/4.0/).

This is an ipsative (forced-choice) survey: for each question the respondent
distributes a fixed budget of points among four statements, one per security
culture category of the Competing Security Cultures Framework.
"""

SURVEY_NAME = "SCDS_1"
SURVEY_AUTHOR = "Lance Hayden"
SURVEY_DESCRIPTION = (
    "Survey to identify existing security culture in an organization."
)
SURVEY_INSTRUCTIONS = (
    "For each question, assign a total of 10 points, divided among the four "
    "statements based on how accurately you think each describes your "
    "organization."
)

POINTS_PER_QUESTION = 10

CATEGORIES = ["Process", "Compliance", "Autonomy", "Trust"]

CATEGORY_DESCRIPTIONS = {
    "Process": (
        "Values stability, reliability, and standard ways of doing things. "
        "Security is infrastructure: policies, procedures, and centralized "
        "control."
    ),
    "Compliance": (
        "Values meeting external requirements and demonstrating control. "
        "Security is evidence: audits, reviews, and documented obligations."
    ),
    "Autonomy": (
        "Values adaptability, speed, and results. Security is a balance of "
        "risk and reward, decided closest to the action."
    ),
    "Trust": (
        "Values people, community, and shared responsibility. Security is "
        "everyone's job, built on awareness and mutual support."
    ),
}

# Each question maps a title to one statement per category. Statement text is
# verbatim from havengrc's V5__ipsative_data.sql (SQL '' unescaped to ').
QUESTIONS = [
    {
        "title": "What's valued most?",
        "answers": {
            "Process": (
                "Stability and reliability are valued most by the "
                "organization. It is critical that everyone knows the rules "
                "and follows them. The organization cannot succeed if people "
                "are all doing things different ways without centralized "
                "visibility."
            ),
            "Compliance": (
                "Successfully meeting external requirements is valued most "
                "by the organization. The organization is under a lot of "
                "scrutiny. It cannot succeed if people fail audits or do not "
                "live up to the expectations of those watching."
            ),
            "Autonomy": (
                "Adapting quickly and competing aggressively are valued most "
                "by the organization. Results are what matters. The "
                "organization cannot succeed if bureaucracy and red tape "
                "impair people's ability to be agile."
            ),
            "Trust": (
                "People and a sense of community are valued most by the "
                "organization. Everyone is in it together. The organization "
                "cannot succeed unless people are given the opportunities "
                "and skills to succeed on their own."
            ),
        },
    },
    {
        "title": "How does the organization work?",
        "answers": {
            "Process": (
                "The organization works on authority, policy, and standard "
                "ways of doing things. Organizational charts are formal and "
                "important. The organization is designed to ensure control "
                "and efficiency."
            ),
            "Compliance": (
                "The organization works on outside requirements and regular "
                "reviews. Audits are a central feature of life. The "
                "organization is designed to ensure everyone meets their "
                "obligations."
            ),
            "Autonomy": (
                "The organization works on independent action and giving "
                "people decision authority. There's no one right way to do "
                "things. The organization is designed to ensure that the "
                "right things get done in the right situations."
            ),
            "Trust": (
                "The organization works on teamwork and cooperation. It is a "
                "community. The organization is designed to ensure everyone "
                "is constantly learning, growing, and supporting one "
                "another."
            ),
        },
    },
    {
        "title": "What does security mean?",
        "answers": {
            "Process": (
                "Security means policies, procedures, and standards, "
                "automated wherever possible using technology. When people "
                "talk about security they are talking about the "
                "infrastructures in place to protect the organization's "
                "information assets."
            ),
            "Compliance": (
                "Security means showing evidence of visibility and control, "
                "particularly to external parties. When people talk about "
                "security they are talking about passing an audit or meeting "
                "a regulatory requirement."
            ),
            "Autonomy": (
                "Security means enabling the organization to adapt and "
                "compete, not hindering it or saying “no” to "
                "everything. When people talk about security they are "
                "talking about balancing risks and rewards."
            ),
            "Trust": (
                "Security means awareness and shared responsibility. When "
                "people talk about security they are talking about the need "
                "for everyone to be an active participant in protecting the "
                "organization."
            ),
        },
    },
    {
        "title": "How is information managed and controlled?",
        "answers": {
            "Process": (
                "Information is seen as a direct source of business value, "
                "accounted for, managed, and controlled like any other "
                "business asset. Formal rules and policies govern "
                "information use and control."
            ),
            "Compliance": (
                "Information is seen as a sensitive and protected resource, "
                "entrusted to the organization by others and subject to "
                "review and audit. Information use and control must always "
                "be documented and verified."
            ),
            "Autonomy": (
                "Information is seen as a flexible tool that is the key to "
                "agility and adaptability in the organization's environment. "
                "Information must be available where and when it is needed "
                "by the business, with a minimum of restrictive control."
            ),
            "Trust": (
                "Information is seen as key to people's productivity, "
                "collaboration, and success. Information must be a shared "
                "resource, minimally restricted, and available throughout "
                "the community to empower people and make them more "
                "successful."
            ),
        },
    },
    {
        "title": "How are operations managed?",
        "answers": {
            "Process": (
                "Operations are controlled and predictable, managed "
                "according to the same standards throughout the "
                "organization."
            ),
            "Compliance": (
                "Operations are visible and verifiable, managed and "
                "documented in order to support audits and outside reviews."
            ),
            "Autonomy": (
                "Operations are agile and adaptable, managed with minimal "
                "bureaucracy and capable of fast adaptation and flexible "
                "execution to respond to changes in the environment."
            ),
            "Trust": (
                "Operations are inclusive and supportive, allowing people "
                "to master new skills and responsibilities and to grow "
                "within the organization."
            ),
        },
    },
    {
        "title": "How is technology managed?",
        "answers": {
            "Process": (
                "Technology is centrally managed. Standards and formal "
                "policies exist to ensure uniform performance internally."
            ),
            "Compliance": (
                "Technology is regularly reviewed. Audits and evaluations "
                "exist to ensure the organization meets its obligations to "
                "others."
            ),
            "Autonomy": (
                "Technology is locally managed. Freedom exists to ensure "
                "innovation, adaptation, and results."
            ),
            "Trust": (
                "Technology is accessible to everyone. Training and support "
                "exists to empower users and maximize productivity."
            ),
        },
    },
    {
        "title": "How are people managed?",
        "answers": {
            "Process": (
                "People must conform to the needs of the organization. They "
                "must adhere to policies and standards of behavior. The "
                "success of the organization is built on everyone following "
                "the rules."
            ),
            "Compliance": (
                "People must demonstrate that they are doing things "
                "correctly. They must ensure the organization meets its "
                "obligations. The success of the organization is built on "
                "everyone regularly proving that they are doing things "
                "properly."
            ),
            "Autonomy": (
                "People must take risks and make quick decisions. They must "
                "not wait for someone else to tell them what's best. The "
                "success of the organization is built on everyone "
                "experimenting and innovating in the face of change."
            ),
            "Trust": (
                "People must work as a team and support one other. They "
                "must know that everyone is doing their part. The success "
                "of the organization is built on everyone learning and "
                "growing together."
            ),
        },
    },
    {
        "title": "How is risk managed?",
        "answers": {
            "Process": (
                "Risk is best managed by getting rid of deviations in the "
                "way things are done. Increased visibility and control "
                "reduce uncertainty and negative outcomes. The point is to "
                "create a reliable standard."
            ),
            "Compliance": (
                "Risk is best managed by documentation and regular review. "
                "Frameworks and evaluations reduce uncertainty and negative "
                "outcomes. The point is to keep everyone on their toes."
            ),
            "Autonomy": (
                "Risk is best managed by decentralizing authority. Negative "
                "outcomes are always balanced by potential opportunities. "
                "The point is to let those closest to the decision make the "
                "call."
            ),
            "Trust": (
                "Risk is best managed by sharing information and knowledge. "
                "Education and support reduce uncertainty and negative "
                "outcomes. The point is to foster a sense of shared "
                "responsibility."
            ),
        },
    },
    {
        "title": "How is accountability achieved?",
        "answers": {
            "Process": (
                "Accountability is stable and formalized. People know what "
                "to expect and what is expected of them. The same rewards "
                "and consequences are found throughout the organization."
            ),
            "Compliance": (
                "Accountability is enabled through review and audit. People "
                "know that they will be asked to justify their actions. "
                "Rewards and consequences are contingent upon external "
                "expectations and judgments."
            ),
            "Autonomy": (
                "Accountability is results-driven. People know there are no "
                "excuses for failing. Rewards and consequences are a "
                "product of successful execution on the organization's "
                "business."
            ),
            "Trust": (
                "Accountability is shared among the group. People know "
                "there are no rock stars or scapegoats. Rewards and "
                "consequences apply to everyone because everyone is a "
                "stakeholder in the organization."
            ),
        },
    },
    {
        "title": "How is performance evaluated?",
        "answers": {
            "Process": (
                "Performance is evaluated against formal strategies and "
                "goals. Success criteria are unambiguous."
            ),
            "Compliance": (
                "Performance is evaluated against the organization's "
                "ability to meet external requirements. Audits define "
                "success."
            ),
            "Autonomy": (
                "Performance is evaluated on the basis of specific "
                "decisions and outcomes. Business success is the primary "
                "criteria."
            ),
            "Trust": (
                "Performance is evaluated by the organizational community. "
                "Success is defined through shared values, commitment, and "
                "mutual respect."
            ),
        },
    },
]

NUM_QUESTIONS = len(QUESTIONS)
MAX_CATEGORY_POINTS = POINTS_PER_QUESTION * NUM_QUESTIONS
