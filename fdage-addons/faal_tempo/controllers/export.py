from odoo.addons.web.controllers.main import serialize_exception, ExcelExport, ExportXlsxWriter, GroupExportXlsxWriter  # noqa

from odoo import http
from odoo.tools import pycompat


class CustomExportXlsxWriterMixin:

    def __init__(self, field_names, row_count=0):
        super().__init__(field_names, row_count=row_count)
        self.header_style.set_bg_color('#cccccc')  # noqa
        self.date_style.set_num_format('dd/mm/yyyy')  # noqa
        self.datetime_style.set_num_format('dd/mm/yyyy')  # noqa
        self.float_style = self.workbook.add_format({'num_format': '# ##0.00'})  # noqa
        self.header_bold_float_style = self.workbook.add_format({'text_wrap': True, 'bold': True, 'bg_color': '#e9ecef', 'num_format': '# ##0.00'})  # noqa

    def write_cell(self, row, column, cell_value):
        cell_style = None

        if isinstance(cell_value, float):
            cell_style = self.float_style
        if cell_style is None:
            super().write_cell(row, column, cell_value)  # noqa
        else:
            self.write(row, column, cell_value, cell_style)  # noqa


class CustomGroupExportXlsxWriter(CustomExportXlsxWriterMixin, GroupExportXlsxWriter):

    def _write_group_header(self, row, column, label, group, group_depth=0):
        aggregates = group.aggregated_values

        label = '%s%s (%s)' % ('    ' * group_depth, label, group.count)
        self.write(row, column, label, self.header_bold_style)
        for field in self.fields[1:]:  # No aggregates allowed in the first column because of the group title
            column += 1
            aggregated_value = aggregates.get(field['name'])
            self.write_header_cell(row, column, aggregated_value)
        return row + 1, 0

    def write_header_cell(self, row, column, cell_value):
        cell_style = self.header_bold_style
        if isinstance(cell_value, float):
            cell_style = self.header_bold_float_style
        self.write(row, column, cell_value, cell_style)


class CustomExportXlsxWriter(CustomExportXlsxWriterMixin, ExportXlsxWriter):
    pass


class CustomExcelExport(ExcelExport, http.Controller):

    @http.route('/web/export/xlsx', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        return super().index(data, token)

    def from_group_data(self, fields, groups):  # noqa
        with CustomGroupExportXlsxWriter(fields, groups.count) as xlsx_writer:
            x, y = 1, 0
            for group_name, group in groups.children.items():
                x, y = xlsx_writer.write_group(x, y, group_name, group)
            xlsx_writer.worksheet.autofilter(0, 0, 0, len(fields) - 1)
            xlsx_writer.worksheet.freeze_panes(1, 0)
        return xlsx_writer.value

    def from_data(self, fields, rows):  # noqa
        with CustomExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    if isinstance(cell_value, (list, tuple)):
                        cell_value = pycompat.to_text(cell_value)
                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)
            xlsx_writer.worksheet.autofilter(0, 0, 0, len(fields) - 1)
            xlsx_writer.worksheet.freeze_panes(1, 0)
        return xlsx_writer.value
