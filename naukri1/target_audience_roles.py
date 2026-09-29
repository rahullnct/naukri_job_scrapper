"""Target-audience role plan shared by every job fetching script.

WHY THIS FILE EXISTS
--------------------
The portal is built for one audience: IT infrastructure and operations
people -- support/help desk, network/infrastructure, system/server, and
cloud/DevOps. That audience is defined in ``target_audience.txt`` in the
website repository, and the 68 titles in ``TARGET_AUDIENCE_ROLES`` below are
a copy of it.

Before this file existed, every scraper crawled a single 407/432 entry
"IT Department" list plus a broad department-level page. The broad page
returns whatever the job site chooses to show, which is how Sales, Finance,
HR and Healthcare listings reached the database.

WHAT IT CHANGES
---------------
1. The crawl plan becomes 80% target-audience roles and 20% other
   high-demand Indian IT roles, by search budget:

       68 target roles / (68 + 17 other) = 80.0%

   Every role target gets the same listing-page cap, so the split in search
   effort is exactly 80/20. The realised job mix will land near that but
   cannot be exact -- a "DevOps Engineer" search returns far more rows than
   an "Onsite Support Engineer" search, and no scraper can control that.

2. Broad department-level targets are dropped from the plan, so the scraper
   only ever asks for named roles.

3. ``is_non_it_title()`` rejects non-IT rows that a role search returns
   anyway. It is a blocklist with an IT override: anything carrying a clear
   IT signal is never rejected, so "Network Security Engineer" survives the
   "security guard" pattern.

This module holds data and pure functions only. It imports nothing from the
scrapers, so it is safe to import from any of them.
"""

import re


# ---------------------------------------------------------------------------
# 80% -- the target audience, copied from target_audience.txt
# ---------------------------------------------------------------------------

# IT Support / Help Desk
TARGET_ROLES_IT_SUPPORT = [
    "Desktop Support Engineer",
    "Desktop Support Technician",
    "IT Support Engineer",
    "IT Support Specialist",
    "IT Support Technician",
    "Technical Support Engineer",
    "Technical Support Specialist",
    "Help Desk Technician",
    "Help Desk Engineer",
    "Service Desk Engineer",
    "Service Desk Analyst",
    "IT Service Desk Analyst",
    "IT Support Analyst",
    "End User Support Engineer",
    "End User Computing Engineer",
    "IT Operations Support Engineer",
    "Field Support Engineer",
    "Onsite Support Engineer",
    "IT Technician",
    "IT Administrator",
]

# Network / Infrastructure
TARGET_ROLES_NETWORK = [
    "Network Engineer",
    "Network Support Engineer",
    "Network Administrator",
    "Network Technician",
    "Network Operations Engineer",
    "NOC Engineer",
    "NOC Analyst",
    "Network Operations Analyst",
    "Infrastructure Engineer",
    "Infrastructure Support Engineer",
    "Infrastructure Administrator",
    "IT Infrastructure Engineer",
    "Network Security Engineer",
    "Wireless Network Engineer",
    "LAN WAN Engineer",
    "Network Operations Center Engineer",
    "Network Implementation Engineer",
    "Network Field Engineer",
]

# System / Server
TARGET_ROLES_SYSTEM = [
    "System Engineer",
    "Systems Engineer",
    "Systems Administrator",
    "System Administrator",
    "Server Administrator",
    "Windows Server Administrator",
    "Linux System Administrator",
    "Linux Engineer",
    "Windows System Engineer",
    "Server Support Engineer",
    "Systems Support Engineer",
    "Infrastructure Systems Engineer",
    "IT Systems Engineer",
    "System Operations Engineer",
    "Platform Engineer",
    "Infrastructure Operations Engineer",
]

# Cloud / DevOps Infrastructure (2nd level, from the Azure admin course)
TARGET_ROLES_CLOUD = [
    "Cloud Engineer",
    "Cloud Support Engineer",
    "Cloud Infrastructure Engineer",
    "Cloud Operations Engineer",
    "Cloud Administrator",
    "Azure Administrator",
    "Azure Cloud Engineer",
    "AWS Cloud Engineer",
    "AWS Systems Administrator",
    "DevOps Engineer",
    "DevOps Infrastructure Engineer",
    "Site Reliability Engineer",
    "Cloud Operations Analyst",
    "Cloud Infrastructure Administrator",
]

TARGET_AUDIENCE_ROLES = (
    TARGET_ROLES_IT_SUPPORT
    + TARGET_ROLES_NETWORK
    + TARGET_ROLES_SYSTEM
    + TARGET_ROLES_CLOUD
)


# ---------------------------------------------------------------------------
# 20% -- other highest-demand IT roles in the Indian market
# ---------------------------------------------------------------------------

HIGH_DEMAND_IT_ROLES = [
    "Java Developer",
    "Python Developer",
    "Full Stack Developer",
    "React Developer",
    "Angular Developer",
    "Node.js Developer",
    ".NET Developer",
    "Automation Test Engineer",
    "QA Engineer",
    "Data Engineer",
    "Data Analyst",
    "Machine Learning Engineer",
    "Cybersecurity Analyst",
    "Salesforce Developer",
    "SAP Consultant",
    "ServiceNow Developer",
    "Database Administrator",
]


# ---------------------------------------------------------------------------
# Non-IT rejection
# ---------------------------------------------------------------------------

