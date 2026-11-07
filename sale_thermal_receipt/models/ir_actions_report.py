from odoo import api, models

THERMAL_REPORT = 'sale_thermal_receipt.report_sale_thermal'

# Height estimate in mm (tune to your printer / font size)
BASE_HEIGHT_MM = 110     # header + totals + footer
LINE_HEIGHT_MM = 9       # per order line
MIN_HEIGHT_MM = 120


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        report = self._get_report(report_ref)
        if report.report_name == THERMAL_REPORT and res_ids:
            orders = self.env[report.model].browse(res_ids)
            max_lines = max((len(o.order_line) for o in orders), default=0)
            height = max(MIN_HEIGHT_MM, BASE_HEIGHT_MM + max_lines * LINE_HEIGHT_MM)
            self = self.with_context(thermal_page_height=height)
        return super(IrActionsReport, self)._render_qweb_pdf_prepare_streams(
            report_ref, data, res_ids=res_ids)

    @api.model
    def _build_wkhtmltopdf_args(self, paperformat_id, landscape,
                                specific_paperformat_args=None, set_viewport_size=False):
        args = super()._build_wkhtmltopdf_args(
            paperformat_id, landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)
        height = self.env.context.get('thermal_page_height')
        if height and '--page-height' in args:
            args[args.index('--page-height') + 1] = '%smm' % height
        return args
