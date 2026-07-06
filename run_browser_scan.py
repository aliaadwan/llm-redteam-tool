from providers.browser_provider import BrowserChatProvider
from core.scanner import run_scan
from core.report import generate_report

TARGET_URL = "https://example.com/chat"
INPUT_SELECTOR = "textarea#chat-input"
RESPONSE_SELECTOR = ".bot-message:last-child"
SEND_SELECTOR = None

provider = BrowserChatProvider(
    page_url=TARGET_URL,
    input_selector=INPUT_SELECTOR,
    response_selector=RESPONSE_SELECTOR,
    send_selector=SEND_SELECTOR,
    wait_seconds=5,
    headless=True,
)

try:
    print("Running a quick test (1 prompt per category) first...")
    results = run_scan(provider, limit_per_category=1)
    report_path = generate_report(results, model_name="browser-chat-target")
    print(f"Report ready: {report_path}")
finally:
    provider.close()