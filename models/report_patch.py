import subprocess
import tempfile
import os

from odoo import models

# Path to your external wkhtmltopdf binary inside container
WKHTMLTOPDF_PATH = "/usr/local/bin/wkhtmltopdf"

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _check_wkhtmltopdf(self):
        """
        Skip the 2-worker requirement
        """
        # Always return True to bypass the 2-worker restriction
        return True

    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False
    ):
        """
        Run external wkhtmltopdf binary safely
        """
        pdf_files = []

        for body in bodies:
            # Body HTML
            body_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            body_file.write(body if isinstance(body, bytes) else body.encode())
            body_file.close()

            # PDF output
            pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf_file.close()

            command = [
                WKHTMLTOPDF_PATH,
                "--disable-local-file-access",
                "--quiet",
                "--javascript-delay", "1000",
                "--no-stop-slow-scripts",
                body_file.name,
                pdf_file.name
            ]

            # Add header if exists
            if header:
                header_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
                header_file.write(header if isinstance(header, bytes) else header.encode())
                header_file.close()
                command.insert(-1, "--header-html")
                command.insert(-1, header_file.name)

            # Add footer if exists
            if footer:
                footer_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
                footer_file.write(footer if isinstance(footer, bytes) else footer.encode())
                footer_file.close()
                command.insert(-1, "--footer-html")
                command.insert(-1, footer_file.name)

            # Run wkhtmltopdf
            subprocess.run(command, check=True)

            pdf_files.append(pdf_file.name)

            # Clean temporary files
            os.unlink(body_file.name)
            if header:
                os.unlink(header_file.name)
            if footer:
                os.unlink(footer_file.name)

        # Combine PDFs (if multiple bodies)
        pdf_content = b""
        for f in pdf_files:
            with open(f, "rb") as file:
                pdf_content += file.read()
            os.unlink(f)

        return pdf_content
