
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    id_zalo = fields.Char(string='Mã ZALO cá nhân')

