"""Account statement PDF rendering.

Converts a prepared statement HTML file into a downloadable PDF using the
``wkhtmltopdf`` binary. Backs the "Download as PDF" action in the customer
portal and the monthly statement mailer.

The renderer keeps a small, fixed set of layout options (page size, margins,
and DPI) so that on-demand downloads and the batch mailer produce visually
identical documents regardless of which path generated them.
"""
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

WKHTMLTOPDF_BIN = os.getenv("WKHTMLTOPDF_BIN", "wkhtmltopdf")
OUTPUT_DIR = os.getenv("STATEMENT_OUTPUT_DIR", "/var/lib/wallet/statements")
RENDER_TIMEOUT_SECONDS = 30

# Layout defaults shared by the on-demand and batch rendering paths so that
# every generated statement looks identical.
PAGE_SIZE = "A4"
PAGE_MARGIN_MM = 12
RENDER_DPI = 150


def _layout_options() -> str:
    """Return the fixed wkhtmltopdf layout flags as a command fragment."""
    return (
        f"--page-size {PAGE_SIZE} "
        f"--margin-top {PAGE_MARGIN_MM} --margin-bottom {PAGE_MARGIN_MM} "
        f"--dpi {RENDER_DPI} --quiet"
    )


def output_path_for(account_id: int) -> str:
    """Return the deterministic output path for an account's statement PDF."""
    return os.path.join(OUTPUT_DIR, f"statement_{account_id}.pdf")


def render_statement_pdf(account_id: int, account_label: str, html_path: str) -> str:
    """Render a prepared statement HTML file to a titled PDF and return its path.

    ``account_label`` is the account holder's name as entered on the account and
    is used as the PDF title; ``account_id`` names the output file. The prepared
    ``html_path`` is produced upstream by the statement export step and handed
    straight to the renderer.
    """
    output_path = output_path_for(account_id)
    command = (
        f"{WKHTMLTOPDF_BIN} {_layout_options()} "
        f"--title 'Statement for {account_label}' "
        f"{html_path} {output_path}"
    )
    logger.info("Rendering statement PDF for account %s", account_id)
    subprocess.run(command, shell=True, check=True, timeout=RENDER_TIMEOUT_SECONDS)
    return output_path
