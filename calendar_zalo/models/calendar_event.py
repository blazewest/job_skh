from odoo import models, fields, api
from datetime import timedelta
import requests
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
_LOG_API_ZALO = {
    "0": "Gửi thành công",
    "-100": "Xảy ra lỗi không xác định, vui lòng thử lại sau",
    "-101": "Ứng dụng không hợp lệ",
    "-102": "Ứng dụng không tồn tại",
    "-103": "Ứng dụng chưa được kích hoạt",
    "-104": "Secret key của ứng dụng không hợp lệ",
    "-105": "Ứng dụng gửi ZNS chưa đươc liên kết với OA nào",
    "-106": "Phương thức không được hỗ trợ",
    "-107": "ID thông báo không hợp lệ",
    "-108": "Số điện thoại không hợp lệ",
    "-109": "ID mẫu ZNS không hợp lệ",
    "-110": "Phiên bản Zalo app không được hỗ trợ. Người dùng cần cập nhật phiên bản mới nhất",
    "-111": "Mẫu ZNS không có dữ liệu",
    "-112": "Nội dung mẫu ZNS không hợp lệ",
    "-1123": "Không thể tạo QR code, vui lòng kiểm tra lại",
    "-113": "Button không hợp lệ",
    "-114": "Người dùng không nhận được ZNS vì các lý do: Trạng thái tài khoản, Tùy chọn nhận ZNS, Sử dụng Zalo phiên bản cũ, hoặc các lỗi nội bộ khác",
    "-115": "Tài khoản ZNS không đủ số dư",
    "-116": "Nội dung không hợp lệ",
    "-117": "OA hoặc ứng dụng gửi ZNS chưa được cấp quyền sử dụng mẫu ZNS này",
    "-118": "Tài khoản Zalo không tồn tại hoặc đã bị vô hiệu hoá",
    "-119": "Tài khoản không thể nhận ZNS",
    "-120": "OA chưa được cấp quyền sử dụng tính năng này",
    "-121": "Mẫu ZNS không có nội dung",
    "-122": "Body request không đúng định dạng JSON",
    "-123": "Giải mã nội dung thông báo RSA thất bại",
    "-124": "Mã truy cập không hợp lệ",
    "-125": "ID Official Account không hợp lệ",
    "-126": "Ví (development mode) không đủ số dư",
    "-127": "Template test chỉ có thể được gửi cho quản trị viên",
    "-128": "Mã encoding key không tồn tại",
    "-129": "Không thể tạo RSA key, vui lòng thử lại sau",
    "-130": "Nội dung mẫu ZNS vượt quá giới hạn kí tự",
    "-131": "Mẫu ZNS chưa được phê duyệt",
    "-132": "Tham số không hợp lệ",
    "-133": "Mẫu ZNS này không được phép gửi vào ban đêm (từ 22h-6h)",
    "-134": "Người dùng chưa phản hồi gợi ý nhận ZNS từ OA",
    "-135": "OA chưa có quyền gửi ZNS (chưa được xác thực, đang sử dụng gói miễn phí)",
    "-136": "Cần kết nối với ZCA để sử dụng tính năng này",
    "-137": "Thanh toán ZCA thất bại (ví không đủ số dư,…)",
    "-138": "Ứng dụng gửi ZNS chưa có quyền sử dụng tính năng này",
    "-139": "Người dùng từ chối nhận loại ZNS này",
    "-140": "OA chưa được cấp quyền gửi ZNS hậu mãi cho người dùng này",
    "-141": "Người dùng từ chối nhận ZNS từ Official Account",
    "-142": "RSA key không tồn tại, vui lòng gọi API tạo RSA key",
    "-143": "RSA key đã tồn tại, vui lòng gọi API lấy RSA key",
    "-144": "OA đã vượt giới hạn gửi ZNS trong ngày",
    "-145": "OA không được phép gửi loại nội dung ZNS này",
    "-146": "Mẫu ZNS này đã bị vô hiệu hóa do chất lượng gửi thấp",
    "-147": "Mẫu ZNS đã vượt giới hạn gửi trong ngày",
    "-148": "Không tìm thấy ZNS journey token",
    "-149": "ZNS journey token không hợp lệ",
    "-150": "ZNS journey token đã hết hạn",
    "-151": "Không phải mẫu ZNS E2EE",
    "-152": "Lấy E2EE key thất bại",
}

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    zalo_file_id = fields.Many2one('zalo.file', string='Tệp Zalo')
    zalo_image_id = fields.Many2one('zalo.image', string='Ảnh Zalo')
    image_preview = fields.Binary(string='Ảnh Zalo Xem trước', compute='_compute_image_preview')

    @api.depends('zalo_image_id')
    def _compute_image_preview(self):
        for rec in self:
            rec.image_preview = rec.zalo_image_id.local_file if rec.zalo_image_id else False

    @api.model_create_multi
    def create(self, vals):
        event = super().create(vals)
        event._create_zalo_crons()
        return event

    def write(self, vals):
        res = super().write(vals)
        self._create_zalo_crons()
        return res

    def _compute_alarm_cron_time(self, event_start, duration, interval):
        """Tính toán thời điểm cần chạy cron dựa trên start - duration"""
        delta = {
            'minutes': timedelta(minutes=duration),
            'hours': timedelta(hours=duration),
            'days': timedelta(days=duration)
        }.get(interval, timedelta(minutes=0))
        return event_start - delta

    def _create_zalo_crons(self):
        """Tạo hoặc cập nhật cron job nếu alarm_type là 'zalo'"""

        cron_model = self.env['ir.cron']
        model = self.env['ir.model']._get('calendar.event')

        for event in self:
            # Xóa cron cũ (tránh trùng)
            old_crons = cron_model.search([
                ('model_id', '=', model.id),
                ('code', 'like', f"model.action_push_zalo({event.id})")
            ])
            old_crons.unlink()

            # Lọc các alarm zalo
            zalo_alarms = event.alarm_ids.filtered(lambda a: a.alarm_type == 'zalo')

            for alarm in zalo_alarms:
                # Tính thời điểm gửi = start - (duration x interval)
                alarm_time = self._compute_alarm_cron_time(
                    event.start,
                    alarm.duration,
                    alarm.interval
                )

                cron_model.create({
                    'name': f"Zalo Reminder for Event {event.id} - Alarm {alarm.id}",
                    'model_id': model.id,
                    'state': 'code',
                    'code': f"model.action_push_zalo({event.id}) or None",
                    'interval_number': 1,
                    'interval_type': 'months',
                    'nextcall': alarm_time,
                    'active': True,
                    'priority': 1,
                })

    def action_push_zalo(self, event_id):
        """Gửi thông báo Zalo từ các alarm có alarm_type='zalo'"""

        event = self.browse(event_id)
        if not event:
            raise UserError("Sự kiện không tồn tại.")

        zalo_alarms = event.alarm_ids.filtered(lambda a: a.alarm_type == 'zalo')
        if not zalo_alarms:
            _logger.info("Không có alarm Zalo cho sự kiện ID %s", event.id)
            return

        user_ids = self._get_zalo_user_ids(event)
        if not user_ids:
            _logger.warning("Không có Zalo user_id trong attendee cho sự kiện ID %s", event.id)
            return

        for alarm in zalo_alarms:
            access_token = alarm.zalo_id.access_token
            if not access_token:
                _logger.warning("Alarm ID %s không có access_token.", alarm.id)
                continue

            for user_id in user_ids:
                self._send_zalo_template_message(event, user_id, access_token)
                self._send_zalo_file_if_available(event, user_id, access_token)

    def _get_zalo_user_ids(self, event):
        """Lấy danh sách user_id Zalo từ attendee"""
        return [uid for uid in event.attendee_ids.mapped('partner_id.id_zalo') if uid]

    def _send_zalo_template_message(self, event, user_id, access_token):
        """Gửi tin nhắn template sự kiện Zalo"""

        from datetime import timedelta

        elements = []

        # Nếu có ảnh, thêm ảnh vào đầu message
        if event.zalo_image_id:
            elements.append({
                "attachment_id": event.zalo_image_id.image_url,
                "type": "banner"
            })

        # Nội dung chính
        elements += [
            {
                "type": "header",
                "content": f"Nhắc sự kiện: {event.name}",
                "align": "left"
            },
            {
                "type": "table",
                "content": [
                    {"key": "Mã Cuộc Họp", "value": str(event.id)},
                    {"key": "Chức vụ",
                     "value": event.attendee_ids and event.attendee_ids[0].partner_id.name or "Không rõ"},
                    {"key": "Thời gian bắt đầu",
                     "value": (event.start + timedelta(hours=7)).strftime('%H:%M %d-%m-%Y')},
                    {"key": "Tóm tắt nội dung", "value": event.description or ""},
                    {"key": "Địa điểm", "value": event.location or ""}
                ]
            },
            {
                "type": "text",
                "align": "center",
                "content": "📢 Vui lòng có mặt đúng giờ!"
            }
        ]

        payload = {
            "recipient": {"user_id": user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "transaction_booking",
                        "language": "VI",
                        "elements": elements,
                        "buttons": [
                            {
                                "title": "Chi tiết sự kiện",
                                "type": "oa.open.url",
                                "payload": {"url": "https://oa.zalo.me/home"}
                            }
                        ]
                    }
                }
            }
        }

        try:
            response = requests.post(
                url="https://openapi.zalo.me/v3.0/oa/message/transaction",
                headers={
                    "access_token": access_token,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            res_json = response.json()
            self._log_zalo_result(event, user_id, res_json.get("error"), zalo_type="template")
            if res_json.get("error") != 0:
                _logger.warning("Zalo API lỗi khi gửi template cho user_id %s: %s", user_id, res_json)
            else:
                _logger.info("Đã gửi template Zalo thành công cho user_id %s", user_id)
        except requests.exceptions.RequestException as e:
            _logger.error("Lỗi kết nối khi gửi template Zalo đến user_id %s: %s", user_id, str(e))

    def _send_zalo_file_if_available(self, event, user_id, access_token):
        """Gửi tệp tin nếu event có zalo_file_id"""

        if not event.zalo_file_id or not event.zalo_file_id.file_token:
            return

        payload = {
            "recipient": {
                "user_id": user_id
            },
            "message": {
                "attachment": {
                    "type": "file",
                    "payload": {
                        "token": event.zalo_file_id.file_token
                    }
                }
            }
        }

        try:
            response = requests.post(
                url="https://openapi.zalo.me/v3.0/oa/message/cs",
                headers={
                    "access_token": access_token,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            res_json = response.json()
            self._log_zalo_result(event, user_id, res_json.get("error"), zalo_type="file")

            if res_json.get("error") != 0:
                _logger.warning("Gửi file Zalo thất bại cho user_id %s: %s", user_id, res_json)
            else:
                _logger.info("Gửi file Zalo thành công cho user_id %s", user_id)
        except requests.exceptions.RequestException as e:
            _logger.error("Lỗi gửi file Zalo user_id %s: %s", user_id, str(e))

    def _log_zalo_result(self, event, user_id, error_code, zalo_type):
        """Ghi log kết quả gửi Zalo vào bảng zalo.log"""
        message = _LOG_API_ZALO.get(str(error_code), "Không rõ lỗi")

        self.env['zalo.log'].create({
            'messenger': message,
            'user_id': user_id,
            'error_code': str(error_code),
            'event_id': event.id,
            'zalo_type': zalo_type
        })





