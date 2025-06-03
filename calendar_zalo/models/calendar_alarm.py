# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class CalendarAlarm(models.Model):
    _inherit = 'calendar.alarm'

    alarm_type = fields.Selection(selection_add=[
        ('zalo', 'Gửi tin nhắn Zalo ')
        ], ondelete={'zalo': 'set default'})
    zalo_id = fields.Many2one(comodel_name='zalo.application',string='Kênh Zalo OA')

    @api.onchange('duration', 'interval', 'alarm_type', 'zalo_id')
    def _onchange_duration_interval(self):
        display_interval = self._interval_selection.get(self.interval, '')
        display_alarm_type = dict(self._fields['alarm_type']._description_selection(self.env)).get(self.alarm_type, '')
        name = f"{display_alarm_type} - {self.duration} {display_interval}"
        if self.zalo_id:
            name += f" - {self.zalo_id.name}"
        self.name = name