# A clear IT signal. A title matching any of these is never rejected, no
# matter what else it contains. This is what keeps "Network Security
# Engineer" from being caught by the "security guard" pattern and
# "IT Recruiter"-style false positives from removing real IT rows.
_IT_OVERRIDE = re.compile(
    r"\b("
    r"it support|technical support|help ?desk|service desk|desktop support|"
    r"end user|system admin|systems admin|server admin|linux|windows server|"
    r"network|noc|infrastructure|infra|cloud|azure|aws|gcp|devops|sre|"
    r"site reliability|kubernetes|docker|vmware|citrix|active directory|"
    r"middleware|websphere|weblogic|storage|backup|virtualisation|"
    r"virtualization|software|developer|programmer|engineer.*(java|python|"
    r"\.net|node|react|angular)|full stack|frontend|front end|backend|"
    r"back end|database|dba|sql server|oracle dba|data engineer|"
    r"data analyst|data scien|machine learning|artificial intelligence|"
    r"cyber ?security|"
    r"information security|soc analyst|penetration test|qa engineer|"
    r"test engineer|automation test|sdet|salesforce|sap |service ?now|"
    r"application support|it operations|it engineer|it executive|"
    r"it administrator|it technician|it analyst|it manager"
    r")\b",
    re.IGNORECASE,
)

# Non-IT occupations. Phrases are deliberately multi-word where a single
# word would be ambiguous ("engineer", "manager", "analyst" alone are not
# usable signals).
_NON_IT = re.compile(
    r"\b("
    # Sales / business development / insurance
    r"sales executive|sales officer|sales manager|sales representative|"
    r"field sales|inside sales|business development executive|"
    r"business development manager|bde|telecaller|tele caller|telecalling|"
    r"insurance advisor|policy advisor|relationship manager|"
    r"branch manager|territory manager|area sales|channel partner|"
    r"loan officer|collection executive|recovery agent|"
    # Finance / accounting / banking
    r"accountant|accounts executive|accounts assistant|accounts payable|"
    r"accounts receivable|book ?keeper|taxation|gst |audit assistant|"
    r"internal auditor|statutory audit|cashier|bank teller|"
    r"financial analyst|equity research|credit analyst|underwriter|"
    r"chartered accountant|company secretary|"
    # HR / admin / office
    r"hr executive|hr manager|hr generalist|human resource|recruiter|"
    r"talent acquisition|payroll executive|receptionist|front office|"
    r"office assistant|office boy|admin executive|administrative assistant|"
    r"personal assistant|data entry|back office|"
    # Marketing / creative / content
    r"digital marketing|seo executive|social media|content writer|"
    r"copywriter|content creator|graphic designer|video editor|"
    r"video maker|photographer|animator|brand manager|"
    r"marketing executive|marketing manager|public relations|"
    # Logistics / warehouse / field
    r"warehouse|logistics|supply chain|delivery boy|delivery executive|"
    r"driver|courier|dispatch|store keeper|storekeeper|inventory executive|"
    r"procurement|purchase executive|"
    # Education
    # NOTE: no bare "principal" -- "Principal Engineer" is an IT seniority
    # title, not a school principal.
    r"teacher|tutor|lecturer|professor|faculty|school principal|"
    r"academic counsel|admission counsel|trainer \(non|"
    # Healthcare
    r"nurse|nursing|doctor|physician|surgeon|pharmacist|"
    r"medical representative|lab technician|radiolog|physiotherap|"
    r"dental|paramedic|ward boy|"
    # Core (non-software) engineering / manufacturing
    r"civil engineer|mechanical engineer|electrical engineer|"
    r"electronics engineer|instrumentation engineer|chemical engineer|"
    r"production engineer|maintenance engineer|site engineer|"
    r"quality inspector|cnc |welder|fitter|machinist|draughtsman|"
    r"autocad|hvac|"
    # Legal / facilities / hospitality / security
    r"lawyer|advocate|paralegal|legal executive|legal associate|"
    r"housekeeping|security guard|chef|cook|waiter|steward|"
    r"hotel management|travel consultant|"
    # BPO / voice
    r"bpo|voice process|customer care|customer service executive|"
    r"customer support executive|call center|call centre|"
    r"process associate|non voice"
    r")\b",
    re.IGNORECASE,
)


def _normalise(text):
    """Lowercase and collapse punctuation so patterns match naturally."""
    text = str(text or "").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9+#. ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_non_it_title(title):
    """True when a job title is clearly not an IT role.

    Blocklist with an IT override: an unmistakable IT signal always wins, so
    the filter cannot silently drop target-audience rows.
    """
    norm = _normalise(title)
    if not norm:
        return False
    if _IT_OVERRIDE.search(norm):
        return False
    return bool(_NON_IT.search(norm))


def build_role_plan(include_high_demand=True):
    """Return the ordered crawl plan: 80% target audience, 20% other IT.

    Target roles come first so that a run interrupted part way through a
    cycle still spends its time on the audience that matters.
    """
    plan = []
    seen = set()

    groups = [TARGET_AUDIENCE_ROLES]
    if include_high_demand:
        groups.append(HIGH_DEMAND_IT_ROLES)

    for group in groups:
        for role in group:
            key = _normalise(role)
            if key and key not in seen:
                seen.add(key)
                plan.append(role)

    return plan


def role_plan_split():
    """Return (target_count, other_count, target_percent) for logging."""
    target = len(build_role_plan(include_high_demand=False))
    total = len(build_role_plan(include_high_demand=True))
    other = total - target
    percent = round((target * 100.0) / total, 1) if total else 0.0
    return target, other, percent
