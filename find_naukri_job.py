import asyncio
import os
import re
import json
import time
import math
import socket
import random
from datetime import datetime
from urllib.parse import quote_plus, urlparse, urlunparse
#from naukri_job_detail_scraper import run_detail_scraper
import hashlib
from datetime import timezone
from zipfile import BadZipFile
from email.utils import parsedate_to_datetime

import pandas as pd
from playwright.async_api import async_playwright
from new_mylib import job_by_department, city_by_states, city_to_state

# --------------------------------------------------
# INTERNET CHECK
# --------------------------------------------------
rank = 1
num_sys = 5

INTERNET_CHECK_HOST    = "8.8.8.8"
INTERNET_CHECK_PORT    = 53
INTERNET_CHECK_TIMEOUT = 3
DETAIL_OUTPUT_FILE = "current_data.xlsx"
BATTERY_STOP_PCT = 20
CYCLE_STATE_FILE = "cycle_state.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(BASE_DIR, "naukri_auth.json")

DETAIL_COLUMNS = [
    "job_id", "internal_job_id", "job_title", "company_name", "company_website",
    "job_description", "skills_required", "experience_required",
    "experience_min_years", "experience_max_years",
    "salary_min", "salary_max", "salary_currency",
    "location", "city", "state", "country",
    "remote_type", "employment_type", "job_category",
    "posted_date", "expiry_date", "application_deadline",
    "apply_url", "updated_at", "fetched_at",
    "is_fake", "is_active", "source_url", "source_type", "source_platform", "score",
]

MASTER_COLUMNS = [
    "state", "role_category", "job_title", "location",
    "search_keyword", "sample_job_url",
    "first_seen_at", "last_seen_at",
    "seen_count", "is_active",
    "source_platform", "source_type",
]


def safe_read_excel_or_empty(file_path: str, columns: list) -> pd.DataFrame:
    """
    Read Excel safely.

    If file is missing, empty, corrupted, or half-written,
    remove it and continue with an empty dataframe.
    """
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)

    try:
        if os.path.getsize(file_path) == 0:
            raise ValueError("Excel file is empty.")

        return pd.read_excel(
            file_path,
            engine="openpyxl",
        )

    except (
        BadZipFile,
        ValueError,
        OSError,
        EOFError,
    ) as error:
        print(
            f"⚠️ Corrupted Excel found: {file_path}. "
            f"Removing it and continuing. Error: {error}"
        )

        try:
            os.remove(file_path)
        except OSError as remove_error:
            print(
                f"⚠️ Could not remove corrupted file "
                f"{file_path}: {remove_error}"
            )

        return pd.DataFrame(columns=columns)


def safe_to_excel(df: pd.DataFrame, file_path: str) -> None:
    """
    Save Excel safely.

    First write to temp xlsx file, then replace original file.
    This prevents main Excel corruption when script is stopped
    using Ctrl+C during save.
    """
    folder_path = os.path.dirname(
        os.path.abspath(file_path)
    )

    base_name = os.path.basename(file_path)
    file_name, file_ext = os.path.splitext(base_name)

    temp_file = os.path.join(
        folder_path,
        f".{file_name}.tmp{file_ext}"
    )

    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except OSError:
            pass

    df.to_excel(
        temp_file,
        index=False,
        engine="openpyxl",
    )

    os.replace(
        temp_file,
        file_path,
    )


def load_cycle_num() -> int:
    """
    Reads current cycle number from cycle_state.json.
    If file does not exist, return 0.
    """
    if not os.path.exists(CYCLE_STATE_FILE):
        return 0

    try:
        with open(CYCLE_STATE_FILE, "r") as f:
            data = json.load(f)
        return int(data.get("cycle_num", 0))
    except Exception:
        return 0


def save_cycle_num(cycle_num: int) -> None:
    """
    Saves current cycle number into cycle_state.json.
    """
    with open(CYCLE_STATE_FILE, "w") as f:
        json.dump({"cycle_num": cycle_num}, f, indent=4)


def get_next_cycle_file(base_file="current_data.xlsx"):
    """
    Returns next cycle file name using cycle_state.json.

    Example:
    cycle_num = 0 → current_data_cycle1.xlsx
    cycle_num = 1 → current_data_cycle2.xlsx
    cycle_num = 2 → current_data_cycle3.xlsx
    """
    base_name = os.path.splitext(base_file)[0]

    current_cycle = load_cycle_num()
    next_cycle = current_cycle + 1

    cycle_file = f"{base_name}_cycle{next_cycle}.xlsx"

    return cycle_file, next_cycle


def append_detail_to_excel(row: dict, output_file: str = DETAIL_OUTPUT_FILE, cycle_size: int = 100):
    """
    Append job detail to current_data.xlsx.

    If current_data.xlsx reaches 100 rows:
    1. Save/copy it as current_data_cycle1.xlsx, current_data_cycle2.xlsx, etc.
    2. Empty current_data.xlsx
    3. Continue adding next data into current_data.xlsx
    """

    df = safe_read_excel_or_empty(
        output_file,
        DETAIL_COLUMNS,
    )

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    if len(df) >= cycle_size:
        cycle_file, cycle_num = get_next_cycle_file(output_file)

        safe_to_excel(
            df,
            cycle_file,
        )
        save_cycle_num(cycle_num)

        empty_df = pd.DataFrame(columns=DETAIL_COLUMNS)
        safe_to_excel(
            empty_df,
            output_file,
        )

        print(f"      Cycle completed → {cycle_file} | rows: {len(df)}")
        print(f"      Emptied → {output_file}")

    else:
        safe_to_excel(
            df,
            output_file,
        )
        print(f"      Saved detail → {output_file} | rows: {len(df)}/{cycle_size}")


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def clean_value(value, default=""):
    if value is None:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    text = str(value).strip()
    if text.lower() in ("nan", "none", "null"):
        return default
    return text


def clean_text(value, default=""):
    text = clean_value(value, default)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_job_id(job_title, source, timestamp):
    raw = "|".join([
        clean_text(job_title).lower(),
        clean_text(source).lower(),
        clean_text(timestamp),
    ])
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def extract_internal_job_id(url: str) -> str:
    url = clean_value(url)
    match = re.search(r"-(\d{8,})/?(?:\?|#)?$", url)
    if match:
        return match.group(1)

    nums = re.findall(r"\d{8,}", url)
    if nums:
        return nums[-1]

    return url.rstrip("/").split("/")[-1]


