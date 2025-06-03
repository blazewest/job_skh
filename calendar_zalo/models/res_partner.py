# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    id_zalo = fields.Char(string='Mã ZALO cá nhân')
