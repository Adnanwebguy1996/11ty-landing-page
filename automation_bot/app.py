from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from bot import find_leads, send_campaign

HOST = "0.0.0.0"
PORT = 5050
STATIC_DIR = Path(__file__).parent / "static"

DEFAULT_SUBJECT = "Quick idea for {name} in {city}"
DEFAULT_BODY = (
    "Hi {name},\n\n"
    "I work with {trade} businesses in {city} to help them book more jobs with less back-and-forth. "
    "If helpful, I can share a short plan tailored to your business."
)


def render_page(
    leads=None,
    logs=None,
    trade: str = "",
    city: str = "",
    max_results: int = 10,
    subject: str = DEFAULT_SUBJECT,
    body: str = DEFAULT_BODY,
    dry_run: bool = True,
) -> str:
    leads = leads or []
    logs = logs or []
    checked = "checked" if dry_run else ""

    leads_rows = "".join(
        f"<tr><td>{l.name}</td><td>{l.trade}</td><td>{l.city}</td><td>{l.email}</td><td><a href='{l.website}' target='_blank'>{l.website}</a></td></tr>"
        for l in leads
    )
    logs_rows = "".join(
        f"<tr><td>{entry['lead'].name}</td><td>{entry['subject']}</td><td>{entry['status']}</td><td>{entry['error']}</td></tr>"
        for entry in logs
    )

    results_html = ""
    if leads:
        results_html = f"""
        <section class='panel'>
          <h2>Leads Found ({len(leads)})</h2>
          <table><thead><tr><th>Name</th><th>Trade</th><th>City</th><th>Email</th><th>Website</th></tr></thead><tbody>{leads_rows}</tbody></table>
        </section>
        <section class='panel'>
          <h2>Campaign Log</h2>
          <table><thead><tr><th>Lead</th><th>Subject</th><th>Status</th><th>Error</th></tr></thead><tbody>{logs_rows}</tbody></table>
        </section>
        """

    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <title>Blue-Collar Outreach Bot</title>
  <link rel='stylesheet' href='/static/style.css' />
</head>
<body>
  <main class='container'>
    <h1>Blue-Collar Outreach Bot (Python)</h1>
    <p class='muted'>Finds businesses from a dataset, personalizes outreach, and runs dry-run or real SMTP campaigns.</p>
    <form method='post' action='/run' class='panel'>
      <div class='grid'>
        <label>Trade<input name='trade' value='{trade}' placeholder='e.g. plumber'></label>
        <label>City<input name='city' value='{city}' placeholder='e.g. Dallas'></label>
        <label>Max results<input type='number' name='max_results' min='1' max='100' value='{max_results}'></label>
      </div>
      <label>Email subject template<input name='subject' value='{subject}'></label>
      <label>Email body template<textarea name='body' rows='6'>{body}</textarea></label>
      <label class='checkbox'><input type='checkbox' name='dry_run' {checked}> Dry run (no emails sent)</label>
      <button type='submit'>Run Automation</button>
    </form>
    {results_html}
  </main>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/":
            html = render_page()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if self.path == "/static/style.css":
            css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.end_headers()
            self.wfile.write(css.encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):  # noqa: N802
        if self.path != "/run":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(data)

        trade = form.get("trade", [""])[0]
        city = form.get("city", [""])[0]
        max_results = int(form.get("max_results", ["10"])[0])
        subject = form.get("subject", [DEFAULT_SUBJECT])[0]
        body = form.get("body", [DEFAULT_BODY])[0]
        dry_run = "dry_run" in form

        leads = find_leads(trade=trade, city=city, max_results=max_results)
        logs = send_campaign(
            leads=leads,
            subject_template=subject,
            body_template=body,
            dry_run=dry_run,
        )
        html = render_page(leads, logs, trade, city, max_results, subject, body, dry_run)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()