def strip_html(text: str) -> str:
    text = clean_value(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_experience_from_url(job_url: str):
    job_url = clean_value(job_url).lower()

    match = re.search(
        r"-(\d+(?:\.\d+)?)-to-(\d+(?:\.\d+)?)-years(?:-|/|\?|$)",
        job_url,
        re.IGNORECASE,
    )

    if match:
        exp_min = float(match.group(1))
        exp_max = float(match.group(2))
        return f"{exp_min:g} - {exp_max:g} years", exp_min, exp_max

    return "", None, None


def get_battery_percent():
    """
    Linux battery percentage checker.
    Returns battery percentage or None if battery not found.
    """
    import glob

    paths = glob.glob("/sys/class/power_supply/BAT*/capacity")

    if not paths:
        return None

    try:
        return float(open(paths[0]).read().strip())
    except Exception:
        return None


def wait_for_battery(min_percent=BATTERY_STOP_PCT, check_interval=60):
    """
    If battery is <= min_percent, pause script.
    Resume only when battery becomes greater than min_percent.
    """
    pct = get_battery_percent()

    if pct is None:
        return

    if pct > min_percent:
        return

    print(f"\n  [BATTERY LOW] Battery is {pct:.0f}% — script paused.")
    print(f"  Please charge laptop. Checking every {check_interval}s...\n")

    while True:
        pct = get_battery_percent()

        if pct is None:
            return

        if pct > min_percent:
            print(f"  [BATTERY OK] Battery is {pct:.0f}% — resuming.\n")
            return

        time.sleep(check_interval)

async def async_dom_text(page, *selectors, default=""):
    for selector in selectors:
        try:
            el = page.locator(selector).first
            if await el.count() > 0:
                text = clean_value(await el.inner_text(timeout=3000))
                if text:
                    return text
        except Exception:
            continue
    return default


async def async_dom_attr(page, selector, attr, default=""):
    try:
        el = page.locator(selector).first
        if await el.count() > 0:
            value = await el.get_attribute(attr, timeout=3000)
            return clean_value(value, default)
    except Exception:
        pass
    return default


async def extract_json_ld_async(page) -> dict:
    try:
        scripts = page.locator("script[type='application/ld+json']")
        count = await scripts.count()

        for i in range(count):
            raw = clean_value(await scripts.nth(i).inner_text(timeout=3000))
            if not raw:
                continue

            data = json.loads(raw)

            if isinstance(data, dict) and data.get("@graph"):
                for item in data["@graph"]:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        return item

            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                return data

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        return item

    except Exception:
        pass

    return {}


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    print(f"      Detail scraping → {url}")

    fetched_at = now_utc()

    try:
        # HTTP 403 handled inside (same-URL bounded retry); other errors as before.
        await safe_naukri_navigate(
            page, url, wait_until="domcontentloaded", timeout=60000, settle_ms=2000,
            nav_type="JOB_DETAIL", job_url=url,
        )
    except (NaukriNavigationStop, NaukriServerError):
        raise
    except Exception as e:
        print(f"      [WARN] Detail page failed: {e}")

    json_ld = await extract_json_ld_async(page)
    job_title = (
        await async_dom_text(page, "h1[class*='title']", "h1[class*='jd-header-title']", "h1")
        or clean_value(input_row.get("job_title"))
    )

    company_name = (
        await async_dom_text(page, "a[class*='comp-name']", "[class*='company-name']", "[class*='compName']")
        or clean_value(input_row.get("company_name"))
    )

    company_website = (
        await async_dom_attr(page, "a[class*='comp-name']", "href")
        or clean_value(input_row.get("company_website"))
    )

    job_description = await async_dom_text(
        page,
        "section[class*='job-desc']",
        "div[class*='job-desc']",
        "[class*='dang-inner-html']",
        "[class*='description']",
    )

    skills = []
    try:
        skill_elements = page.locator("[class*='key-skill'] a, [class*='skills'] a, a[class*='chip']")
        count = await skill_elements.count()
        for i in range(count):
            txt = clean_value(await skill_elements.nth(i).inner_text(timeout=2000))
            if txt:
                skills.append(txt)
    except Exception:
        pass

    experience_required = await async_dom_text(
        page,
        "[class*='exp-txt']",
        "[class*='expwdth']",
        "span[class*='exp']",
        "[class*='experience']",
    )

    salary_text = await async_dom_text(
        page,
        "[class*='salary']",
        "[class*='package']",
        "span[class*='sal']",
    )

    location_text = (
        await async_dom_text(page, "[class*='location']", "[class*='loc-link']", "span[class*='loc']")
        or clean_value(input_row.get("location"))
    )

    posted_date = (
        clean_value(json_ld.get("datePosted"))
        or await async_dom_text(
            page,
            "[class*='posted']",
            "[class*='post-date']",
            "[class*='job-post-day']",
        )
    )
    expiry_date = clean_value(json_ld.get("validThrough"))

    apply_url = (
        await async_dom_attr(page, "a[class*='apply']", "href")
        or url
    )

    source_type = clean_value(input_row.get("source_type"), "job_portal")
    source_platform = clean_value(input_row.get("source_platform"), "Naukri")
    experience_required, experience_min_years, experience_max_years = parse_experience_from_url(url)
    return {
        "job_id": generate_job_id(job_title, source_platform, fetched_at),
        "internal_job_id": extract_internal_job_id(url),
        "job_title": job_title,
        "company_name": company_name,
        "company_website": company_website,
        "job_description": strip_html(job_description),
        "skills_required": "; ".join(skills),
        "experience_required": experience_required,
        "experience_min_years": experience_min_years,
        "experience_max_years": experience_max_years,
        "salary_min": "not disclosed",
        "salary_max": "not disclosed",
        "salary_currency": "INR",
        "location": location_text,
        "city": clean_value(input_row.get("city") or input_row.get("location")),
        "state": clean_value(input_row.get("state")),
        "country": "India",
        "remote_type": "Onsite",
        "employment_type": "Full-time",
        "job_category": clean_value(input_row.get("role_category") or input_row.get("job_category")),
        "posted_date": posted_date,
        "expiry_date": expiry_date,
        "application_deadline": expiry_date,
        "apply_url": apply_url,
        "updated_at": posted_date,
        "fetched_at": fetched_at,
        "is_fake": False,
        "is_active": True,
        "source_url": "https://www.naukri.com",
        "source_type": source_type,
        "source_platform": source_platform,
        "score": 30,
    }

def is_internet_available():
    try:
        socket.setdefaulttimeout(INTERNET_CHECK_TIMEOUT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((INTERNET_CHECK_HOST, INTERNET_CHECK_PORT))
        s.close()
        return True
    except (socket.error, OSError):
        return False

def wait_for_internet(check_interval=5):
    if is_internet_available():
        return
    print("\n  [OFFLINE] Internet lost — script paused.")
    print(f"  Checking every {check_interval}s until restored...\n")
    while not is_internet_available():
        time.sleep(check_interval)
    print("  [ONLINE]  Internet restored — resuming.\n")

# --------------------------------------------------
# HTTP 403 / ACCESS-DENIED HANDLING
# --------------------------------------------------
# A 403 is NOT a network failure: the machine is online, Naukri simply refused
# this request. It must never call wait_for_internet(), never advance the
# checkpoint, and never be retried forever. Policy:
#   403 #1 -> wait 15 min -> retry the SAME URL
#   403 #2 -> wait 30 min -> retry the SAME URL
#   403 #3 -> wait 60 min -> retry the SAME URL
#   403 #4 -> stop safely, state files untouched
# No proxy/IP/UA rotation, no CAPTCHA handling, no cookie manipulation.

HTTP_403_STATUS = 403
HTTP_403_COOLDOWNS_SECONDS = [
    15 * 60,
    30 * 60,
    60 * 60,
]
HTTP_403_MAX_RETRIES = len(HTTP_403_COOLDOWNS_SECONDS)
ACCESS_EVENTS_LOG_FILE = "naukri_access_events.log"

# HTTP 429 = Naukri is rate-limiting. Also NOT a network failure. A valid
# Retry-After header always wins (even when longer than the fallback); the
# fallback below applies only when the header is missing or unusable.
#   429 #1 -> wait 15 min (or Retry-After) -> retry the SAME URL
#   429 #2 -> wait 30 min (or Retry-After) -> retry the SAME URL
#   429 #3 -> wait 60 min (or Retry-After) -> retry the SAME URL
#   429 #4 -> stop safely, state files untouched
# The counter resets only after the same URL loads AND validates as a Naukri
# page. Kept fully separate from the 403 policy above.
HTTP_429_STATUS = 429
HTTP_429_COOLDOWNS_SECONDS = [
    15 * 60,
    30 * 60,
    60 * 60,
]
HTTP_429_MAX_RETRIES = len(HTTP_429_COOLDOWNS_SECONDS)
# Sanity cap for Retry-After. Anything above is treated as unusable (logged),
# so a corrupt header cannot park the worker for days.
HTTP_429_RETRY_AFTER_MAX_SECONDS = 24 * 60 * 60

# HTTP 5xx = temporary server/CDN fault. Also NOT a network failure and NOT
# 403/429. Policy: retry the SAME URL with exponential backoff + jitter
# (~5, 10, 20, 40 s). If still 5xx the caller DEFERS the item into a
# persisted queue (listing pages and job details are queued separately),
# continues with the remaining work, and retries the queue later with a
# small separate budget. Nothing here rotates anything or bypasses anything.
HTTP_5XX_STATUSES = {500, 502, 503, 504}
HTTP_5XX_BASE_DELAY_SECONDS = 5
HTTP_5XX_MAX_IMMEDIATE_RETRIES = 4
HTTP_5XX_JITTER_FRACTION = 0.2                 # +/- 20% of the base delay
HTTP_5XX_PAGE_DEFER_COOLDOWN_SECONDS = 10 * 60 # wait before the next known page
HTTP_5XX_DEFERRED_PAGE_MAX_RETRIES = 2
HTTP_5XX_DEFERRED_JOB_MAX_RETRIES = 2
FAILED_5XX_PAGE_QUEUE_FILE = "state_5xx_pages.json"   # FAILED_5XX_PAGE_QUEUE
FAILED_5XX_JOB_QUEUE_FILE = "state_5xx_jobs.json"     # FAILED_5XX_JOB_QUEUE
UNRESOLVED_5XX_FILE = "naukri_5xx_unresolved.json"

# Title fragments of security/challenge interstitials. Used ONLY to log that a
# non-403 response is not a normal job page. Nothing here tries to pass them.
SECURITY_CHALLENGE_TITLE_MARKERS = (
    "access denied",
    "captcha",
    "verify you are",
    "security check",
    "unusual traffic",
    "are you a robot",
    "attention required",
    "request blocked",
)


class NaukriNavigationStop(Exception):
    """Base for 'stop this worker, checkpoint preserved' navigation outcomes."""

    status_label = "HTTP error"

    def __init__(self, url: str, attempts: int, context: dict):
        self.url = url
        self.attempts = attempts
        self.context = dict(context or {})
        super().__init__(
            f"{self.status_label} from Naukri persisted after {attempts} retries: {url}"
        )

    def print_stop(self) -> None:
        raise NotImplementedError


class NaukriAccessDenied(NaukriNavigationStop):
    """Raised when Naukri keeps returning HTTP 403 after every bounded retry."""

    status_label = "HTTP 403"

    def print_stop(self) -> None:
        print_http_403_stop(self.url, self.context)


class NaukriRateLimited(NaukriNavigationStop):
    """Raised when Naukri keeps returning HTTP 429 after every bounded retry."""

    status_label = "HTTP 429"

    def print_stop(self) -> None:
        print_http_429_stop(self.url, self.context)


class NaukriServerError(Exception):
    """HTTP 5xx persisted through every immediate retry of one URL.

    Deliberately NOT a NaukriNavigationStop: the worker must not stop. The
    caller defers the item (listing page or job) and continues.
    """

    def __init__(self, url: str, status: int, attempts: int, context: dict):
        self.url = url
        self.status = status
        self.attempts = attempts
        self.context = dict(context or {})
        super().__init__(
            f"HTTP {status} from Naukri persisted after {attempts} immediate retries: {url}"
        )


def current_checkpoint_context() -> dict:
    """Position as recorded in the EXISTING checkpoint files.

    Both files are written before every navigation, so they always describe
    the operation currently in flight. Reading them here means the 403 path
    reports and preserves exactly what a restart would resume from.
    """
    city_state = load_city_state()
    role_state = load_role_state()
    city = city_state.get("city_name") or ""
    try:
        state_name = city_to_state(city) if city else ""
    except Exception:
        state_name = ""
    return {
        "rank": rank,
        "city": city,
        "state": state_name or "",
        "role_category": role_state.get("role_category") or "",
        "search_keyword": role_state.get("search_keyword") or "",
        "page_number": city_state.get("page_number", 1),
    }


def log_access_event(event: str, url: str, status, context: dict,
                     landed_url: str = "", attempt: int = 0,
                     cooldown_seconds: int = 0, action: str = "",
                     retry_after_raw: str = "", retry_after_seconds="",
                     nav_type: str = "", job_url: str = "", deferred_attempt="",
                     jitter_seconds="") -> None:
    """Append one access/security event line. Never logs cookies or tokens."""
    ctx = context or {}
    fields = [
        ("timestamp", now_time()),
        ("rank", ctx.get("rank", rank)),
        ("event", event),
        ("http_status", status if status is not None else "unknown"),
        ("requested_url", url),
        ("landed_url", landed_url or ""),
        ("city", ctx.get("city", "")),
        ("state", ctx.get("state", "")),
        ("role_category", ctx.get("role_category", "")),
        ("search_keyword", ctx.get("search_keyword", "")),
        ("page_number", ctx.get("page_number", "")),
        ("nav_type", nav_type),
        ("job_url", job_url),
        ("attempt", attempt),
        ("deferred_attempt", deferred_attempt),
        ("jitter_seconds", jitter_seconds),
        ("retry_after_raw", retry_after_raw if retry_after_raw is not None else ""),
        ("retry_after_seconds", retry_after_seconds if retry_after_seconds is not None else ""),
        ("cooldown_seconds", cooldown_seconds),
        ("action", action),
    ]
    line = " | ".join(f"{key}={value}" for key, value in fields)
    try:
        with open(ACCESS_EVENTS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as error:
        print(f"  [WARN] Could not write {ACCESS_EVENTS_LOG_FILE}: {error}")


def _format_minutes(seconds: int) -> str:
    return f"{seconds // 60} minutes"


def print_http_403_banner(url: str, context: dict, attempt: int,
                          cooldown_seconds: int) -> None:
    print("\n" + "=" * 60)
    print("[HTTP 403 - ACCESS DENIED]\n")
    print(f"Requested URL : {url}")
    print(f"City          : {context.get('city') or '—'}")
    print(f"Role          : {context.get('search_keyword') or '—'}"
          f"  ({context.get('role_category') or '—'})")
    print(f"Page          : {context.get('page_number', '—')}")
    print(f"Attempt       : {attempt}/{HTTP_403_MAX_RETRIES}")
    print("Action        : Current state preserved")
    print(f"Cooldown      : {_format_minutes(cooldown_seconds)}")
    print("Next action   : Retry the same URL")
    print("=" * 60 + "\n", flush=True)


def print_http_403_stop(url: str, context: dict) -> None:
    print("\n" + "=" * 60)
    print("[HTTP 403 - STOPPING]\n")
    print("Naukri continues to return HTTP 403.")
    print("No further automatic retry will be performed.\n")
    print("Current scraper state has been preserved.\n")
    print(f"City : {context.get('city') or '—'}")
    print(f"Role : {context.get('search_keyword') or '—'}"
          f"  ({context.get('role_category') or '—'})")
    print(f"Page : {context.get('page_number', '—')}")
    print(f"URL  : {url}\n")
    print("Re-run the scraper after investigating the access issue.")
    print("=" * 60 + "\n", flush=True)


def parse_retry_after(raw_value):
    """Parse a Retry-After header into whole seconds.

    Returns (seconds, note). seconds is None when the header is absent,
    malformed, negative, or above HTTP_429_RETRY_AFTER_MAX_SECONDS; note says
    why, so the caller can log it and fall back to the configured policy.
    Supports both forms allowed by RFC 9110: delta-seconds and HTTP-date.
    """
    if raw_value is None:
        return None, "not provided"
    text = str(raw_value).strip()
    if not text:
        return None, "empty"

    seconds = None
    if re.fullmatch(r"\d+", text):
        seconds = int(text)
        form = "seconds"
    else:
        try:
            when = parsedate_to_datetime(text)
        except (TypeError, ValueError, IndexError):
            when = None
        if when is None:
            return None, f"malformed ({text[:40]!r})"
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        seconds = int(math.ceil((when - datetime.now(timezone.utc)).total_seconds()))
        form = "http-date"

    if seconds < 0:
        # A date already in the past means "retry now"; still pause briefly
        # via the configured fallback rather than hammering immediately.
        return None, f"{form} in the past"
    if seconds > HTTP_429_RETRY_AFTER_MAX_SECONDS:
        return None, f"{form} exceeds {HTTP_429_RETRY_AFTER_MAX_SECONDS}s cap"
    return seconds, form


def _response_header(response, name: str):
    """Header value from a Playwright response, or None. Never raises."""
    if response is None:
        return None
    try:
        headers = response.headers or {}
        for key, value in headers.items():
            if key.lower() == name.lower():
                return value
    except Exception:
        pass
    return None


def print_http_429_banner(url: str, context: dict, attempt: int,
                          cooldown_seconds: int, retry_after_raw,
                          retry_after_seconds) -> None:
    print("\n" + "=" * 60)
    print("[HTTP 429 - TOO MANY REQUESTS]\n")
    print("Naukri is currently rate-limiting this scraper.\n")
    print(f"Requested URL : {url}")
    print(f"City          : {context.get('city') or '—'}")
    print(f"Role          : {context.get('search_keyword') or '—'}"
          f"  ({context.get('role_category') or '—'})")
    print(f"Page          : {context.get('page_number', '—')}")
    print(f"Attempt       : {attempt}/{HTTP_429_MAX_RETRIES}\n")
    print("Checkpoint    : PRESERVED")
    if retry_after_seconds is not None:
        print(f"Retry-After   : {retry_after_raw} ({retry_after_seconds} seconds)")
        print(f"Cooldown      : {_format_minutes(cooldown_seconds)} (from Retry-After)")
    else:
        shown = "Not provided" if retry_after_raw in (None, "") else f"unusable: {retry_after_raw!r}"
        print(f"Retry-After   : {shown}")
        print(f"Cooldown      : {_format_minutes(cooldown_seconds)} (configured fallback)")
    print("Next Action   : Retry EXACT SAME URL")
    print("=" * 60 + "\n", flush=True)


def print_http_429_stop(url: str, context: dict) -> None:
    print("\n" + "=" * 60)
    print("[HTTP 429 - PERSISTENT RATE LIMIT]\n")
    print("Naukri continues to return HTTP 429.\n")
    print("Automatic retries have been exhausted.\n")
    print("Current checkpoint has been preserved.\n")
    print(f"City          : {context.get('city') or '—'}")
    print(f"Role          : {context.get('search_keyword') or '—'}"
          f"  ({context.get('role_category') or '—'})")
    print(f"Page          : {context.get('page_number', '—')}")
    print(f"URL           : {url}\n")
    print("No further Naukri requests will be sent by this worker.\n")
    print("Manual investigation is required.")
    print("=" * 60 + "\n", flush=True)


def http_5xx_backoff_seconds(retry_index: int):
    """(delay, jitter) for immediate 5xx retry number retry_index (0-based).

    delay = base * 2**index, plus a uniform jitter of +/- HTTP_5XX_JITTER_FRACTION
    so several ranks do not retry at exactly the same moment. Never below 1 s.
    """
    base = HTTP_5XX_BASE_DELAY_SECONDS * (2 ** retry_index)
    jitter = random.uniform(-HTTP_5XX_JITTER_FRACTION, HTTP_5XX_JITTER_FRACTION) * base
    return max(1.0, base + jitter), jitter


def _status_reason(status) -> str:
    return {
        500: "INTERNAL SERVER ERROR", 502: "BAD GATEWAY",
        503: "SERVICE UNAVAILABLE", 504: "GATEWAY TIMEOUT",
    }.get(status, "SERVER ERROR")


def print_http_5xx_retry_banner(url: str, status, context: dict, nav_type: str,
                                attempt: int, delay: float, job_url: str = "") -> None:
    print("\n" + "=" * 60)
    print(f"[HTTP {status} - {_status_reason(status)}]\n")
    print(f"Type          : {nav_type.replace('_', ' ')}")
    print(f"City          : {context.get('city') or '—'}")
    print(f"Role          : {context.get('search_keyword') or '—'}"
          f"  ({context.get('role_category') or '—'})")
    print(f"Page          : {context.get('page_number', '—')}")
    if job_url:
        print(f"Job URL       : {job_url}")
    print(f"Attempt       : {attempt}/{HTTP_5XX_MAX_IMMEDIATE_RETRIES}")
    print(f"Retry In      : {delay:.1f} seconds")
    print("Action        : Retry SAME URL")
    print("=" * 60 + "\n", flush=True)


def print_http_5xx_page_deferred(status, context: dict, page_number, page1_case: bool) -> None:
    print("\n" + "=" * 60)
    print("[PERSISTENT 5xx - LISTING PAGE DEFERRED]\n")
    print(f"Status        : {status}")
    print(f"City          : {context.get('city') or '—'}")
    print(f"Role          : {context.get('search_keyword') or '—'}"
          f"  ({context.get('role_category') or '—'})")
    print(f"Page          : {page_number}\n")
    print("Immediate retries exhausted.\n")
    print("Action:")
    if page1_case:
        print("1. Whole search combination added to FAILED_5XX_PAGE_QUEUE (total pages unknown)")
        print(f"2. Wait {HTTP_5XX_PAGE_DEFER_COOLDOWN_SECONDS // 60} minutes")
        print("3. Continue to the next search combination (this one is NOT marked done)")
        print("4. Retry Page 1 later; its remaining pages are discovered only after it loads")
    else:
        print(f"1. Page {page_number} added to FAILED_5XX_PAGE_QUEUE")
        print(f"2. Wait {HTTP_5XX_PAGE_DEFER_COOLDOWN_SECONDS // 60} minutes")
        print(f"3. Continue to Page {int(page_number) + 1}")
        print(f"4. Retry Page {page_number} after the last known page")
    print("=" * 60 + "\n", flush=True)


def print_http_5xx_job_deferred(status, job_url: str, page_number) -> None:
    print("\n" + "=" * 60)
    print("[PERSISTENT 5xx - JOB DEFERRED]\n")
    print(f"Status        : {status}")
    print(f"Job URL       : {job_url}")
    print(f"Listing Page  : {page_number}\n")
    print("Immediate retries exhausted.\n")
    print("Action:")
    print("1. Job added to FAILED_5XX_JOB_QUEUE")
    print("2. Continue remaining job cards")
    print("3. Retry this job after normal cards are processed")
    print("=" * 60 + "\n", flush=True)


# ---- persisted 5xx queues (plain JSON lists next to the existing state files)

def load_5xx_queue(path: str) -> list:
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_5xx_queue(path: str, items: list) -> None:
    """Atomic write (temp file + os.replace) so Ctrl+C cannot corrupt the queue."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def enqueue_5xx_item(path: str, entry: dict) -> dict:
    """Add or refresh a failed item keyed by URL. Idempotent. Returns stored entry."""
    items = load_5xx_queue(path)
    for existing in items:
        if existing.get("url") == entry.get("url"):
            existing["last_status"] = entry.get("last_status")
            existing["last_failed_at"] = now_time()
            existing["normal_attempts"] = int(existing.get("normal_attempts", 0)) + int(entry.get("normal_attempts", 0))
            save_5xx_queue(path, items)
            return existing
    entry = dict(entry)
    entry.setdefault("deferred_attempts", 0)
    entry.setdefault("first_failed_at", now_time())
    entry["last_failed_at"] = now_time()
    items.append(entry)
    save_5xx_queue(path, items)
    return entry


def remove_5xx_item(path: str, url: str) -> None:
    items = [i for i in load_5xx_queue(path) if i.get("url") != url]
    save_5xx_queue(path, items)


def update_5xx_item(path: str, entry: dict) -> None:
    items = load_5xx_queue(path)
    for idx, existing in enumerate(items):
        if existing.get("url") == entry.get("url"):
            items[idx] = entry
            break
    else:
        items.append(entry)
    save_5xx_queue(path, items)


def record_5xx_unresolved(kind: str, entry: dict) -> None:
    """Persist an item whose deferred budget is exhausted. Never silently dropped."""
    items = load_5xx_queue(UNRESOLVED_5XX_FILE)
    record = dict(entry)
    record["kind"] = kind
    record["recorded_at"] = now_time()
    items.append(record)
    save_5xx_queue(UNRESOLVED_5XX_FILE, items)
    log_access_event(
        "HTTP_5XX_UNRESOLVED", entry.get("url", ""), entry.get("last_status"),
        {"rank": rank, "city": entry.get("city", ""), "state": entry.get("state", ""),
         "role_category": entry.get("role_category", ""),
         "search_keyword": entry.get("search_keyword", ""),
         "page_number": entry.get("page_number", "")},
        nav_type=kind, job_url=entry.get("url", "") if kind == "JOB_DETAIL" else "",
        deferred_attempt=entry.get("deferred_attempts", ""),
        action=f"deferred budget exhausted; recorded in {UNRESOLVED_5XX_FILE}",
    )


async def validate_listing_page(page, url: str, status, context: dict) -> bool:
    """A recovered listing page must be a real Naukri search page, not just 200."""
    if status is None or status >= 400:
        return False
    if await detect_security_challenge(page, url, status, context):
        return False
    try:
        landed = page.url or ""
        parsed = urlparse(landed)
    except Exception:
        return False
    if "naukri.com" not in parsed.netloc.lower():
        return False
    if "jobs" not in parsed.path.lower():
        return False
    return True


async def detect_security_challenge(page, url: str, status, context: dict) -> bool:
    """Log-only check that a non-403 response looks like a Naukri page.

    An HTTP 200 does not prove the job page loaded. If the tab is off
    naukri.com or the title is a known challenge/interstitial, the event is
    recorded separately so it can be investigated. Nothing is bypassed and
    the caller's normal logic still runs (the stale-page guard and the
    zero-job checks remain the final word on the content).
    """
    try:
        landed = page.url or ""
        host = urlparse(landed).netloc.lower()
        title = (await page.title()) or ""
    except Exception:
        return False

    title_l = title.lower()
    off_site = bool(host) and "naukri.com" not in host
    challenge = any(marker in title_l for marker in SECURITY_CHALLENGE_TITLE_MARKERS)
    if not (off_site or challenge):
        return False

    reason = "off-site redirect" if off_site else f"challenge title: {title[:80]!r}"
    print(f"  [SECURITY PAGE] HTTP {status} but page is not a normal Naukri page "
          f"({reason}). Not bypassed; continuing with existing checks.", flush=True)
    log_access_event(
        "SECURITY_CHALLENGE", url, status, context,
        landed_url=landed, action=f"logged only ({reason})",
    )
    return True


async def safe_naukri_navigate(page, url: str, *, wait_until="domcontentloaded",
                               timeout=60000, settle_ms=0, context=None,
                               nav_type="LISTING_PAGE", job_url=""):
    """Navigate to a Naukri URL with bounded HTTP 403 recovery.

    Normal path is identical to the old inline code: battery wait, internet
    wait, page.goto(), optional settle wait, return the main-document
    response. Network exceptions propagate unchanged so callers' existing
    network-error handlers keep working.

    On HTTP 403 the SAME url is retried after HTTP_403_COOLDOWNS_SECONDS
    [attempt-1]; after HTTP_403_MAX_RETRIES consecutive 403s
    NaukriAccessDenied is raised. Nothing here writes checkpoint state.

    On HTTP 429 the SAME url is retried after Retry-After when usable, else
    HTTP_429_COOLDOWNS_SECONDS[attempt-1]; after HTTP_429_MAX_RETRIES
    consecutive rate-limit attempts NaukriRateLimited is raised. A response
    that follows a 429 must also validate as a Naukri page before the 429
    counter resets. The two counters and policies are independent.

    On HTTP 500/502/503/504 the SAME url is retried after ~5/10/20/40 s with
    jitter; after HTTP_5XX_MAX_IMMEDIATE_RETRIES NaukriServerError is raised so
    the caller can defer the item. Not a stop, not a network error.
    """
    consecutive_403 = 0
    consecutive_429 = 0
    consecutive_5xx = 0
    while True:
        wait_for_battery()
        wait_for_internet()
        response = await page.goto(url, wait_until=wait_until, timeout=timeout)
        status = response.status if response is not None else None
        landed = ""
        try:
            landed = response.url if response is not None else page.url
        except Exception:
            pass

        if status == HTTP_403_STATUS:
            consecutive_403 += 1
            ctx = context or current_checkpoint_context()
            if consecutive_403 > HTTP_403_MAX_RETRIES:
                log_access_event(
                    "HTTP_403_STOP", url, status, ctx, landed_url=landed,
                    attempt=consecutive_403, action="retries exhausted; stopping",
                )
                raise NaukriAccessDenied(url, HTTP_403_MAX_RETRIES, ctx)

            cooldown = HTTP_403_COOLDOWNS_SECONDS[consecutive_403 - 1]
            print_http_403_banner(url, ctx, consecutive_403, cooldown)
            log_access_event(
                "HTTP_403", url, status, ctx, landed_url=landed,
                attempt=consecutive_403, cooldown_seconds=cooldown,
                action="state preserved; cooldown then retry same URL",
            )
            resume_at = datetime.fromtimestamp(time.time() + cooldown)
            print(f"  Paused. Retrying the same URL at "
                  f"{resume_at.strftime('%H:%M:%S')}", flush=True)
            await asyncio.sleep(cooldown)
            continue

        if status in HTTP_5XX_STATUSES:
            consecutive_5xx += 1
            ctx = context or current_checkpoint_context()
            if consecutive_5xx > HTTP_5XX_MAX_IMMEDIATE_RETRIES:
                log_access_event(
                    "HTTP_5XX_EXHAUSTED", url, status, ctx, landed_url=landed,
                    nav_type=nav_type, job_url=job_url, attempt=consecutive_5xx - 1,
                    action="immediate retries exhausted; caller defers item",
                )
                raise NaukriServerError(url, status, HTTP_5XX_MAX_IMMEDIATE_RETRIES, ctx)
            delay, jitter = http_5xx_backoff_seconds(consecutive_5xx - 1)
            print_http_5xx_retry_banner(url, status, ctx, nav_type, consecutive_5xx,
                                        delay, job_url)
            log_access_event(
                "HTTP_5XX", url, status, ctx, landed_url=landed, nav_type=nav_type,
                job_url=job_url, attempt=consecutive_5xx, cooldown_seconds=round(delay, 1),
                jitter_seconds=round(jitter, 2), action="backoff then retry same URL",
            )
            await asyncio.sleep(delay)
            continue

        if status != HTTP_429_STATUS and settle_ms:
            await page.wait_for_timeout(settle_ms)

        if consecutive_5xx:
            ctx = context or current_checkpoint_context()
            print(f"  [HTTP 5xx - RECOVERED] URL loaded with HTTP {status} after "
                  f"{consecutive_5xx} short retry(ies).", flush=True)
            log_access_event("HTTP_5XX_RECOVERED", url, status, ctx, landed_url=landed,
                             nav_type=nav_type, job_url=job_url, attempt=consecutive_5xx,
                             action="same URL loaded during immediate retry")
            consecutive_5xx = 0

        # Content validation for anything that is not a 4xx/5xx. Log-only on
        # the normal path; decisive only when recovering from a 429.
        challenge = False
        if status is not None and status < 400 and status != HTTP_429_STATUS:
            challenge = await detect_security_challenge(
                page, url, status, context or current_checkpoint_context()
            )

        invalid_after_429 = bool(consecutive_429) and status != HTTP_429_STATUS and (
            status is None or status >= 400 or challenge
        )

        if status == HTTP_429_STATUS or invalid_after_429:
            consecutive_429 += 1
            ctx = context or current_checkpoint_context()
            if consecutive_429 > HTTP_429_MAX_RETRIES:
                log_access_event(
                    "HTTP_429_STOP", url, status, ctx, landed_url=landed,
                    attempt=consecutive_429, action="retries exhausted; stopping",
                )
                raise NaukriRateLimited(url, HTTP_429_MAX_RETRIES, ctx)

            retry_after_raw = None
            retry_after_seconds, note = None, "not provided"
            if status == HTTP_429_STATUS:
                retry_after_raw = _response_header(response, "Retry-After")
                retry_after_seconds, note = parse_retry_after(retry_after_raw)
                if retry_after_raw is not None and retry_after_seconds is None:
                    print(f"  [HTTP 429] Retry-After header unusable ({note}); "
                          "using configured fallback cooldown.", flush=True)
            else:
                print(f"  [HTTP 429 - RECOVERY NOT VALID] Retry returned HTTP {status} "
                      "but not a normal Naukri page; treating as still rate-limited.",
                      flush=True)

            if retry_after_seconds is not None:
                cooldown = retry_after_seconds
            else:
                cooldown = HTTP_429_COOLDOWNS_SECONDS[consecutive_429 - 1]

            print_http_429_banner(url, ctx, consecutive_429, cooldown,
                                  retry_after_raw, retry_after_seconds)
            log_access_event(
                "HTTP_429" if status == HTTP_429_STATUS else "HTTP_429_INVALID_RECOVERY",
                url, status, ctx, landed_url=landed,
                attempt=consecutive_429, cooldown_seconds=cooldown,
                retry_after_raw=retry_after_raw if retry_after_raw is not None else "",
                retry_after_seconds=retry_after_seconds if retry_after_seconds is not None else "",
                action=f"checkpoint preserved; cooldown ({note}) then retry same URL",
            )
            resume_at = datetime.fromtimestamp(time.time() + cooldown)
            print(f"  Paused. Retrying the same URL at "
                  f"{resume_at.strftime('%H:%M:%S')}", flush=True)
            await asyncio.sleep(cooldown)
            continue

        if consecutive_429:
            ctx = context or current_checkpoint_context()
            print(f"  [HTTP 429 - RECOVERED] URL loaded with HTTP {status} and validated "
                  f"after {consecutive_429} cooldown(s). Resuming where paused.", flush=True)
            log_access_event(
                "HTTP_429_RECOVERED", url, status, ctx, landed_url=landed,
                attempt=consecutive_429, action="same URL loaded and validated; counter reset",
            )
            consecutive_429 = 0

        if consecutive_403:
            ctx = context or current_checkpoint_context()
            print(f"  [HTTP 403 - RECOVERED] URL loaded with HTTP {status} after "
                  f"{consecutive_403} cooldown(s). Resuming where paused.", flush=True)
            log_access_event(
                "HTTP_403_RECOVERED", url, status, ctx, landed_url=landed,
                attempt=consecutive_403, action="same URL loaded; counter reset",
            )
            consecutive_403 = 0

        if status is not None and status >= 400:
            ctx = context or current_checkpoint_context()
            print(f"  [HTTP {status}] Non-403/429/5xx error status; existing logic decides.",
                  flush=True)
            log_access_event("HTTP_ERROR", url, status, ctx, landed_url=landed,
                             action="logged only")

        return response

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
OUTPUT_FILE   = "naukri_it_jobs_by_city.xlsx"

# ✅ Two separate state files instead of one
CITY_STATE_FILE = "state_city.json"    # stores: city_name, page_number
ROLE_STATE_FILE = "state_role.json"    # stores: role_category, search_keyword

JOBS_PER_PAGE = 20
WAIT_SECONDS  = 2

# --------------------------------------------------
# CITY STATE  (city name + page number)
# --------------------------------------------------

def load_city_state() -> dict:
    """
    Returns {"city_name": str, "page_number": int}.
    city_name is the actual city string e.g. "Pune".
    page_number is which Naukri page we were on.
    """
    if not os.path.exists(CITY_STATE_FILE):
        return {"city_name": None, "page_number": 1}
    try:
        with open(CITY_STATE_FILE) as f:
            data = json.load(f)
        return {
            "city_name":   data.get("city_name", None),
            "page_number": int(data.get("page_number", 1)),
        }
    except Exception:
        return {"city_name": None, "page_number": 1}


def save_city_state(city_name: str, page_number: int) -> None:
    """
    Save the current city name and page number.

    state_city.json example:
    {
        "city_name": "Pune",
        "page_number": 3
    }
    """
    with open(CITY_STATE_FILE, "w") as f:
        json.dump(
            {"city_name": city_name, "page_number": page_number},
            f, indent=4
        )


def reset_city_state() -> None:
    """Reset city back to first city, page 1."""
    save_city_state(city_name=None, page_number=1)


# --------------------------------------------------
# ROLE STATE  (role_category + search_keyword)
# --------------------------------------------------

def load_role_state() -> dict:
    """
    Returns {"role_category": str, "search_keyword": str}.
    role_category is the department name e.g. "IT Department".
    search_keyword is the specific job title e.g. "Python Developer".
    """
    if not os.path.exists(ROLE_STATE_FILE):
        return {"role_category": None, "search_keyword": None}
    try:
        with open(ROLE_STATE_FILE) as f:
            data = json.load(f)
        return {
            "role_category":  data.get("role_category", None),
            "search_keyword": data.get("search_keyword", None),
        }
    except Exception:
        return {"role_category": None, "search_keyword": None}


def save_role_state(role_category: str, search_keyword: str) -> None:
    """
    Save the current role category and search keyword.

    state_role.json example:
    {
        "role_category": "IT Department",
        "search_keyword": "Python Developer"
    }
    """
    with open(ROLE_STATE_FILE, "w") as f:
        json.dump(
            {"role_category": role_category, "search_keyword": search_keyword},
            f, indent=4
        )


def reset_role_state() -> None:
    """Reset role back to first role."""
    save_role_state(role_category=None, search_keyword=None)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_cities_by_rank(all_cities: list, rank: int, num_sys: int) -> list:
    len_city  = len(all_cities)
    one_unit  = int(len_city / num_sys) + 1
    first_idx = one_unit * (rank - 1)
    last_idx  = one_unit * rank
    return all_cities[first_idx:last_idx]


def build_search_list() -> list:
    """
    Build flat list of all (city × role_category × search_keyword) combos.
    Returns list of dicts with keys:
        state, location, role_category, search_keyword
    """
    all_cities = [city for cities in city_by_states.values() for city in cities]
    all_cities = list(dict.fromkeys(all_cities))            # remove duplicates
    all_cities = get_cities_by_rank(all_cities, rank, num_sys)

    searches = []
    for role_category, job_titles in job_by_department.items():
        keywords = list(dict.fromkeys([role_category] + job_titles))
        for city in all_cities:
            real_state = city_to_state(city)
            for keyword in keywords:
                searches.append({
                    "state":          real_state,
                    "location":       city,
                    "role_category":  role_category,
                    "search_keyword": keyword,
                })

    print(f"Total combos: {len(searches):,}")
    return searches


def find_resume_index(searches: list,
                      city_state: dict,
                      role_state: dict) -> int:
    """
    Given the saved city name and role names, find the index in searches
    where we should resume.

    Matching priority:
      1. city_name + role_category + search_keyword  (exact resume point)
      2. city_name + role_category                   (first keyword of that dept in this city)
      3. city_name only                              (first keyword of first dept in this city)
      4. 0                                           (fresh start)
    """
    saved_city    = city_state.get("city_name")
    saved_cat     = role_state.get("role_category")
    saved_keyword = role_state.get("search_keyword")

    if not saved_city:
        return 0     # no saved state → start from beginning

    # Priority 1: exact match
    for idx, s in enumerate(searches):
        if (s["location"]       == saved_city
                and s["role_category"]  == saved_cat
                and s["search_keyword"] == saved_keyword):
            return idx

    # Priority 2: city + category
    for idx, s in enumerate(searches):
        if s["location"] == saved_city and s["role_category"] == saved_cat:
            return idx

    # Priority 3: city only
    for idx, s in enumerate(searches):
        if s["location"] == saved_city:
            return idx

    return 0   # fallback


def now_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def make_slug(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def clean_job_title(title: str) -> str:
    title = str(title).strip().split("\n")[0].strip()
    title = re.sub(r"\s+", " ", title)
    return title.replace("Hiring For", "").replace("Urgent Hiring", "").strip()

def clean_url(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))

def make_unique_key(role_category: str, job_title: str, location: str) -> str:
    return (normalize_text(role_category) + "|"
            + normalize_text(job_title) + "|"
            + normalize_text(location))

def build_search_url(keyword: str, location: str, page_number: int) -> str:
    kslug = make_slug(keyword)
    lslug = make_slug(location)
    base  = f"https://www.naukri.com/{kslug}-jobs-in-{lslug}"
    if page_number == 1:
        return base
    return f"{base}-{page_number}"


# --------------------------------------------------
# TOTAL JOBS / PAGES
# --------------------------------------------------

async def get_total_jobs(page) -> int:
    try:
        selectors = [
            ".styles_count-string__DlPaZ",
            ".search-result-header .count",
            "[class*='count-string']",
            "[class*='resultsCount']",
            ".results-header",
            "span.count",
            ".job-count",
        ]
        count_text = ""
        for sel in selectors:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    count_text = await el.inner_text(timeout=3000)
                    if count_text.strip():
                        break
            except Exception:
                continue

        if not count_text:
            body_text = await page.locator("body").inner_text(timeout=5000)
            m = re.search(r"\d+\s*-\s*\d+\s+of\s+([\d,]+)\s+[Jj]ob", body_text)
            if m:
                count_text = m.group(0)

        m = re.search(r"of\s+([\d,]+)", count_text.replace(",", ""))
        if m:
            return int(m.group(1).replace(",", ""))
    except Exception as e:
        print(f"    [WARN] Could not read total job count: {e}")
    return 0


def calculate_total_pages(total_jobs: int, jobs_per_page: int = JOBS_PER_PAGE) -> int:
    if total_jobs <= 0:
        return 0
    return math.ceil(total_jobs / jobs_per_page)


# --------------------------------------------------
# MASTER FILE
# --------------------------------------------------

def load_existing_master() -> pd.DataFrame:
    return safe_read_excel_or_empty(
        OUTPUT_FILE,
        MASTER_COLUMNS,
    )

def save_master(df: pd.DataFrame) -> None:
    sorted_df = df.sort_values(
        by=["state", "role_category", "location", "job_title"]
    )

    safe_to_excel(
        sorted_df,
        OUTPUT_FILE,
    )


# --------------------------------------------------
# PAGE SCRAPING
# --------------------------------------------------

async def scroll_page(page) -> None:
    for _ in range(3):
        await page.mouse.wheel(0, 3000)
        await page.wait_for_timeout(1000)

async def extract_jobs_from_page(page) -> list:
    await scroll_page(page)
    items = await page.locator("a[href*='job-listings']").evaluate_all(
        """
        (anchors) => anchors.map(a => ({
            title: (a.innerText || a.textContent || a.getAttribute("title") || "").trim(),
            url:   a.href
        }))
        """
    )
    results = []
    for item in items:
        title = clean_job_title(item.get("title", ""))
        url   = clean_url(item.get("url", ""))
        if not title or "/job-listings-" not in url or len(title) < 3:
            continue
        results.append({"job_title": title, "sample_job_url": url})
    return results


# --------------------------------------------------
# MAIN
# --------------------------------------------------

async def main():
    ALL_SEARCHES = build_search_list()
    total        = len(ALL_SEARCHES)

    # ── load existing scraped data ─────────────────────────────────────────
    master_df     = load_existing_master()
    existing_data = {}
    for _, row in master_df.iterrows():
        key = make_unique_key(
            row.get("role_category", ""),
            row.get("job_title", ""),
            row.get("location", ""),
        )
        existing_data[key] = row.to_dict()

    # ── restore position from the two state files ──────────────────────────
    city_state = load_city_state()    # {"city_name": "Pune", "page_number": 3}
    role_state = load_role_state()    # {"role_category": "IT Dept", "search_keyword": "Python Developer"}

    start_search_index = find_resume_index(ALL_SEARCHES, city_state, role_state)
    start_page_number  = city_state.get("page_number", 1)

    print(f"\nTotal search combos : {total:,}")
    print(f"Resuming at         : combo #{start_search_index + 1}/{total}")
    print(f"  city              : {city_state.get('city_name') or 'first city (fresh start)'}")
    print(f"  role_category     : {role_state.get('role_category') or '—'}")
    print(f"  search_keyword    : {role_state.get('search_keyword') or '—'}")
    print(f"  page_number       : {start_page_number}")
    print(f"Remaining combos    : {total - start_search_index:,}\n")

    async with async_playwright() as p:
        auth_file = AUTH_FILE

        if not os.path.exists(auth_file):
            raise FileNotFoundError(
                f"Authentication file not found: {auth_file}. "
                "Run save_naukri_login.py first."
            )

        browser = await p.chromium.launch(
            headless=False,
        )

        context = await browser.new_context(
            storage_state=auth_file,
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={
                "width": 1920,
                "height": 1080,
            },
        )

        page = await context.new_page()
        detail_page = await context.new_page()

        # ------------------------------------------------------------------
        # 5xx recovery helpers. Nested so they share existing_data, page and
        # detail_page without changing any existing signature.
        # ------------------------------------------------------------------
        def _page_ctx(state_name, role_category, search_keyword, location, page_number):
            return {"rank": rank, "city": location, "state": state_name,
                    "role_category": role_category, "search_keyword": search_keyword,
                    "page_number": page_number}

        async def process_deferred_jobs(page_number_hint=None):
            """FAILED_5XX_JOB_QUEUE: one bounded deferred attempt per entry."""
            queue = load_5xx_queue(FAILED_5XX_JOB_QUEUE_FILE)
            if not queue:
                return
            print(f"\n  [5xx JOB QUEUE] {len(queue)} deferred job(s) to retry", flush=True)
            for entry in queue:
                job_url = entry.get("url", "")
                input_row = entry.get("input_row") or {}
                ctx = _page_ctx(entry.get("state", ""), entry.get("role_category", ""),
                                entry.get("search_keyword", ""), entry.get("city", ""),
                                entry.get("page_number", page_number_hint))
                attempt_no = int(entry.get("deferred_attempts", 0)) + 1
                print(f"    Deferred job retry {attempt_no}/{HTTP_5XX_DEFERRED_JOB_MAX_RETRIES} "
                      f"→ {job_url}", flush=True)
                try:
                    detail_row = await scrape_job_detail_async(detail_page, job_url, input_row)
                    failed_status = None
                except NaukriServerError as srv:
                    detail_row, failed_status = None, srv.status
                if isinstance(detail_row, dict):
                    # Real success: navigated, passed the P5 job-id guard, row built.
                    append_detail_to_excel(detail_row, "current_data.xlsx")
                    remove_5xx_item(FAILED_5XX_JOB_QUEUE_FILE, job_url)
                    log_access_event("HTTP_5XX_JOB_RECOVERED", job_url, 200, ctx,
                                     nav_type="JOB_DETAIL", job_url=job_url,
                                     deferred_attempt=attempt_no,
                                     action="deferred job saved; removed from queue")
                    continue
                # Still 5xx, or the stale-page guard dropped it: not a success.
                entry["deferred_attempts"] = attempt_no
                entry["last_failed_at"] = now_time()
                if failed_status is not None:
                    entry["last_status"] = failed_status
                if attempt_no >= HTTP_5XX_DEFERRED_JOB_MAX_RETRIES:
                    remove_5xx_item(FAILED_5XX_JOB_QUEUE_FILE, job_url)
                    record_5xx_unresolved("JOB_DETAIL", entry)
                    print(f"    ⚠️  Job still failing after {attempt_no} deferred retries; "
                          f"recorded in {UNRESOLVED_5XX_FILE}, continuing.", flush=True)
                else:
                    update_5xx_item(FAILED_5XX_JOB_QUEUE_FILE, entry)
                    log_access_event("HTTP_5XX_JOB_DEFERRED_AGAIN", job_url, failed_status, ctx,
                                     nav_type="JOB_DETAIL", job_url=job_url,
                                     deferred_attempt=attempt_no, action="kept in queue")

        async def process_listing_jobs(state_name, role_category, search_keyword,
                                       location, page_number):
            """Extract and process every job card on the page that is ALREADY loaded.

            This is the original inline per-page block, moved verbatim so the
            deferred-page pass can reuse it. Only addition: a 5xx on one job's
            detail page defers that job instead of aborting the page.
            """
            jobs = await extract_jobs_from_page(page)
            print(f"    Scraped {len(jobs)} job titles")

            for job in jobs:
                job_title = job["job_title"]
                sample_job_url = job["sample_job_url"]
                key = make_unique_key(role_category, job_title, location)

                if key in existing_data:
                    try:
                        old = int(existing_data[key].get("seen_count", 0))
                    except Exception:
                        old = 0

                    existing_data[key]["seen_count"] = old + 1
                    existing_data[key]["last_seen_at"] = now_time()
                    existing_data[key]["is_active"] = 1

                    if not existing_data[key].get("sample_job_url"):
                        existing_data[key]["sample_job_url"] = sample_job_url

                else:
                     existing_data[key] = {
                         "state": state_name,
                         "role_category": role_category,
                         "job_title": job_title,
                         "location": location,
                         "search_keyword": search_keyword,
                         "sample_job_url": sample_job_url,
                         "first_seen_at": now_time(),
                         "last_seen_at": now_time(),
                         "seen_count": 1,
                         "is_active": 1,
                         "source_platform": "Naukri",
                         "source_type": "job_portal",
                     }

                input_row = {
                    "state": state_name,
                    "role_category": role_category,
                    "job_title": job_title,
                    "location": location,
                    "city": location,
                    "search_keyword": search_keyword,
                    "sample_job_url": sample_job_url,
                    "source_platform": "Naukri",
                    "source_type": "job_portal",
                    "is_fake": False,
                    "is_active": True,
                }

                try:
                    detail_row = await scrape_job_detail_async(
                        detail_page,
                        sample_job_url,
                        input_row
                    )
                except NaukriServerError as srv:
                    # One job's detail page is down: defer it, keep the other cards.
                    print_http_5xx_job_deferred(srv.status, sample_job_url, page_number)
                    enqueue_5xx_item(FAILED_5XX_JOB_QUEUE_FILE, {
                        "url": sample_job_url, "job_title": job_title,
                        "city": location, "state": state_name,
                        "role_category": role_category, "search_keyword": search_keyword,
                        "page_number": page_number, "input_row": input_row,
                        "last_status": srv.status, "normal_attempts": srv.attempts,
                    })
                    log_access_event("HTTP_5XX_JOB_DEFERRED", sample_job_url, srv.status,
                                     _page_ctx(state_name, role_category, search_keyword,
                                               location, page_number),
                                     nav_type="JOB_DETAIL", job_url=sample_job_url,
                                     attempt=srv.attempts, action="added to FAILED_5XX_JOB_QUEUE")
                    continue

                append_detail_to_excel(detail_row, "current_data.xlsx")
            updated_df = pd.DataFrame(existing_data.values())
            save_master(updated_df)
            print(f"    Saved → {OUTPUT_FILE}  |  Total unique: {len(updated_df):,}")

            # Normal cards done → retry this page's (and any older) deferred jobs.
            await process_deferred_jobs(page_number)
            return len(jobs)

        async def defer_listing_page(state_name, role_category, search_keyword, location,
                                     page_number, url, status, attempts, total_pages=None):
            """Persist a page whose immediate 5xx retries failed, then cool down."""
            page1_case = total_pages is None
            enqueue_5xx_item(FAILED_5XX_PAGE_QUEUE_FILE, {
                "url": url, "city": location, "state": state_name,
                "role_category": role_category, "search_keyword": search_keyword,
                "page_number": page_number, "total_pages": total_pages,
                "last_status": status, "normal_attempts": attempts,
            })
            ctx = _page_ctx(state_name, role_category, search_keyword, location, page_number)
            print_http_5xx_page_deferred(status, ctx, page_number, page1_case)
            log_access_event(
                "HTTP_5XX_PAGE_DEFERRED", url, status, ctx, nav_type="LISTING_PAGE",
                attempt=attempts, cooldown_seconds=HTTP_5XX_PAGE_DEFER_COOLDOWN_SECONDS,
                action=("whole search combination deferred (page 1, total pages unknown)"
                        if page1_case else "added to FAILED_5XX_PAGE_QUEUE; cooldown before next page"),
            )
            resume_at = datetime.fromtimestamp(time.time() + HTTP_5XX_PAGE_DEFER_COOLDOWN_SECONDS)
            print(f"  Cooling down until {resume_at.strftime('%H:%M:%S')} before continuing.",
                  flush=True)
            await asyncio.sleep(HTTP_5XX_PAGE_DEFER_COOLDOWN_SECONDS)

        async def process_deferred_pages():
            """FAILED_5XX_PAGE_QUEUE: one bounded deferred attempt per entry.

            A page-1 entry that loads has its remaining pages discovered from
            the real total and appended to this same queue as fresh entries,
            so no page number is ever invented.
            """
            queue = load_5xx_queue(FAILED_5XX_PAGE_QUEUE_FILE)
            if not queue:
                return
            print(f"\n  [5xx PAGE QUEUE] {len(queue)} deferred listing page(s) to retry", flush=True)
            idx = 0
            while idx < len(queue):
                entry = queue[idx]
                idx += 1
                url = entry.get("url", "")
                state_name = entry.get("state", "")
                role_category = entry.get("role_category", "")
                search_keyword = entry.get("search_keyword", "")
                location = entry.get("city", "")
                page_number = int(entry.get("page_number", 1))
                ctx = _page_ctx(state_name, role_category, search_keyword, location, page_number)
                attempt_no = int(entry.get("deferred_attempts", 0)) + 1
                print(f"\n  Deferred page retry {attempt_no}/{HTTP_5XX_DEFERRED_PAGE_MAX_RETRIES} "
                      f"→ {search_keyword} | {location} | page {page_number}\n  {url}", flush=True)
                failed_status = None
                valid = False
                try:
                    response = await safe_naukri_navigate(
                        page, url, wait_until="domcontentloaded", timeout=60000,
                        settle_ms=WAIT_SECONDS * 1000, context=ctx, nav_type="LISTING_PAGE",
                    )
                    status = response.status if response is not None else None
                    valid = await validate_listing_page(page, url, status, ctx)
                    if not valid:
                        failed_status = status
                        print(f"  [5xx QUEUE] HTTP {status} but not a valid listing page; "
                              "not counted as recovered.", flush=True)
                except NaukriServerError as srv:
                    failed_status = srv.status

                if valid:
                    if entry.get("total_pages") is None and page_number == 1:
                        # Page 1 of a deferred combination: discover the real total now.
                        total_jobs = await get_total_jobs(page)
                        total_pages = calculate_total_pages(total_jobs)
                        print(f"  Deferred combination: {total_jobs:,} jobs → {total_pages} pages")
                        for later in range(2, total_pages + 1):
                            later_url = build_search_url(search_keyword, location, later)
                            if any(q.get("url") == later_url for q in queue):
                                continue
                            later_entry = enqueue_5xx_item(FAILED_5XX_PAGE_QUEUE_FILE, {
                                "url": later_url, "city": location, "state": state_name,
                                "role_category": role_category,
                                "search_keyword": search_keyword,
                                "page_number": later, "total_pages": total_pages,
                                "last_status": None, "normal_attempts": 0,
                                "expanded_from_page1": True,
                            })
                            queue.append(later_entry)
                    await process_listing_jobs(state_name, role_category, search_keyword,
                                               location, page_number)
                    remove_5xx_item(FAILED_5XX_PAGE_QUEUE_FILE, url)
                    log_access_event("HTTP_5XX_PAGE_RECOVERED", url, 200, ctx,
                                     nav_type="LISTING_PAGE", deferred_attempt=attempt_no,
                                     action="deferred page processed; removed from queue")
                    await asyncio.sleep(WAIT_SECONDS)
                    continue

                entry["deferred_attempts"] = attempt_no
                entry["last_failed_at"] = now_time()
                if failed_status is not None:
                    entry["last_status"] = failed_status
                if attempt_no >= HTTP_5XX_DEFERRED_PAGE_MAX_RETRIES:
                    remove_5xx_item(FAILED_5XX_PAGE_QUEUE_FILE, url)
                    record_5xx_unresolved("LISTING_PAGE", entry)
                    print(f"  ⚠️  Page still failing after {attempt_no} deferred retries; "
                          f"recorded in {UNRESOLVED_5XX_FILE}, continuing.", flush=True)
                else:
                    update_5xx_item(FAILED_5XX_PAGE_QUEUE_FILE, entry)
                    log_access_event("HTTP_5XX_PAGE_DEFERRED_AGAIN", url, failed_status, ctx,
                                     nav_type="LISTING_PAGE", deferred_attempt=attempt_no,
                                     action="kept in queue")
                await asyncio.sleep(HTTP_5XX_PAGE_DEFER_COOLDOWN_SECONDS)

        for search_index in range(start_search_index, total):
            seed           = ALL_SEARCHES[search_index]
            state_name     = seed["state"]
            role_category  = seed["role_category"]
            search_keyword = seed["search_keyword"]
            location       = seed["location"]

            # ✅ Save current city + role to their respective files
            save_city_state(
                city_name   = location,
                page_number = 1,          # will be updated per page below
            )
            save_role_state(
                role_category  = role_category,
                search_keyword = search_keyword,
            )

            page1_url = build_search_url(search_keyword, location, 1)

            print(f"\n[{search_index + 1}/{total}]  {search_keyword}  |  {location}, {state_name}")
            print(f"  URL (pg 1): {page1_url}")

            try:
                await safe_naukri_navigate(
                    page, page1_url, wait_until="domcontentloaded",
                    timeout=60000, settle_ms=WAIT_SECONDS * 1000,
                )

                total_jobs = await get_total_jobs(page)

                if total_jobs == 0:
                    print("  0 jobs found — skipping")
                    # advance: this combo is done, next one starts at page 1
                    save_city_state(location, page_number=1)
                    continue

                total_pages = calculate_total_pages(total_jobs)
                print(f"  Total jobs: {total_jobs:,}  →  pages: {total_pages}")

                page_start = (
                    start_page_number
                    if search_index == start_search_index
                    else 1
                )

                for page_number in range(page_start, total_pages + 1):

                    # ✅ Update page_number in city state file every page
                    save_city_state(location, page_number)

                    if page_number > 1:
                        search_url = build_search_url(search_keyword, location, page_number)
                        print(f"\n  Page {page_number}/{total_pages}  →  {search_url}")
                        try:
                            await safe_naukri_navigate(
                                page, search_url, wait_until="domcontentloaded",
                                timeout=60000, settle_ms=WAIT_SECONDS * 1000,
                            )
                        except NaukriNavigationStop:
                            raise      # handled once, in the combo-level handler
                        except NaukriServerError as srv:
                            await defer_listing_page(
                                state_name, role_category, search_keyword, location,
                                page_number, search_url, srv.status, srv.attempts,
                                total_pages=total_pages,
                            )
                            continue   # next KNOWN page; this one is queued
                        except Exception as nav_err:
                            err_msg = str(nav_err).lower()
                            if any(k in err_msg for k in
                                   ["net::", "timeout", "connection", "network", "err_"]):
                                print(f"  [NET ERROR] {nav_err}")
                                wait_for_battery()
                                wait_for_internet()
                                print("  Retrying page after reconnect...")
                                try:
                                    await safe_naukri_navigate(
                                        page, search_url, wait_until="domcontentloaded",
                                        timeout=60000, settle_ms=WAIT_SECONDS * 1000,
                                    )
                                except NaukriNavigationStop:
                                    raise
                                except NaukriServerError as srv:
                                    await defer_listing_page(
                                        state_name, role_category, search_keyword, location,
                                        page_number, search_url, srv.status, srv.attempts,
                                        total_pages=total_pages,
                                    )
                                    continue
                                except Exception as retry_err:
                                    print(f"  Retry failed: {retry_err} — exiting")
                                    await browser.close()
                                    return
                            else:
                                print(f"  ERROR on page {page_number}: {nav_err}")
                                await browser.close()
                                return
                    else:
                        print(f"  Page 1/{total_pages}  (already loaded)")

                    jobs_on_page = await process_listing_jobs(
                        state_name, role_category, search_keyword, location, page_number
                    )

                    if jobs_on_page == 0 and page_number > 1:
                        print("  Empty page — stopping pagination early")
                        break

                    await asyncio.sleep(WAIT_SECONDS)

                # All known pages done → retry deferred 5xx pages (this combo's
                # and any older ones, incl. deferred page-1 combinations).
                await process_deferred_pages()

                # combo fully done — reset page to 1 ready for next combo
                save_city_state(location, page_number=1)

            except NaukriServerError as srv:
                # Only page 1 can raise this here: pagination and detail 5xx are
                # handled lower down. total_pages is unknown, so the WHOLE
                # combination is deferred; nothing is marked completed.
                await defer_listing_page(
                    state_name, role_category, search_keyword, location,
                    1, page1_url, srv.status, srv.attempts, total_pages=None,
                )
                continue

            except NaukriNavigationStop as stopped:
                # 403 or 429 retries exhausted. Checkpoint files still hold the
                # paused city/role/page: nothing after the failed navigation
                # ran, so nothing advanced.
                stopped.print_stop()
                try:
                    await context.close()
                except Exception:
                    pass
                await browser.close()
                return

            except Exception as e:
                err_msg = str(e).lower()
                if any(k in err_msg for k in
                       ["net::", "timeout", "connection", "network", "err_"]):
                    print(f"  [NET ERROR] {e}")
                    wait_for_battery()
                    wait_for_internet()
                    print("  Retrying same search after reconnect...")
                    continue
                else:
                    print(f"  ERROR: {e} — state saved, re-run to continue.")
                    await browser.close()
                    return

        # Final pass over anything still deferred; leftovers stay in the queue
        # files for the next run.
        await process_deferred_pages()
        await process_deferred_jobs()

        await context.close()
        await browser.close()

    # all done — reset both state files
    reset_city_state()
    reset_role_state()

    final_df = pd.DataFrame(existing_data.values())
    save_master(final_df)

    print("\n================================")
    print("DONE.")
    print(f"Output file         : {OUTPUT_FILE}")
    print(f"Total unique entries: {len(final_df):,}")
    print("================================")




# ===========================================================================
# TARGET_AUDIENCE_ROLE_PLAN_APPLIED
# ---------------------------------------------------------------------------
# The portal serves one audience: IT infrastructure and operations people
# (support/help desk, network/infrastructure, system/server, cloud/DevOps),
# defined in target_audience.txt in the website repository.
#
# This block makes the crawl plan 80% target-audience roles and 20% other
# high-demand Indian IT roles, and stops non-IT jobs being fetched at all.
# It wraps the existing logic instead of rewriting it, and re-running the
# patcher is a no-op because of the marker above.
# ===========================================================================
try:
    from target_audience_roles import (
        build_role_plan,
        is_non_it_title,
        role_plan_split,
    )
except ImportError:
    build_role_plan = None
    is_non_it_title = None
    role_plan_split = None

if build_role_plan is not None:

    # -- 1) Role plan replaces the 432-entry IT list ------------------------
    # The list imported from new_mylib.py is kept there untouched; only what
    # this script searches for is narrowed.
    job_by_department = {"IT Department": build_role_plan()}

    # -- 2) Drop the bare department keyword --------------------------------
    # build_search_list() searches the category name itself as a keyword:
    #
    #     keywords = list(dict.fromkeys([role_category] + job_titles))
    #
    # That bare "IT Department" search returns whatever Naukri chooses to
    # show, which is one of the ways non-IT jobs reached the portal. The
    # combination is removed here rather than by editing the loop.
    _TA_PREV_BUILD_SEARCH_LIST = build_search_list

    def build_search_list() -> list:
        """Original combinations, minus the broad department keyword."""
        searches = _TA_PREV_BUILD_SEARCH_LIST()
        kept = []
        for item in searches:
            keyword = str(item.get("search_keyword", "")).strip().lower()
            category = str(item.get("role_category", "")).strip().lower()
            if keyword and keyword == category:
                continue
            kept.append(item)
        removed = len(searches) - len(kept)
        if removed:
            print(
                "\U0001f6ab Removed %d broad department search(es)." % removed,
                flush=True,
            )
        return kept

    # -- 3) Reject non-IT titles before anything is saved -------------------
    _TA_PREV_APPEND_DETAIL_TO_EXCEL = append_detail_to_excel

    def append_detail_to_excel(row, output_file=DETAIL_OUTPUT_FILE,
                               cycle_size=100):
        """Skip non-IT rows, then save exactly as before."""
        try:
            title = row.get("job_title", "")
        except AttributeError:
            title = ""
        if title and is_non_it_title(title):
            print(
                "\U0001f6ab Skipped non-IT job: %s" % str(title)[:70],
                flush=True,
            )
            return None
        return _TA_PREV_APPEND_DETAIL_TO_EXCEL(row, output_file, cycle_size)

    _TA_TARGET, _TA_OTHER, _TA_PERCENT = role_plan_split()
    print(
        "\U0001f3af Target-audience role plan active: %d target + %d other IT "
        "role(s) = %.1f%% target." % (_TA_TARGET, _TA_OTHER, _TA_PERCENT),
        flush=True,
    )




# ===========================================================================
# P1_PER_JOB_SOURCE_URL_APPLIED
# ---------------------------------------------------------------------------
# Every row used to be written with the same constant source_url:
#
#     "source_url": "https://www.naukri.com",      <- find_naukri_job.py:507
#
# jobs/models.py declares
#
#     UniqueConstraint(fields=["source_url"],
#                      condition=Q(source_url__isnull=False),
#                      name="unique_job_source_url_when_available")
#
# One Naukri row claimed that constant on 2026-08-21, so every Naukri row
# produced since then collided with it and was rejected at insert time. The
# site ended up with exactly one Naukri job while the scrapers kept running
# normally.
#
# The correct per-job value was already in hand. scrape_job_detail_async()
# receives the job's own detail page URL as its `url` argument and already
# uses it for internal_job_id (line 480) and the experience range (line 477);
# it simply was not used for source_url.
#
# Per section 2.2 of docs/JOB_FETCHING_SCRIPT_CONTRACT.md this is applied as
# a wrapper placed before __main__, not as an edit to the working function,
# so line 507 is left untouched and the change is purely additive. The marker
# above makes re-running the patcher a no-op.
# ===========================================================================
_P1_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, with the job's own URL stored as source_url."""
    row = await _P1_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)
    if isinstance(row, dict):
        row["source_url"] = clean_value(url)
    return row


print("\U0001f517 Per-job source_url active (P1).", flush=True)




# ===========================================================================
# P1A_EXCEL_ILLEGAL_CHARACTER_FIX_APPLIED
# ---------------------------------------------------------------------------
# One malformed job used to kill the whole scraper.
#
# openpyxl refuses a small set of ASCII control characters and raises
#
#     IllegalCharacterError(f"{value} cannot be used in worksheets.")
#         openpyxl/cell/cell.py line 165
#         ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
#
# Some Naukri job descriptions contain one of those characters. The exception
# was raised inside df.to_excel() in safe_to_excel(), escaped
# append_detail_to_excel(), and unwound to the main loop, where it either
# ended the process or retried the same search. Because the crawl position is
# saved per PAGE (save_city_state at line 956, before the page's jobs are
# scraped), the restart re-scraped and re-appended every job already written
# from that page, then hit the same bad job and crashed again -- a permanent
# crash / restart / duplicate loop. Rank 1 logged 7,603 crashes and 7,603
# restarts, and its working file held 81 rows made up of only 6 distinct jobs.
#
# Layer 1 -- remove only what Excel cannot store, before writing.
#   Applies to string cells only. The character class below is copied from
#   openpyxl, so TAB (0x09), NEWLINE (0x0A) and CARRIAGE RETURN (0x0D) are
#   deliberately NOT in it and survive untouched, as does every character
#   above 0x1F -- all normal Unicode, punctuation and accented text is
#   preserved. Numeric cells are not touched at all.
#
# Layer 2 -- a safety net, so this class of fault can never again stop a run.
#   If a row still cannot be written, only that job is skipped, loudly. Only
#   IllegalCharacterError is caught; every other error propagates exactly as
#   before, so genuine faults such as a full disk are not masked.
#
# Per section 2.2 of docs/JOB_FETCHING_SCRIPT_CONTRACT.md both layers are
# wrappers placed before __main__; no existing function body is edited. The
# marker above makes re-running the patcher a no-op.
# ===========================================================================
try:
    from openpyxl.utils.exceptions import IllegalCharacterError as _P1A_ILLEGAL_ERR
except ImportError:                                    # pragma: no cover
    class _P1A_ILLEGAL_ERR(Exception):
        pass

# Exactly the character class openpyxl rejects. Nothing else is removed.
_P1A_ILLEGAL_XLSX_CHARS = re.compile(r"[\000-\010\013-\014\016-\037]")


def _p1a_clean_text(value):
    """Strip only Excel-illegal control characters from a string value."""
    if isinstance(value, str) and _P1A_ILLEGAL_XLSX_CHARS.search(value):
        return _P1A_ILLEGAL_XLSX_CHARS.sub("", value)
    return value


_P1A_PREV_SAFE_TO_EXCEL = safe_to_excel


def _p1a_needs_cleaning(value):
    """True only for a string that actually holds an Excel-illegal character."""
    return isinstance(value, str) and bool(_P1A_ILLEGAL_XLSX_CHARS.search(value))


def safe_to_excel(df, file_path):
    """Sanitise string cells, then save exactly as before."""
    try:
        columns = list(df.columns)
    except AttributeError:
        return _P1A_PREV_SAFE_TO_EXCEL(df, file_path)

    cleaned_cells = 0
    cleaned_df = None

    # Every column is scanned by VALUE, not by dtype. pandas 3 stores text as
    # the "str" dtype rather than "object", so a dtype test would silently
    # skip exactly the description column this fix exists for. Non-string
    # values are passed through untouched by _p1a_clean_text(), so numeric
    # columns cannot be altered.
    for column in columns:
        original = df[column]
        changed = int(original.map(_p1a_needs_cleaning).sum())
        if changed:
            if cleaned_df is None:
                cleaned_df = df.copy()
            cleaned_df[column] = original.map(_p1a_clean_text)
            cleaned_cells += changed

    if cleaned_cells:
        print(
            "      \U0001f9f9 Removed Excel-illegal control characters from "
            "%d cell(s) before saving %s." % (cleaned_cells, file_path),
            flush=True,
        )

    return _P1A_PREV_SAFE_TO_EXCEL(
        cleaned_df if cleaned_df is not None else df,
        file_path,
    )


_P1A_PREV_APPEND_DETAIL_TO_EXCEL = append_detail_to_excel


def append_detail_to_excel(row, output_file=DETAIL_OUTPUT_FILE, cycle_size=100):
    """Append as before; skip only this job if Excel still refuses the row."""
    try:
        return _P1A_PREV_APPEND_DETAIL_TO_EXCEL(row, output_file, cycle_size)
    except _P1A_ILLEGAL_ERR as error:
        try:
            title = str(row.get("job_title", ""))[:80]
            job_url = str(row.get("source_url") or row.get("apply_url", ""))[:160]
        except AttributeError:
            title, job_url = "", ""
        print(
            "      \u26a0\ufe0f  SKIPPED ONE JOB - Excel refused the row even after "
            "sanitising.\n"
            "         title : %s\n"
            "         url   : %s\n"
            "         reason: %s\n"
            "         The scraper is continuing with the next job."
            % (title, job_url, type(error).__name__),
            flush=True,
        )
        return None


print("\U0001f9f9 Excel illegal-character guard active (P1A).", flush=True)




# ===========================================================================
# P2_COMPANY_NAME_FIX_APPLIED
# ---------------------------------------------------------------------------
# company_name was both MISSING and WRONG.
#
# The original extraction (line 410) was:
#
#     company_name = (
#         await async_dom_text(page, "a[class*='comp-name']",
#                                    "[class*='company-name']",
#                                    "[class*='compName']")
#         or clean_value(input_row.get("company_name"))
#     )
#
# Two faults, both measured on live pages rather than assumed:
#
#   1. "a[class*='comp-name']" matches nothing on the current Naukri layout -
#      which is also why company_website came out empty on 100% of rows.
#   2. "[class*='company-name']" DOES match, but it matches the recommended
#      jobs widget further down the page, not the job being scraped. Probing
#      12 live pages across all 5 ranks gave 2 blank and, of the 10 with a
#      value, 8 naming a completely different company - a Han Digital
#      Solution job stored as "Cognizant", an Artex Risk Solutions job stored
#      as "Cardinal Health", and so on.
#
# The fallback on input_row can never help: input_row is built in the main
# loop and has no "company_name" key.
#
# Trustworthy sources, in the order used below:
#
#   1. JSON-LD JobPosting.hiringOrganization - correct on 12 of 12 probed
#      pages, always agreeing with the page <title>, and already clean.
#   2. The job-detail header - correct on 12 of 12, but rendered as
#      "TekWissen 4.92.1K Reviews", so the rating/review tail is trimmed.
#   3. Nothing. The job is then SKIPPED rather than saved with a wrong or
#      empty company.
#
# The URL slug was tested as a candidate and REJECTED: isolating the company
# portion needs the title and city boundaries to be guessed, and the two
# authoritative sources above already cover every page seen.
#
# Per section 2.2 of docs/JOB_FETCHING_SCRIPT_CONTRACT.md this is applied as
# wrappers placed before __main__; no existing function body is edited.
# ===========================================================================

# "TekWissen 4.92.1K Reviews" -> "TekWissen".  Anchored at the end so a
# company whose own name contains digits (for example "3i Infotech") is safe.
_P2_REVIEW_SUFFIX = re.compile(
    r"\s+[\d.]+[KkMm]?\s*Reviews?\s*$", re.IGNORECASE
)


def _p2_tidy_company(value):
    """Trim the rating/review tail the detail header appends."""
    text = clean_text(value)
    previous = None
    while text and text != previous:
        previous = text
        text = _P2_REVIEW_SUFFIX.sub("", text).strip()
    return text


async def _p2_company_from_page(page):
    """Return a trustworthy company name for the job now loaded, or ""."""
    # 1) JSON-LD JobPosting.hiringOrganization
    try:
        json_ld = await extract_json_ld_async(page)
        organisation = (json_ld or {}).get("hiringOrganization")
        if isinstance(organisation, dict):
            name = clean_text(organisation.get("name"))
        elif isinstance(organisation, str):
            name = clean_text(organisation)
        else:
            name = ""
        if name:
            return name
    except Exception:
        pass

    # 2) the job-detail header, minus its review tail
    try:
        header = await async_dom_text(
            page,
            "div[class*='jd-header-comp-name']",
            "[class*='styles_jd-header-comp-name']",
        )
        name = _p2_tidy_company(header)
        if name:
            return name
    except Exception:
        pass

    # 3) nothing trustworthy
    return ""


_P2_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, with company_name taken from a trusted source."""
    row = await _P2_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)
    if isinstance(row, dict):
        # The page is still the job's detail page, so it can be re-read.
        row["company_name"] = await _p2_company_from_page(page)
    return row


_P2_PREV_APPEND_DETAIL_TO_EXCEL = append_detail_to_excel


def append_detail_to_excel(row, output_file=DETAIL_OUTPUT_FILE, cycle_size=100):
    """Skip a job with no trustworthy company; otherwise save as before."""
    if isinstance(row, dict):
        company = clean_text(row.get("company_name"))
        if not company:
            print(
                "      \u26a0\ufe0f  Skipped job with no trustworthy company name: %s"
                % str(row.get("job_title", ""))[:70],
                flush=True,
            )
            return None
    return _P2_PREV_APPEND_DETAIL_TO_EXCEL(row, output_file, cycle_size)


print("\U0001f3e2 Company-name source fixed: JSON-LD first (P2).", flush=True)




# ===========================================================================
# P3_CITY_STATE_FIX_APPLIED
# ---------------------------------------------------------------------------
# city and state described the SEARCH, not the job.
#
#     "location": location_text,                                   <- the job
#     "city":  clean_value(input_row.get("city") or input_row.get("location")),
#     "state": clean_value(input_row.get("state")),                 <- the search
#
# input_row is built in the main loop from the crawl plan, so `city` was
# whichever city the scraper happened to be searching. Measured on 255 live
# rows: 111 (43.5%) carried a city that appears nowhere in the job's own
# location. Rank 4 was crawling Rajahmundry and saved Pune, Hyderabad, Noida,
# Bengaluru and New Delhi jobs as "Rajahmundry, Andhra Pradesh"; rank 5 was
# crawling Vasco da Gama and saved Pune and Gurugram jobs as "Vasco da Gama,
# Goa". In the database all 1,030 Naukri rows sat under just six cities - the
# six the fleet happened to be crawling.
#
# Resolution order, each step verified against live pages before being used:
#
#   1. JSON-LD jobLocation.address.addressLocality. Present on every page
#      probed, and already a clean LIST of names, so no comma parsing and no
#      "( Viman Nagar )" area suffix to strip.
#   2. The location text the scraper already reads from the page, first entry.
#   3. Alias normalisation, so the existing city_to_state() can resolve names
#      it does not hold - it knows "Bengaluru" but not "Bangalore", and
#      "Delhi" but not "New Delhi".
#   4. state comes from the existing city_to_state() helper in new_mylib.
#      Where it cannot resolve one, state is left blank rather than filled
#      with the search state. state is null=True and 17 rows already have no
#      state, so blank is a value the site already handles; "Other" is not -
#      no row on the site uses it.
#   5. The search city and state remain the final fallback, used only when the
#      page yielded NO location at all. They are deliberately NOT used when a
#      location was found but is not a mappable Indian city ("Remote",
#      "Dubai"), because storing the search city there is the very defect
#      this fix exists to remove.
#
# MULTI-CITY JOBS: `city` is a single value by the site's own convention - of
# more than 70,000 rows, none contains a comma - and it is indexed and used
# for filtering. The first locality is therefore stored as the primary city
# and the complete list stays in `location`, which is unchanged.
#
# NOT CHANGED: `location`, which already held the job's real location, and
# the strict target-city filtering and fallback semantics the contract
# protects in section 2.3.
#
# Per section 2.2 of docs/JOB_FETCHING_SCRIPT_CONTRACT.md this is a wrapper
# placed before __main__; no existing function body is edited.
# ===========================================================================

# Only genuine aliases for the same place. Each maps to the spelling the
# existing city_to_state() helper actually holds, so state resolution works.
_P3_CITY_ALIASES = {
    "bangalore": "Bengaluru", "bangaluru": "Bengaluru",
    "bengalooru": "Bengaluru", "blr": "Bengaluru",
    "mysore": "Mysuru", "mangalore": "Mangaluru",
    "gurgaon": "Gurugram",
    "new delhi": "Delhi", "delhi / ncr": "Delhi", "delhi/ncr": "Delhi",
    "delhi ncr": "Delhi", "ncr": "Delhi",
    "bombay": "Mumbai", "madras": "Chennai", "calcutta": "Kolkata",
    "cochin": "Kochi", "ernakulam": "Kochi",
    "trivandrum": "Thiruvananthapuram",
    "vizag": "Visakhapatnam", "pondicherry": "Puducherry",
    "baroda": "Vadodara", "poona": "Pune",
    "trichy": "Tiruchirappalli", "tiruchi": "Tiruchirappalli",
    "gauhati": "Guwahati", "banaras": "Varanasi", "benares": "Varanasi",
}


def _p3_normalise_city(name):
    """Trim an '( area )' suffix, tidy spacing, and apply alias correction."""
    text = clean_text(name)
    if not text:
        return ""
    text = re.sub(r"\(.*?\)", " ", text)
    text = " ".join(text.split()).strip(" -,")
    if not text:
        return ""
    return _P3_CITY_ALIASES.get(text.lower(), text)


def _p3_cities_from_json_ld(json_ld):
    """Ordered city list from jobLocation.address.addressLocality."""
    places = (json_ld or {}).get("jobLocation")
    if not isinstance(places, list):
        places = [places]

    cities = []
    for place in places:
        if not isinstance(place, dict):
            continue
        address = place.get("address")
        if not isinstance(address, dict):
            continue
        locality = address.get("addressLocality")
        if isinstance(locality, str):
            locality = [locality]
        if not isinstance(locality, list):
            continue
        for entry in locality:
            city = _p3_normalise_city(entry)
            if city and city not in cities:
                cities.append(city)
    return cities


def _p3_city_from_location_text(location_text):
    """First city of the location text the scraper already read."""
    text = clean_text(location_text)
    if not text:
        return ""
    return _p3_normalise_city(text.split(",")[0])


_P3_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, with the job's own city and state."""
    row = await _P3_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)
    if not isinstance(row, dict):
        return row

    cities = []
    try:
        cities = _p3_cities_from_json_ld(await extract_json_ld_async(page))
    except Exception:
        cities = []

    if not cities:
        city = _p3_city_from_location_text(row.get("location"))
        if city:
            cities = [city]

    if cities:
        primary = cities[0]
        row["city"] = primary
        try:
            state = city_to_state(primary)
        except Exception:
            state = "Other"
        # Blank rather than the search state, which would be a guess.
        row["state"] = "" if not state or state == "Other" else state
    # No location at all -> the search city and state stay, as the last resort.

    return row


