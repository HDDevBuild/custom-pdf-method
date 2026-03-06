import subprocess
import tempfile
import os

from odoo import models


WKHTMLTOPDF_PATH = "/usr/local/bin/wkhtmltopdf"


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

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
        Override wkhtmltopdf execution to work without multiple workers
        """

        pdf_files = []

        for body in bodies:

            body_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            body_file.write(body)
            body_file.close()

            pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf_file.close()

            command = [
                WKHTMLTOPDF_PATH,
                "--disable-local-file-access",
                "--quiet",
                body_file.name,
                pdf_file.name
            ]

            subprocess.run(command, check=True)

            pdf_files.append(pdf_file.name)

        pdf_content = b''

        for f in pdf_files:
            with open(f, "rb") as file:
                pdf_content += file.read()

            os.unlink(f)

        return pdf_content
