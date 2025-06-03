import base64
import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ZaloImage(models.Model):
    _name = 'zalo.image'
    _description = 'Ảnh từ Zalo OA'

    name = fields.Char(string='Tên ảnh')
    image_url = fields.Char(string='Mã đường dẫn')
    response_data = fields.Text(string='Phản hồi từ Zalo')
    local_file = fields.Binary(string='Ảnh nội bộ')
    zalo_id = fields.Many2one(comodel_name='zalo.application', string='Kênh Zalo OA')
    uploaded = fields.Boolean(string='Đã upload?', compute='_compute_uploaded', store=True)

    @api.depends('image_url')
    def _compute_uploaded(self):
        for rec in self:
            rec.uploaded = bool(rec.image_url)

    def upload_to_zalo(self):
        """
        Gửi ảnh đến Zalo nếu có đủ access_token và file
        """
        for record in self:
            if not record.local_file or not record.zalo_id or not record.zalo_id.access_token:
                _logger.warning("Thiếu file hoặc access_token khi gửi ảnh lên Zalo.")
                continue

            try:
                file_name = record.name or 'zalo_image.jpg'
                image_data = record.local_file.decode('utf-8')
                file_content = base64.b64decode(image_data)

                files = {'file': (file_name, file_content, 'image/jpeg')}
                headers = {'access_token': record.zalo_id.access_token}
                response = requests.post(
                    url='https://openapi.zalo.me/v2.0/oa/upload/image',
                    headers=headers,
                    files=files)
                response.raise_for_status()
                result = response.json()

                record.response_data = str(result)
                record.image_url = result.get('data', {}).get('attachment_id', '')
                _logger.info(f"Upload thành công: {record.image_url}")

            except Exception as e:
                record.response_data = f"Lỗi khi upload: {str(e)}"
                _logger.error(f"Lỗi upload ảnh Zalo: {str(e)}")

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ZaloImage, self).create(vals_list)
        for rec in records:
            rec.upload_to_zalo()
        return records

    def write(self, vals):
        res = super(ZaloImage, self).write(vals)
        if 'local_file' in vals or 'zalo_id' in vals:
            for rec in self:
                rec.upload_to_zalo()
        return res



    @api.model
    def cron_reupload_zalo_images(self):
        """
        Cron tự động gửi lại ảnh mỗi 3 ngày.
        Chỉ gửi những bản ghi có zalo_id và local_file.
        """
        images = self.search([('zalo_id', '!=', False), ('local_file', '!=', False)])
        for image in images:
            try:
                image.upload_to_zalo()
            except Exception as e:
                _logger.warning(f"Không thể gửi lại ảnh ID {image.id}: {e}")