print("\U0001f4cd City and state now come from the job (P3).", flush=True)




# ===========================================================================
# P4_URL_LENGTH_FIX_APPLIED
# ---------------------------------------------------------------------------
# Job URLs could exceed the field length and lose the whole row.
#
# jobs/models.py declares both of these as URLField, whose Django default
# max_length is 200:
#
#     apply_url  = models.URLField(blank=True, null=True)
#     source_url = models.URLField(blank=True, null=True)
#
# A Naukri detail URL carries the job title, the company and every listed
# city in its slug, so it grows without bound:
#
#   .../job-listings-territory-business-executive-medigreen-pharmaceuticals-
#      panaji-vasco-da-gama-margao-tiruchirappalli-howrah-vellore-haridwar-
#      kolkata-siliguri-sonipat-ahmedabad-bengaluru-mapusa-gandhinagar-guntur-
#      hyderabad-junagadh-0-to-3-years-060325504947                (274 chars)
#
# In the current output the longest is 256 and 4 rows of 221 (1.8%) are over
# the limit. apply_url and source_url are identical on 100% of rows, because
# apply_url falls back to the detail URL (line 470-473) and P1 sets
# source_url to the same value - so BOTH fields fail together, in one error
# message, and the row is rejected. Fixing only apply_url would leave the row
# still failing on source_url, so both are handled here.
#
# THE URL IS NEVER TRUNCATED. Naukri's canonical short form is used instead:
#
#     https://www.naukri.com/job-listings-<job id>        48 characters
#
# Proven on live pages before being adopted: for every long URL tested, the
# short form loaded the same job and the JSON-LD "identifier" matched the
# original exactly. The singular "job-listing-<id>" returns "Naukri - 404
# Error Found" and is deliberately not used.
#
# The id is taken from the URL STRING, not from row["internal_job_id"].
# That field loses a leading zero on its way through the spreadsheet - the
# validation log shows internal_job_id 10926031783 for a job whose URL ends
# 010926031783 - and a wrong id would produce a URL for a different job or
# for none at all.
#
# Per section 2.2 of docs/JOB_FETCHING_SCRIPT_CONTRACT.md this is a wrapper
# placed before __main__; no existing function body is edited.
# ===========================================================================

