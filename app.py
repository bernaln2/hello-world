import http.server
import json
import urllib.parse
from blockchain import VotingBlockchain

CANDIDATES = ["Alice Johnson", "Bob Smith"]
blockchain = VotingBlockchain()


def render_base(title, content, flash_msg=None):
    flash_html = ""
    if flash_msg:
        category, message = flash_msg
        flash_html = f'<div class="flash {category}">{message}</div>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Class Election 2026</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: #f0f2f5;
            color: #333;
            min-height: 100vh;
        }}
        header {{
            background: #1a73e8;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        header h1 {{ font-size: 1.8rem; }}
        header p {{ margin-top: 5px; opacity: 0.9; }}
        nav {{
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 15px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        nav a {{
            text-decoration: none;
            color: #1a73e8;
            font-weight: bold;
            padding: 8px 20px;
            border-radius: 5px;
            transition: background 0.2s;
        }}
        nav a:hover {{ background: #e8f0fe; }}
        .container {{
            max-width: 700px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        .flash {{
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .flash.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .flash.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
    </style>
</head>
<body>
    <header>
        <h1>Class President Election 2026</h1>
        <p>Secured by Blockchain</p>
    </header>
    <nav>
        <a href="/">Vote</a>
        <a href="/results">Results</a>
    </nav>
    <div class="container">
        {flash_html}
        {content}
    </div>
</body>
</html>"""


def render_vote_page(flash_msg=None):
    candidate_options = ""
    for i, candidate in enumerate(CANDIDATES):
        candidate_options += f"""
        <div class="candidate-option">
            <input type="radio" id="candidate_{i}" name="candidate" value="{candidate}" required>
            <label for="candidate_{i}">{candidate}</label>
        </div>"""

    content = f"""
    <style>
        .vote-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .vote-card h2 {{
            margin-bottom: 20px;
            text-align: center;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }}
        .form-group input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }}
        .form-group input[type="text"]:focus {{
            outline: none;
            border-color: #1a73e8;
        }}
        .candidates {{
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
        }}
        .candidate-option {{
            flex: 1;
            text-align: center;
        }}
        .candidate-option input[type="radio"] {{ display: none; }}
        .candidate-option label {{
            display: block;
            padding: 20px;
            border: 3px solid #ddd;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        .candidate-option input[type="radio"]:checked + label {{
            border-color: #1a73e8;
            background: #e8f0fe;
            color: #1a73e8;
        }}
        .candidate-option label:hover {{
            border-color: #aaa;
        }}
        .submit-btn {{
            width: 100%;
            padding: 14px;
            background: #1a73e8;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .submit-btn:hover {{ background: #1557b0; }}
    </style>
    <div class="vote-card">
        <h2>Cast Your Vote</h2>
        <form method="POST" action="/vote">
            <div class="form-group">
                <label for="student_id">Student ID Number</label>
                <input type="text" id="student_id" name="student_id"
                       placeholder="Enter your student ID" required>
            </div>
            <div class="form-group">
                <label>Select Your Candidate</label>
                <div class="candidates">
                    {candidate_options}
                </div>
            </div>
            <button type="submit" class="submit-btn">Submit Vote</button>
        </form>
    </div>"""
    return render_base("Vote", content, flash_msg)


def render_results_page(flash_msg=None):
    vote_counts = blockchain.get_results()
    total_votes = sum(vote_counts.values())
    chain_valid = blockchain.is_chain_valid()
    chain_data = blockchain.get_chain()

    status_class = "chain-valid" if chain_valid else "chain-invalid"
    status_text = "Valid - No tampering detected" if chain_valid else "INVALID - Chain has been tampered with!"

    bars_html = ""
    colors = ["#1a73e8", "#ea4335"]
    for i, candidate in enumerate(CANDIDATES):
        count = vote_counts.get(candidate, 0)
        pct = round(count / total_votes * 100, 1) if total_votes > 0 else 0
        color = colors[i % len(colors)]
        bars_html += f"""
        <div class="candidate-result">
            <div class="candidate-name">{candidate}</div>
            <div class="bar-container">
                <div class="bar" style="width: {pct}%; background: {color};">{pct}%</div>
            </div>
            <div class="vote-count">{count} votes</div>
        </div>"""

    blocks_html = ""
    for j, block in enumerate(chain_data):
        is_genesis = j == 0
        block_class = "block genesis" if is_genesis else "block"
        header_text = f"Block #{block['index']}" + (" (Genesis)" if is_genesis else "")
        if is_genesis:
            data_text = "Election Start"
        else:
            data_text = f"Student {block['data']['student_id']} voted for {block['data']['candidate']}"

        arrow = '<div class="chain-arrow">&#8595;</div>' if j > 0 else ""
        blocks_html += f"""
        {arrow}
        <div class="{block_class}">
            <div class="block-header">{header_text}</div>
            <div class="block-field"><span>Data:</span> {data_text}</div>
            <div class="block-field"><span>Hash:</span><div class="hash">{block['hash']}</div></div>
            <div class="block-field"><span>Previous Hash:</span><div class="hash">{block['previous_hash']}</div></div>
        </div>"""

    content = f"""
    <style>
        .results-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .results-card h2 {{ margin-bottom: 20px; text-align: center; }}
        .candidate-result {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            gap: 15px;
        }}
        .candidate-name {{ width: 140px; font-weight: bold; }}
        .bar-container {{
            flex: 1;
            background: #e9ecef;
            border-radius: 10px;
            height: 35px;
            overflow: hidden;
        }}
        .bar {{
            height: 100%;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9rem;
            min-width: 40px;
            transition: width 0.5s;
        }}
        .vote-count {{ width: 80px; text-align: right; font-weight: bold; }}
        .total {{ text-align: center; margin-top: 20px; color: #666; }}
        .chain-status {{
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        .chain-valid {{ background: #d4edda; color: #155724; }}
        .chain-invalid {{ background: #f8d7da; color: #721c24; }}
        .blockchain-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .blockchain-card h2 {{ margin-bottom: 20px; text-align: center; }}
        .block {{
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            font-size: 0.85rem;
        }}
        .block.genesis {{ border-color: #1a73e8; background: #f8f9ff; }}
        .block-header {{ font-weight: bold; margin-bottom: 8px; color: #1a73e8; }}
        .block-field {{ margin-bottom: 4px; }}
        .block-field span {{ color: #666; }}
        .hash {{
            font-family: monospace;
            font-size: 0.75rem;
            word-break: break-all;
            color: #555;
        }}
        .chain-arrow {{ text-align: center; font-size: 1.5rem; color: #aaa; margin: 5px 0; }}
    </style>
    <div class="results-card">
        <h2>Election Results</h2>
        <div class="chain-status {status_class}">
            Blockchain Status: {status_text}
        </div>
        {bars_html}
        <div class="total">Total votes cast: {total_votes}</div>
    </div>
    <div class="blockchain-card">
        <h2>Blockchain Ledger</h2>
        {blocks_html}
    </div>"""
    return render_base("Results", content, flash_msg)


class ElectionHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_html(render_vote_page())
        elif self.path == "/results":
            self.send_html(render_results_page())
        elif self.path.startswith("/vote-success"):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            msg = params.get("msg", ["Vote recorded!"])[0]
            self.send_html(render_results_page(flash_msg=("success", msg)))
        elif self.path.startswith("/vote-error"):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            msg = params.get("msg", ["An error occurred."])[0]
            self.send_html(render_vote_page(flash_msg=("error", msg)))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/vote":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            params = urllib.parse.parse_qs(body)

            student_id = params.get("student_id", [""])[0].strip()
            candidate = params.get("candidate", [""])[0].strip()

            if not student_id:
                self.redirect("/vote-error?msg=" + urllib.parse.quote("Please enter your Student ID."))
                return
            if not student_id.isdigit():
                self.redirect("/vote-error?msg=" + urllib.parse.quote("Student ID must be a number."))
                return
            if candidate not in CANDIDATES:
                self.redirect("/vote-error?msg=" + urllib.parse.quote("Invalid candidate selected."))
                return

            success, message = blockchain.cast_vote(student_id, candidate)
            if success:
                self.redirect("/vote-success?msg=" + urllib.parse.quote(message))
            else:
                self.redirect("/vote-error?msg=" + urllib.parse.quote(message))
        else:
            self.send_response(404)
            self.end_headers()

    def send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    server = http.server.HTTPServer(("0.0.0.0", port), ElectionHandler)
    print(f"Election server running at http://localhost:{port}")
    print("Press Ctrl+C to stop")
    server.serve_forever()
