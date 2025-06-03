# models/zalo_file.py
import base64
import requests
from odoo import models, fields, api
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class ZaloFile(models.Model):
    _name = 'zalo.file'
    _description = 'Tệp từ Zalo OA'

    name = fields.Char(string='Tên file')
    file_token = fields.Char(string='Token từ Zalo')
    response_data = fields.Text(string='Phản hồi từ Zalo')
    local_file = fields.Binary(string='File nội bộ')
    zalo_id = fields.Many2one(comodel_name='zalo.application', string='Kênh Zalo OA')
    uploaded = fields.Boolean(string='Đã upload?', compute='_compute_uploaded', store=True)

    @api.depends('file_token')
    def _compute_uploaded(self):
        for rec in self:
            rec.uploaded = bool(rec.file_token)

    def _upload_file_to_zalo(self):
        for rec in self:
            if not rec.zalo_id or not rec.zalo_id.access_token or not rec.local_file:
                continue
            try:
                file_name = rec.name or 'zalo_file.docx'
                file_data = base64.b64decode(rec.local_file)
                files = {'file': (file_name, file_data, 'application/octet-stream')}
                headers = {'access_token': rec.zalo_id.access_token}

                response = requests.post(
                    url='https://openapi.zalo.me/v2.0/oa/upload/file',
                    headers=headers,
                    files=files
                )
                response.raise_for_status()
                result = response.json()

                rec.response_data = str(result)
                rec.file_token = result.get('data', {}).get('token', '')
                _logger.info(f"Upload file thành công: {rec.file_token}")

            except Exception as e:
                rec.response_data = f"Lỗi khi upload: {str(e)}"
                _logger.error(f"Lỗi upload file Zalo: {str(e)}")

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ZaloFile, self).create(vals_list)
        for rec in records:
            rec._upload_file_to_zalo()
        return records

    def write(self, vals):
        res = super(ZaloFile, self).write(vals)
        if 'local_file' in vals or 'zalo_id' in vals:
            for rec in self:
                rec._upload_file_to_zalo()
        return res

    @api.model
    def cron_reupload_zalo_file(self):
        """
        Cron tự động gửi lại ảnh mỗi 5 ngày.
        Chỉ gửi những bản ghi có zalo_id và local_file,
        và không quá 15 ngày kể từ ngày tạo.
        """
        fifteen_days_ago = fields.Datetime.now() - timedelta(days=15)
        images = self.search([
            ('zalo_id', '!=', False),
            ('local_file', '!=', False),
            ('create_date', '>=', fifteen_days_ago)
        ])
        for image in images:
            try:
                image.upload_to_zalo()
            except Exception as e:
                _logger.warning(f"Không thể gửi lại file ID {image.id}: {e}")