# Django's URLField default. Not read from the model - the scraper has no
# access to it - but stated here so the reason for the number is explicit.
_P4_MAX_URL_LENGTH = 200

# The trailing numeric job id of a Naukri detail URL, leading zeros intact.
_P4_NAUKRI_JOB_ID = re.compile(r"-(\d{6,})$")


def _p4_short_job_url(url):
    """Naukri's canonical short URL for the same job, or "" if not derivable."""
    text = clean_value(url)
    if not text:
        return ""
    # Drop any query string or fragment before looking for the id.
    text = text.split("?")[0].split("#")[0].rstrip("/")
    match = _P4_NAUKRI_JOB_ID.search(text)
    if not match:
        return ""
    short = "https://www.naukri.com/job-listings-%s" % match.group(1)
    # A derived URL that is itself too long would defeat the purpose.
    if len(short) > _P4_MAX_URL_LENGTH:
        return ""
    return short


_P4_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, with over-long job URLs replaced, never cut."""
    row = await _P4_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)
    if not isinstance(row, dict):
        return row

    short = _p4_short_job_url(url)

    for field in ("apply_url", "source_url"):
        value = clean_value(row.get(field))
        if len(value) <= _P4_MAX_URL_LENGTH:
            continue
        if short:
            row[field] = short
            print(
                "      \U0001f517 %s was %d chars; using the canonical short URL "
                "for the same job (%d chars)." % (field, len(value), len(short)),
                flush=True,
            )
        else:
            # No id, so no valid short form. The URL is left exactly as it is
            # rather than cut into a dead link; the row will be rejected, which
            # is visible and correct, unlike a broken link that silently works.
            print(
                "      \u26a0\ufe0f  %s is %d chars and no job id could be read from "
                "the URL, so it was left intact rather than truncated: %s"
                % (field, len(value), value[:80]),
                flush=True,
            )

    return row


print("\U0001f517 Over-long job URLs use the canonical short form (P4).", flush=True)




# ===========================================================================
# P5_STALE_PAGE_GUARD_APPLIED
# ---------------------------------------------------------------------------
# A failed navigation could hand back the PREVIOUS job's page.
#
#     try:
#         await page.goto(url, wait_until="domcontentloaded", timeout=60000)
#         await page.wait_for_timeout(2000)
#     except Exception as e:
#         print(f"      [WARN] Detail page failed: {e}")     <- warns, continues
#
#     json_ld = await extract_json_ld_async(page)             <- reads the tab
#
# The exception is swallowed and extraction proceeds. One tab, detail_page,
# is created once (line 906) and reused for every job, so after a failed
# goto() the tab still holds the last job that loaded. The row would then
# carry that job's title, company and description together with the
# requested job's URL, id and apply link - a record describing two jobs.
#
# STATUS WHEN THIS GUARD WAS WRITTEN: risk only, not observed.
#   - 334 rows in the live working files: 0 whose title fails to match its
#     own URL slug.
#   - 1,834 rows in the production database: 0 such mismatches.
#   - 36 rows whose company differs from the slug ALL have a matching title,
#     so they are name variants (PSRTEK vs psr-tek), not stale pages - a
#     stale page would get BOTH wrong, since both come from the same DOM.
#   - No "[WARN] Detail page failed" in any rank log during the window.
# The guard is therefore preventative, and is written so that it cannot
# change behaviour on the normal path.
#
# HOW IT GUARDS, WITHOUT A SECOND PAGE LOAD:
# Re-navigating in the wrapper would double every page load and halve the
# crawl rate. Instead, after extraction, the tab's own URL is compared with
# the requested URL by numeric job id. A failed goto() leaves the tab on the
# previous job, so the ids differ and the row is dropped. Comparing the id
# rather than the whole string tolerates Naukri's redirects and the short
# canonical form introduced by P4, which end with the same id.
#
# BOUNDED BY DESIGN: no retry, no loop, no browser restart. One comparison,
# then either the row or None. The tab is left on about:blank after a
# mismatch so a second consecutive failure is caught by the same test rather
# than inheriting an older page.
# ===========================================================================

_P5_JOB_ID = re.compile(r"-(\d{6,})$")


def _p5_job_id(url):
    """The numeric job id at the end of a Naukri URL, or "" if there is none."""
    text = clean_value(url)
    if not text:
        return ""
    text = text.split("?")[0].split("#")[0].rstrip("/")
    match = _P5_JOB_ID.search(text)
    return match.group(1) if match else ""


_P5_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, dropped if the tab is not showing that job."""
    row = await _P5_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)
    if not isinstance(row, dict):
        return row

    wanted = _p5_job_id(url)
    if not wanted:
        # No id to check against; leave the row exactly as it was.
        return row

    try:
        landed = _p5_job_id(page.url)
    except Exception:
        landed = ""

    if landed == wanted:
        return row

    print(
        "      \u26a0\ufe0f  SKIPPED ONE JOB - the browser tab is not showing it, so "
        "the page content would belong to another job.\n"
        "         wanted job id : %s\n"
        "         tab is on     : %s\n"
        "         The scraper is continuing with the next job."
        % (wanted, (landed or "an unknown page")),
        flush=True,
    )

    # Clear the tab so a further failure cannot inherit an older job either.
    try:
        await page.goto("about:blank", timeout=15000)
    except Exception:
        pass

    return None


