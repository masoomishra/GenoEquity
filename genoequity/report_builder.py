from datetime import datetime


def build_html_report(gwas_id, variants_count, resolved_count, flagged, coverage, reliability, gap_index):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def dict_to_html(d):
        return "<br>".join([f"<b>{k}</b>: {v:.4f}" for k, v in d.items()])

    html = f"""
    <html>
    <head>
        <title>GenoEquity Report</title>
        <style>
            body {{
                font-family: Arial;
                margin: 40px;
                background-color: #f7f7f7;
            }}
            .card {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
            }}
            h2 {{
                color: #444;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }}
        </style>
    </head>

    <body>

    <div class="card">
        <h1>GenoEquity PRS Bias Report</h1>
        <p><b>GWAS ID:</b> {gwas_id}</p>
        <p><b>Generated:</b> {now}</p>
    </div>

    <div class="card">
        <h2>Summary</h2>
        <p>Total variants: {variants_count}</p>
        <p>Resolved rsIDs: {resolved_count}</p>
        <p>Flagged variants: {len(flagged)}</p>
    </div>

    <div class="card">
        <h2>Top Flagged Variants</h2>
        <p>{", ".join(flagged[:10]) if flagged else "None"}</p>
    </div>

    <div class="card">
        <h2>Coverage (by ancestry)</h2>
        <p>{dict_to_html(coverage)}</p>
    </div>

    <div class="card">
        <h2>Reliability (by ancestry)</h2>
        <p>{dict_to_html(reliability)}</p>
    </div>

    <div class="card">
        <h2>Gap Index (bias vs NFE)</h2>
        <p>{dict_to_html(gap_index)}</p>
    </div>

    </body>
    </html>
    """

    return html