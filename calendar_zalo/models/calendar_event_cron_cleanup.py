from odoo import models, fields

class CalendarEventCronCleanup(models.Model):
    _name = 'calendar.event.cron.cleanup'
    _description = 'Lưu thông tin các cron Zalo đã chạy và cần dọn dẹp'

    cron_name = fields.Char(required=True, index=True)
    cron_id = fields.Many2one('ir.cron', string="Cron", ondelete='set null')
    event_id = fields.Many2one('calendar.event', string="Sự kiện")
    alarm_id = fields.Many2one('calendar.alarm', string="Báo thức")
    state = fields.Selection([
        ('pending', 'Chờ xóa'),
        ('done', 'Đã xóa'),
        ('failed', 'Lỗi')
    ], default='pending', string="Trạng thái")
    error_message = fields.Text(string="Lỗi (nếu có)")