_P5_PREV_APPEND_DETAIL_TO_EXCEL = append_detail_to_excel


def append_detail_to_excel(row, output_file=DETAIL_OUTPUT_FILE, cycle_size=100):
    """Never write a dropped row; otherwise save exactly as before."""
    if not isinstance(row, dict):
        return None
    return _P5_PREV_APPEND_DETAIL_TO_EXCEL(row, output_file, cycle_size)


print("\U0001f6e1\ufe0f  Stale detail-page guard active (P5).", flush=True)




# ===========================================================================
# P6A_SALARY_APPLIED
# ---------------------------------------------------------------------------
# Before this block the scraper never read salary from any page. It wrote a
# fixed literal on every job:
#
#     "salary_min": "not disclosed",
#     "salary_max": "not disclosed",
#     "salary_currency": "INR",
#
# so all Naukri rows reached the database with NULL salary, including the
# jobs where Naukri publishes a real figure. ("not disclosed" is in the
# validation engine's EMPTY_MARKERS, so it became NULL rather than an error -
# the pipeline was safe, just blind.) The salary_text variable a few hundred
# lines above was assigned and never read: dead code.
#
# INVESTIGATION BASIS (189 live pages, of which 187 were real job pages):
#   - 100% of real job pages carry a JSON-LD baseSalary block.
#   -  15.5% disclose a numeric salary, 84.5% say "Not Disclosed".
#   -  baseSalary.value.minValue / maxValue are NEVER populated - the figure
#      exists only as TEXT in baseSalary.value.value, so it must be parsed.
#   -  the existing [class*='salary'] selector is CONTAMINATED: it returns
#      '0 - 3 years 7-16 Lacs P.A.' - the experience glued to the salary.
#      div[class*='jhc__salary'] returns the clean '7-16 Lacs P.A.'.
#
# WHAT THIS BLOCK DOES
# Reads the salary text from the page that is ALREADY loaded - no extra
# navigation and no extra network request - parses it into absolute rupees,
# and writes salary_min / salary_max / salary_currency onto the row.
#
# ABSOLUTE RUPEES, NOT LPA. Storing the bare number 15 for "15 Lacs" is the
# defect that already damaged 413 rows on other platforms (min=8.00
# max=12.00); the site added SALARY_NOISE_FLOOR = 1000 to hide them. Lacs are
# therefore expanded by 100000 and Cr by 10000000. That is a unit expansion
# inside one period, NOT a monthly-to-annual conversion, which is forbidden -
# the website infers the period itself from magnitude
# (SALARY_ANNUAL_FLOOR = 200000).
#
# NOTHING IS EVER INVENTED. "Not Disclosed", "Unpaid", an empty value or any
# format not confidently understood leaves BOTH fields empty, which the
# validation engine stores as NULL. Never 0 - zero is a real number that
# would pass the salary slider and sort as the lowest-paid job on the site.
#
# BOUNDED BY DESIGN: pure text parsing plus one DOM read. No retry, no loop,
# no navigation, no browser restart.
# ===========================================================================


_P6A_MULTIPLIERS = {
    "lac": 100000,
    "lacs": 100000,
    "lakh": 100000,
    "lakhs": 100000,
    "cr": 10000000,
    "crore": 10000000,
    "crores": 10000000,
}

# Values that mean "there is no number here". Anything matching is left empty.
_P6A_NOT_A_NUMBER = re.compile(
    r"^(?:not\s*disclosed|undisclosed|unpaid|not\s*mentioned|not\s*available"
    r"|unknown|none|null|n\.?/?a\.?|nil|-{1,2}|as\s*per\s*industry.*"
    r"|negotiable|best\s*in\s*industry.*|confidential)$",
    re.IGNORECASE,
)

# The trailing period marker. Recorded, never used to convert.
_P6A_PERIOD_SUFFIX = re.compile(r"\s*p\.?\s*[am]\.?\s*$", re.IGNORECASE)

# Currency decoration that may appear on either side.
_P6A_CURRENCY = re.compile(r"(?:\u20b9|\bRs\.?|\bINR\b)", re.IGNORECASE)

# One side of a range: a number, optionally carrying its own unit word.
_P6A_SIDE = re.compile(
    r"^\s*([\d,]+(?:\.\d+)?)\s*(lacs?|lakhs?|crores?|cr)?\s*$",
    re.IGNORECASE,
)

_P6A_RANGE_SPLIT = re.compile(r"\s*(?:-|\u2013|\u2014|\bto\b)\s*", re.IGNORECASE)

# A side below this with no unit of its own may inherit the other side's unit.
# At or above it, the number is already written in rupees ("50,000-2 Lacs").
_P6A_UNIT_INHERIT_CEILING = 1000

# Job.salary_min / salary_max are DecimalField(max_digits=12, decimal_places=2),
# so the largest storable value is 9,999,999,999.99.
_P6A_MAX_RUPEES = 9999999999


def _p6a_side(text):
    """Return (number, unit_or_None) for one side of a range, else (None, None)."""
    match = _P6A_SIDE.match(text or "")
    if not match:
        return None, None

    try:
        number = float(match.group(1).replace(",", ""))
    except (TypeError, ValueError):
        return None, None

    unit = match.group(2)
    if unit:
        unit = unit.lower().rstrip(".")

    return number, unit


def _p6a_parse_salary(text):
    """Parse Naukri salary text into (salary_min, salary_max) absolute rupees.

    Returns (None, None) whenever there is no confidently understood number.
    Never returns 0, never guesses, never converts between periods.
    """
    raw = clean_value(text)
    if not raw:
        return None, None

    body = " ".join(raw.split())
    if _P6A_NOT_A_NUMBER.match(body):
        return None, None

    # Drop the period marker and any currency decoration.
    body = _P6A_PERIOD_SUFFIX.sub("", body).strip()
    body = _P6A_CURRENCY.sub(" ", body)
    body = " ".join(body.split())

    if not body or _P6A_NOT_A_NUMBER.match(body):
        return None, None

    parts = [part for part in _P6A_RANGE_SPLIT.split(body) if part.strip()]

    if len(parts) == 1:
        # A single value was never observed in the investigation. Accept it
        # only when it carries an explicit unit word, which removes all
        # ambiguity and uses the same multiplication rule already proven for
        # ranges. A bare unitless number is NOT proven safe, so it is left
        # empty rather than guessed.
        value, unit = _p6a_side(parts[0])
        if value is None or unit is None:
            return None, None
        low_value, low_unit = value, unit
        high_value, high_unit = value, unit

    elif len(parts) == 2:
        low_value, low_unit = _p6a_side(parts[0])
        high_value, high_unit = _p6a_side(parts[1])
        if low_value is None or high_value is None:
            return None, None

        # Unit inheritance. "15-20 Lacs" -> the bare 15 inherits Lacs.
        # "50,000-2 Lacs" -> 50,000 is already rupees and must NOT inherit,
        # or it would become fifty thousand lakhs.
        if (
            low_unit is None
            and high_unit is not None
            and low_value < _P6A_UNIT_INHERIT_CEILING
        ):
            low_unit = high_unit

        if (
            high_unit is None
            and low_unit is not None
            and high_value < _P6A_UNIT_INHERIT_CEILING
        ):
            high_unit = low_unit

    else:
        return None, None

    # Neither side carries a unit and both are tiny: almost certainly an LPA
    # figure with the word missing. Storing 5 and 9 is exactly the damage that
    # SALARY_NOISE_FLOOR exists to hide, so refuse rather than guess.
    if (
        low_unit is None
        and high_unit is None
        and max(low_value, high_value) < _P6A_UNIT_INHERIT_CEILING
    ):
        return None, None

    low = int(round(low_value * _P6A_MULTIPLIERS.get(low_unit, 1)))
    high = int(round(high_value * _P6A_MULTIPLIERS.get(high_unit, 1)))

    # Never emit zero or a negative figure; never emit an inverted pair; never
    # emit something the Decimal column cannot hold.
    if low <= 0 or high <= 0:
        return None, None
    if low > high:
        return None, None
    if high > _P6A_MAX_RUPEES:
        return None, None

    return low, high


async def _p6a_salary_text(page):
    """Salary text from the page that is ALREADY open. No navigation."""
    try:
        data = await extract_json_ld_async(page)
    except Exception:
        data = None

    if isinstance(data, dict):
        base = data.get("baseSalary")
        if isinstance(base, dict):
            value = base.get("value")
            if isinstance(value, dict):
                text = clean_value(value.get("value"))
                if text:
                    return text
            elif value is not None:
                text = clean_value(value)
                if text:
                    return text

    # Fallback: Naukri's own salary node. NOT [class*='salary'], which returns
    # the experience text glued to the salary.
    try:
        return await async_dom_text(
            page,
            "div[class*='jhc__salary']",
            "[class*='jhc__salary']",
        )
    except Exception:
        return ""


_P6A_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, with the real salary filled in when disclosed."""
    row = await _P6A_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)

    # P5 returns None for a stale page; leave that decision untouched.
    if not isinstance(row, dict):
        return row

    try:
        salary_text = await _p6a_salary_text(page)
    except Exception:
        salary_text = ""

    salary_min, salary_max = _p6a_parse_salary(salary_text)

    if salary_min is None:
        row["salary_min"] = ""
        row["salary_max"] = ""

        # Distinguish "the page says there is no salary" from "we could not
        # understand what the page said" - the second is worth reading in a log.
        # The period marker is stripped first, otherwise "Unpaid P.M" would be
        # reported as not understood when it is understood perfectly well.
        shown = clean_value(salary_text)
        probe = _P6A_PERIOD_SUFFIX.sub("", " ".join(shown.split())).strip()
        if shown and probe and not _P6A_NOT_A_NUMBER.match(probe):
            print(
                "      [P6A] salary text not understood, left empty: %r" % shown,
                flush=True,
            )
    else:
        row["salary_min"] = salary_min
        row["salary_max"] = salary_max
        print(
            "      \U0001f4b0 salary %r -> %s / %s INR"
            % (clean_value(salary_text), salary_min, salary_max),
            flush=True,
        )

    row["salary_currency"] = "INR"
    return row


print("\U0001f4b0  Salary extraction active (P6-A).", flush=True)




# ===========================================================================
# P6B_REMOTE_TYPE_APPLIED
# ---------------------------------------------------------------------------
# Before this block the scraper wrote a fixed literal on every job:
#
#     "remote_type": "Onsite",
#
# so all 8,244 Naukri rows in the database are "onsite" - zero Remote, zero
# Hybrid - while Shine/Freshersworld show 8.6% remote and 0.8% hybrid. Every
# genuinely remote or hybrid Naukri job was being mislabelled as Onsite.
#
# INVESTIGATION (45 random live job pages + 24 pages from Naukri's own
# work-from-home / remote / hybrid listings):
#
#   JSON-LD carries NO work-mode field at all.
#     jobLocationType              : absent on 45/45
#     applicantLocationRequirements: absent on 45/45
#   So the structured source used for P6-A salary does not exist here.
#
#   The ONLY trustworthy source is Naukri's dedicated work-mode chip:
#     <div class="styles_jhc__wfhmode__iQwF4">Remote</div>
#     <div class="styles_jhc__wfhmode__iQwF4">Hybrid</div>
#   Observed values: "Remote" (12) and "Hybrid" (6+5). Naukri renders this
#   chip ONLY for remote and hybrid jobs - there is no "Onsite" or "Work from
#   office" chip anywhere in the sample.
#
#   Two neighbouring nodes must NOT be used:
#     span[class*='jhc__wfht']   -> "Hiring office located in Noida"
#                                   a tooltip about the HIRING OFFICE, not the
#                                   work mode. Reading it would turn a remote
#                                   job into "Noida".
#     i[class*='ni-icon-wfh-pin'] -> an icon, always empty.
#   Selecting div[class*='jhc__wfhmode'] excludes both.
#
# WHY THE DESCRIPTION IS NEVER USED
# Keyword matching over the page text was measured and is unusable:
#   12 of 40 chip-less pages contain the word "remote"
#   17 of 40 chip-less pages contain the word "hybrid"
# Real examples that would have produced a wrong answer:
#   "hybrid or behaviour driven development (bdd)"   <- a test methodology
#   "gis remote sensing, environmental science"      <- a scientific field
#   "provide remote and onsite technical assistance" <- a job duty
#   "remote infrastructure management services"      <- a service type
#   "hybrid - hyderabad, chennai, bengaluru"         <- ANOTHER job, from the
#                                                       similar-jobs sidebar
# The last one is the worst: the recommendations panel embeds other jobs'
# work modes in the same body text, so description matching would classify a
# job by a different job's mode.
#
# NO CHIP AND UNKNOWN CHIP ARE DIFFERENT THINGS
# Job.remote_type is CharField(choices=REMOTE_TYPE_CHOICES, blank=True,
# null=True) with no default, and the validation engine maps an empty value
# to None with no error.
#
# The first version of this block stored EMPTY for a missing chip, on the
# grounds that Naukri publishes no onsite chip so absence proved nothing.
# A follow-up read-only investigation disproved that: see
# P6B_NO_CHIP_ONSITE_APPLIED below. Naukri does classify every job, and
# "Work from office" is one of its three named work modes - it simply is not
# badged on the page. A genuinely absent chip is therefore EVIDENCE of an
# onsite job, and is stored as Onsite.
#
# An UNRECOGNISED chip is still absence of evidence and still stores as
# NULL. Those two cases use different constants precisely so that a future
# edit cannot collapse them and start asserting Onsite for a work mode
# Naukri never stated.
#
# BOUNDED BY DESIGN: one DOM read on the page that is already open. No extra
# navigation, no network request, no retry, no loop.
# ===========================================================================


# Naukri's work-mode chip. Only these two values were ever observed.
_P6B_CHIP_SELECTORS = (
    "div[class*='jhc__wfhmode']",
    "a[class*='jhc__wfhmode']",
)

# Fail-safe value for a chip that IS present but cannot be trusted.
_P6B_UNKNOWN = ""

# ===========================================================================
# P6B_NO_CHIP_ONSITE_APPLIED
# ---------------------------------------------------------------------------
# Value for a chip that is genuinely ABSENT.
#
# Naukri's own "Work mode" search filter has exactly three options. Each was
# clicked and both the resulting URL and the chip on a job it returned were
# recorded, so the label, the parameter and the on-page evidence are bound in
# one chain with no assumption at any link:
#
#     "Work from office" -> wfhType=0 -> 7,391 of 8,177 jobs -> NO CHIP
#     "Hybrid"           -> wfhType=3 ->   491 jobs -> chip "Hybrid"
#     "Remote"           -> wfhType=2 ->   295 jobs -> chip "Remote"
#
# Arithmetic closes: 8,177 - (295 + 491 + 2 legacy temp-WFH) = 7,389, against
# the 7,391 that wfhType=0 returns. The no-chip set IS Naukri's "Work from
# office" bucket; Naukri badges only the two exceptional modes.
#
# Supporting per-job evidence: of 36 sampled no-chip pages, 36 named a
# physical city, 0 carried the "Hiring office located in ..." tooltip that
# remote jobs show, 0 had a JSON-LD work-mode key, and 0 showed any Remote or
# Hybrid signal.
#
# An earlier guess that wfhType=3 meant "work from office" was contradicted by
# the evidence - every job it returned carried a Hybrid chip - and was
# discarded rather than relied on. The mapping above is the measured one.
# ===========================================================================
_P6B_NO_CHIP = "Onsite"

# EXACT chip vocabulary. The chip is a short label, never a sentence, so the
# match is exact rather than a prefix or a substring. This is deliberate: with
# prefix matching, a stray "hybrid or behaviour driven development (bdd)" or
# "remote infrastructure management services" would be classified as a work
# mode. Those strings cannot reach here today, but an exact whitelist means a
# future Naukri class change cannot turn prose into a work mode either.
_P6B_CHIP_VOCABULARY = {
    "remote": "Remote",
    "work from home": "Remote",
    "wfh": "Remote",
    "hybrid": "Hybrid",
    "work from office": "Onsite",
    "onsite": "Onsite",
    "on-site": "Onsite",
    "on site": "Onsite",
    "in office": "Onsite",
    "wfo": "Onsite",
}

# A work-mode chip is a short label. Anything longer is prose, not a chip.
_P6B_MAX_CHIP_LENGTH = 24


def _p6b_resolve_remote_type(chip_text):
    """Map Naukri's work-mode chip to a JobSphere remote_type.

    A genuinely ABSENT chip means Onsite: that is Naukri's default "Work from
    office" category, established from Naukri's own work-mode filter.

    Anything present but unrecognised returns "" and is stored as NULL.
    NO CHIP and UNKNOWN CHIP must never collapse into the same answer, or a
    work mode Naukri never stated would be asserted as Onsite. The job
    description is still never read.
    """
    text = " ".join(clean_value(chip_text).split()).lower().strip(" .,:;-")

    # Genuinely absent chip -> Naukri's default work mode.
    if not text:
        return _P6B_NO_CHIP

    # Present, but too long to be a label: prose, not a chip. Fail safe.
    if len(text) > _P6B_MAX_CHIP_LENGTH:
        return _P6B_UNKNOWN

    # Present and short, but not in the vocabulary. Fail safe.
    return _P6B_CHIP_VOCABULARY.get(text, _P6B_UNKNOWN)


async def _p6b_chip_text(page):
    """Work-mode chip from the page that is ALREADY open. No navigation."""
    try:
        return await async_dom_text(page, *_P6B_CHIP_SELECTORS)
    except Exception:
        return ""


_P6B_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, with the real work mode when Naukri states it."""
    row = await _P6B_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)

    # P5 returns None for a stale page; leave that decision untouched.
    if not isinstance(row, dict):
        return row

    try:
        chip = await _p6b_chip_text(page)
    except Exception:
        chip = ""

    resolved = _p6b_resolve_remote_type(chip)
    row["remote_type"] = resolved

    shown = clean_value(chip)
    if resolved and shown:
        # A chip was on the page and was understood.
        print(
            "      \U0001f3e0 work mode %r -> %s" % (shown, resolved),
            flush=True,
        )
    elif shown:
        # A chip was present but not understood - worth seeing in the log.
        print(
            "      [P6B] work-mode chip not understood, left empty: %r" % shown,
            flush=True,
        )

    return row


print("\U0001f3e0  Work mode read from the job page (P6-B).", flush=True)



# ===========================================================================
# P6C_EMPLOYMENT_TYPE_APPLIED
# ---------------------------------------------------------------------------
# Before this block the scraper wrote a fixed literal on every single job:
#
#     "employment_type": "Full-time",
#
# so all 8,951 Naukri rows in the database are "full_time" - zero internships,
# zero contract roles, zero part-time roles - while the same database holds
# 187 contract, 47 part-time and 32 internship rows from other sources. Every
# non-full-time Naukri job was being mislabelled.
#
# INVESTIGATION (92 live job pages: 56 from ordinary searches, 36 harvested
# from searches chosen to reach job types a random sample would miss)
#
#   Naukri publishes employment type in TWO places, and they never disagreed:
#
#     1. JSON-LD  JobPosting.employmentType
#        present on 92/92 pages, always a str, never a list
#     2. DOM      the "Employment Type:" row of the other-details block
#          <div class="styles_details__Y424J">
#            <label>Employment Type:</label><span>Full Time, Permanent</span>
#          </div>
#        present on 92/92 pages
#
#     conflicts between the two: 0 of 92
#
#   Search-result cards do NOT carry employment type, so it can only be read
#   from the detail page - which is where this wrapper runs.
#
#   The complete raw vocabulary observed on 92 pages:
#
#     'Full Time, Permanent'                84
#     'Part Time, Permanent'                 3
#     'Part Time, Temporary/Contractual'     2
#     'Full Time, Temporary/Contractual'     2
#     'Part Time, Freelance/Homebased'       1
#
#   Naukri always states TWO dimensions in one comma-joined string: hours
#   (Full Time / Part Time) and tenure (Permanent / Temporary/Contractual /
#   Freelance/Homebased). Both are parsed; see the priority note below.
#
# WHY THE JOB TITLE IS NEVER USED
# Title keywords were measured against the structured field and are unusable.
# Every one of these real jobs names an employment type in its title that
# Naukri's own structured field contradicts:
#
#   'AI ML Intern'                        -> 'Full Time, Permanent'
#   'Artificial Intelligence Intern'      -> 'Full Time, Permanent'
#   'AI & Data Innovation Intern'         -> 'Full Time, Permanent'
#   'DSA Problem Setter Intern'           -> 'Full Time, Permanent'
#   'SOC Intern'                          -> 'Full Time, Permanent'
#   'AI trainee'                          -> 'Full Time, Permanent'
#   'NLP and Python Expert on Contract'   -> 'Full Time, Permanent'
#   'Temporary Faculty - German Language' -> 'Full Time, Permanent'
#   'Temporary operator'                  -> 'Full Time, Permanent'
#   'Associate Recruiter (temporary)'     -> 'Full Time, Permanent'
#   'Part time Radiologist Consultant'    -> 'Full Time, Permanent'
#   'Power BI Trainer (Part time)'        -> 'Full Time, Permanent'
#   'Back Office Operations - Part time'  -> 'Full Time, Permanent'
#   'Freelance Interior Designer'         -> 'Part Time, Permanent'
#   'Freelance Jobs Open To All'          -> 'Full Time, Permanent'
#
# Six of six internship-titled jobs and every one of the six temporary-titled
# jobs would have been classified wrongly by a title rule. The structured
# field is the only source used here.
#
# MISSING IS NOT FULL-TIME
# Job.employment_type is CharField(choices=EMPLOYMENT_TYPE_CHOICES,
# blank=True, null=True) with NO default, and the validation engine maps an
# empty value to None with no error. Unlike P6-B's work mode, Naukri exposes
# no employment-type filter and therefore no default bucket, so nothing
# proves what a missing value would mean. A missing value is stored as NULL.
#
# UNKNOWN IS NOT FULL-TIME EITHER, AND MUST NOT BE PASSED THROUGH
# admin_portal/scripts/job_validation_engine.py rejects the WHOLE ROW with
# "Invalid employment_type." if it is given a non-empty value it cannot map.
# So an unrecognised value must never be forwarded: it is stored as NULL and
# logged, which keeps the job and every other field it carries.
# ===========================================================================

# The other-details block holds five sibling rows with the SAME class -
# Role, Industry Type, Department, Employment Type, Role Category - so the
# row must be selected by its own label. A bare "label + span" would return
# "Role: Data Engineer" instead. Playwright's :has() / :has-text() pin it to
# the right row.
#
# A class-name change on Naukri would break these selectors, which is exactly
# why JSON-LD is the primary source and this is only the fallback.
_P6C_DOM_SELECTORS = (
    "div[class*='styles_details']:has(label:has-text('Employment Type'))",
    "div[class*='details']:has(label:has-text('Employment Type'))",
)

# The row reads "Employment Type: Full Time, Permanent"; drop the label.
_P6C_DOM_LABEL = re.compile(r"^\s*employment\s*type\s*:?\s*", re.I)

# Naukri joins the two dimensions with a comma, and joins alternatives within
# a dimension with a slash: "Full Time, Temporary/Contractual". Splitting on
# both yields the individual tokens.
_P6C_TOKEN_SPLIT = re.compile(r"[,/|;]+")

# EXACT token vocabulary, built ONLY from values actually observed on Naukri,
# mapped to the exact labels of Job.EMPLOYMENT_TYPE_CHOICES. The match is
# exact rather than a substring: with substring matching a description
# sentence such as "contract manufacturing services" would classify a job.
_P6C_TOKEN_VOCABULARY = {
    # --- observed on live Naukri pages ---
    "full time": "Full Time",
    "permanent": "Full Time",
    "part time": "Part Time",
    "temporary": "Temporary",
    "contractual": "Contract",
    "freelance": "Freelance",
    # --- NOT observed in employmentType on any of the 151 pages checked ---
    # Naukri does not express internships through employmentType at all: its
    # own internship-only Stipend filter (?qcstipend=unpaid) and its
    # internship / summer-internship / industrial-training listings all return
    # jobs whose employmentType is "Full Time, Permanent", including jobs
    # titled literally "Internship" and "Summer Internship". Internship-ness
    # lives in Naukri's separate Stipend and Duration attributes, which are a
    # different field and outside P6-C.
    #
    # This entry is therefore forward-compatibility only, never exercised by
    # today's Naukri. It is an identity mapping of a JobSphere canonical label
    # onto itself - it infers nothing - so if Naukri ever does publish the
    # word, the value is stored rather than dropped.
    "internship": "Internship",
}

# Observed Naukri tokens that carry no employment-type meaning. They are
# skipped in silence; anything NOT listed here and not in the vocabulary is
# genuinely unknown and is reported.
_P6C_IGNORED_TOKENS = {
    "homebased",
}

# Priority when Naukri states more than one type, which it does on every job.
# This is NOT invented here. It is the precedence already implemented twice in
# this project, in admin_portal/scripts/job_validation_engine.py and in
# admin_portal/manual_job_importer.py, both of which test in exactly this
# order and fall back to full_time last. Mirroring it means the value stored
# is the value JobSphere itself would derive from Naukri's raw string - the
# difference being that an unknown value fails safe to NULL here instead of
# rejecting the entire row there.
_P6C_PRIORITY = (
    "Internship",
    "Part Time",
    "Contract",
    "Temporary",
    "Freelance",
    "Full Time",
)

# Naukri's longest observed value is 32 characters. Anything far longer is
# prose, not a label. Exact token matching already rejects prose; this is a
# cheap second guard against a future Naukri class change feeding a
# paragraph into this function.
_P6C_MAX_LENGTH = 60

# Stored when the value is genuinely ABSENT.
_P6C_MISSING = ""

# Stored when a value IS present but cannot be trusted. Deliberately a
# separate constant from _P6C_MISSING so the two reasons stay distinguishable
# even though both currently store NULL, and so neither can ever be edited
# into "Full Time".
_P6C_UNKNOWN = ""


def _p6c_tokens(raw):
    """Split Naukri's employment-type value into normalised tokens."""
    if isinstance(raw, (list, tuple, set)):
        # schema.org allows a list. Treat it exactly like the comma string
        # Naukri actually sends, so neither form is handled by accident.
        raw = ", ".join(clean_value(item) for item in raw)

    text = " ".join(clean_value(raw).split())
    if not text or len(text) > _P6C_MAX_LENGTH:
        return None, text

    tokens = []
    for piece in _P6C_TOKEN_SPLIT.split(text.lower()):
        piece = " ".join(piece.split()).strip(" .:;-")
        if piece:
            tokens.append(piece)
    return tokens, text


def _p6c_resolve_employment_type(raw):
    """Map Naukri's employment-type value to a JobSphere employment_type.

    Returns one of the Job.EMPLOYMENT_TYPE_CHOICES labels, or "" when the
    value is missing or cannot be trusted. Never guesses, never falls back to
    Full Time, and never reads the job title or the description.
    """
    resolved, _unknown = _p6c_resolve_with_detail(raw)
    return resolved


def _p6c_resolve_with_detail(raw):
    """Resolver plus the unrecognised tokens, so the caller can report them."""
    tokens, text = _p6c_tokens(raw)

    # Genuinely absent, or too long to be a label.
    if tokens is None:
        return (_P6C_MISSING if not text else _P6C_UNKNOWN), []

    found = set()
    unknown = []
    for token in tokens:
        mapped = _P6C_TOKEN_VOCABULARY.get(token)
        if mapped:
            found.add(mapped)
        elif token not in _P6C_IGNORED_TOKENS:
            unknown.append(token)

    if not found:
        # Nothing recognised. Fail safe rather than guess.
        return _P6C_UNKNOWN, unknown

    for candidate in _P6C_PRIORITY:
        if candidate in found:
            return candidate, unknown

    return _P6C_UNKNOWN, unknown


async def _p6c_employment_text(page):
    """Employment type from the page that is ALREADY open. No navigation.

    JSON-LD first: it is a structured field, it was present on 92/92 pages,
    and it is not affected by a CSS class rename. The DOM row is the fallback
    for a page whose JSON-LD is missing or malformed.
    """
    raw = ""
    source = ""

    try:
        json_ld = await extract_json_ld_async(page)
        if isinstance(json_ld, dict):
            value = json_ld.get("employmentType")
            if isinstance(value, (list, tuple)):
                value = ", ".join(clean_value(item) for item in value)
            raw = clean_value(value)
            if raw:
                source = "json-ld"
    except Exception:
        raw = ""

    if not raw:
        try:
            dom = await async_dom_text(page, *_P6C_DOM_SELECTORS)
            dom = clean_value(dom)
            # The block reads "Employment Type: Full Time, Permanent";
            # drop the label so only the value is parsed.
            dom = _P6C_DOM_LABEL.sub("", dom).strip()
            if dom:
                raw, source = dom, "dom"
        except Exception:
            pass

    return raw, source


_P6C_PREV_SCRAPE_JOB_DETAIL_ASYNC = scrape_job_detail_async


async def scrape_job_detail_async(page, url: str, input_row: dict) -> dict:
    """Original detail scrape, with the employment type Naukri actually states."""
    row = await _P6C_PREV_SCRAPE_JOB_DETAIL_ASYNC(page, url, input_row)

    # P5 returns None for a stale page; leave that decision untouched.
    if not isinstance(row, dict):
        return row

    try:
        raw, source = await _p6c_employment_text(page)
    except Exception:
        raw, source = "", ""

    resolved, unknown = _p6c_resolve_with_detail(raw)
    row["employment_type"] = resolved

    shown = clean_value(raw)
    if resolved and shown:
        print(
            "      \U0001f4bc employment type %r -> %s (%s)"
            % (shown, resolved, source),
            flush=True,
        )
    elif shown:
        # Naukri stated something this block does not recognise. Store NULL
        # rather than guess, and say so - this is how a new Naukri value gets
        # noticed instead of silently becoming Full Time.
        print(
            "      [P6C] employment type not understood, left empty: %r"
            % shown,
            flush=True,
        )
    elif unknown:
        print(
            "      [P6C] unrecognised employment-type tokens: %r" % unknown,
            flush=True,
        )

    return row


print("\U0001f4bc  Employment type read from the job page (P6-C).", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
