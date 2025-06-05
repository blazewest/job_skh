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
    "-200": "Gửi tin nhắn thất bại",
    "-201": "Tham số không hợp lệ",
    "-204": "Official Account đã bị xóa",
    "-205": "Official Account không tồn tại",
    "-209": "API này không được hỗ trợ do ứng dụng chưa được kích hoạt",
    "-210": "Tham số vượt quá giới hạn cho phép",
    "-211": "Vượt quá quota sử dụng cho phép của tính năng",
    "-212": "Official Account chưa đăng ký API này",
    "-213": "Người dùng chưa quan tâm Official Account",
    "-214": "Bài viết đang được xử lý",
    "-216": "Access token không hợp lệ",
    "-217": "Người dùng đã chặn tin mời quan tâm",
    "-218": "Đã quá giới hạn gửi đến người dùng này",
    "-219": "Ứng dụng đã bị gỡ bỏ hoặc vô hiệu hóa",
    "-220": "access_token đã hết hạn hoặc không còn khả dụng",
    "-221": "Tài khoản Official Account chưa xác thực",
    "-223": "OA đã vượt hạn mức xuất bản Nội dung cho phép trong kỳ",
    "-224": "Official Account chưa mua gói dịch vụ để sử dụng tính năng này",
    "-227": "Tài khoản người dùng đã bị khóa hoặc không online hơn 45 ngày. OA hiện không thể tương tác đến người dùng này",
    "-230": "Người dùng không tương tác với OA trong 7 ngày qua",
    "-232": "Người dùng chưa phát sinh tương tác hoặc tương tác cuối đã quá hạn. OA hiện không thể tương tác đến người dùng này",
    "-233": "Loại tin nhắn không được hỗ trợ hoặc không khả dụng",
    "-234": "Loại tin nhắn này không được phép gửi vào buổi tối (từ 22 giờ - 6 giờ sáng hôm sau)",
    "-235": "API này không được hỗ trợ cho phân loại OA của bạn",
    "-237": "Nhóm chat GMF đã hết hạn",
    "-238": "asset_id đã được sử dụng hoặc không còn khả dụng",
    "-240": "API gửi tin nhắn V2 đã không còn hoạt động, vui lòng chuyển qua API gửi tin nhắn V3",
    "-241": "asset_id miễn phí (có sẵn trong Gói dịch vụ) đã được sử dụng",
    "-242": "appsecret_proof cung cấp trong tham số API không hợp lệ",
    "-244": "Người dùng đã hạn chế nhận loại tin nhắn này từ OA của bạn",
    "-248": "Vi phạm tiêu chuẩn nền tảng.",
    "-320": "Ứng dụng của bạn cần kết nối với Zalo Cloud Account để sử dụng tính năng trả phí",
    "-321": "Zalo Cloud Account liên kết với App đã hết tiền hoặc không thể thực hiện trả phí",
    "-403": "Không thể tương tác với nhóm chat vì nhóm này không được sở hữu bởi OA",
    "-1340": "Không tìm thấy Form	",
    "-1341": "OA không có quyền truy cập form này",

}

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    zalo_file_id = fields.Many2one('zalo.file', string='Tệp Zalo')
    zalo_image_id = fields.Many2one('zalo.image', string='Ảnh Zalo')
    image_preview = fields.Binary(string='Ảnh Zalo Xem trước', compute='_compute_image_preview')
    modify = fields.Boolean(string='Sửa đổi', default=False)
    sent = fields.Boolean(string='Đã gửi', default=False)

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
        # Cờ tạm để tránh đệ quy
        avoid_recursion = self.env.context.get('avoid_modify_recursion', False)

        res = super().write(vals)

        if avoid_recursion:
            return res

        for record in self:
            other_fields = set(vals.keys()) - {'sent'}

            if other_fields and record.sent is True:
                # Gọi write nhưng truyền context tránh recursion
                record.with_context(avoid_modify_recursion=True).write({'modify': True})

            if other_fields:
                record._create_zalo_crons()

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
            zalo_alarms = event.alarm_ids.filtered(lambda a: a.alarm_type == 'zalo')

            for alarm in zalo_alarms:
                alarm_time = self._compute_alarm_cron_time(
                    event.start,
                    alarm.duration,
                    alarm.interval
                )

                # Truyền alarm.id vào code gọi
                code_str = f"model.action_push_zalo({event.id}, {alarm.id}) or None"

                # Tìm cron hiện tại (nếu có) theo event và alarm id
                existing_cron = cron_model.search([
                    ('model_id', '=', model.id),
                    ('code', '=', code_str)
                ], limit=1)

                if existing_cron:
                    # Cập nhật thời gian nếu cần
                    existing_cron.write({
                        'nextcall': alarm_time,
                        'active': True,
                    })
                    _logger.info("🛠️ Cập nhật cron ID %s cho event ID %s, alarm ID %s", existing_cron.id, event.id,
                                 alarm.id)
                else:
                    # Tạo mới nếu chưa có
                    cron_model.create({
                        'name': f"Zalo Reminder for Event {event.id} - Alarm {alarm.id}",
                        'model_id': model.id,
                        'state': 'code',
                        'code': code_str,
                        'interval_number': 1,
                        'interval_type': 'months',
                        'nextcall': alarm_time,
                        'active': True,
                        'priority': 1,
                    })
                    _logger.info("✅ Tạo mới cron cho event ID %s, alarm ID %s", event.id, alarm.id)

    def action_push_zalo(self, event_id, alarm_id=None):
        """Gửi thông báo Zalo từ các alarm có alarm_type='zalo' và đánh dấu cron cần xóa"""

        event = self.sudo().browse(event_id)
        if not event.exists():
            raise UserError("Sự kiện không tồn tại.")

        if alarm_id:
            zalo_alarms = event.alarm_ids.filtered(lambda a: a.alarm_type == 'zalo' and a.id == alarm_id)
        else:
            zalo_alarms = event.alarm_ids.filtered(lambda a: a.alarm_type == 'zalo')

        if not zalo_alarms:
            _logger.info("Không có alarm Zalo cho sự kiện ID %s", event.id)
            return

        zalo_users = self._get_zalo_user_ids(event)
        user_ids = [u['id_zalo'] for u in zalo_users]
        name_users = [u['name'] for u in zalo_users]

        if not user_ids:
            _logger.warning("Không có Zalo user_id trong attendee cho sự kiện ID %s", event.id)
            return

        success = True

        for alarm in zalo_alarms:
            access_token = alarm.zalo_id.access_token
            if not access_token:
                _logger.warning("Alarm ID %s không có access_token.", alarm.id)
                success = False
                continue

            for user_id, name_user in zip(user_ids, name_users):
                result = self._send_zalo_template_message(event, user_id, access_token, alarm.id, name_user)
                if not result:
                    success = False

            # ✅ Đánh dấu cần xóa cron, KHÔNG xóa hoặc tắt cron tại đây
            model = self.env['ir.model']._get('calendar.event')
            code_str = f"model.action_push_zalo({event.id}, {alarm.id}) or None"
            name_str = f"Zalo Reminder for Event {event.id} - Alarm {alarm.id}"

            cron = self.env['ir.cron'].search([
                ('model_id', '=', model.id),
                ('code', '=', code_str),
                ('name', '=', name_str),
            ], limit=1)

            if cron:
                self.env['calendar.event.cron.cleanup'].sudo().create({
                    'cron_name': name_str,
                    'cron_id': cron.id,
                    'event_id': event.id,
                    'alarm_id': alarm.id,
                    'state': 'pending'
                })

        if success:
            _logger.info("✅ Gửi thành công cho tất cả user, cập nhật sent=True")
            fresh_event = self.env['calendar.event'].sudo().browse(event.id)
            if fresh_event.exists():
                fresh_event.write({'sent': True})
            else:
                _logger.warning("❌ Không thể cập nhật sent=True vì event không còn tồn tại")

    def cleanup_zalo_crons(self):
        """Xóa các cron Zalo đã đánh dấu là pending"""
        cleanup_model = self.env['calendar.event.cron.cleanup']
        pending = cleanup_model.search([('state', '=', 'pending')])
        for rec in pending:
            try:
                if rec.cron_id and rec.cron_id.exists():
                    rec.cron_id.unlink()
                    rec.write({'state': 'done'})
                    _logger.info("🧹 Đã xóa cron: %s", rec.cron_name)
                else:
                    rec.write({'state': 'done'})
            except Exception as e:
                rec.write({'state': 'failed', 'error_message': str(e)})
                _logger.error("❌ Lỗi khi xóa cron: %s - %s", rec.cron_name, e)

    def _get_zalo_user_ids(self, event):
        """Lấy danh sách user Zalo từ attendee, gồm cả id_zalo và tên"""
        return [
            {'id_zalo': partner.id_zalo, 'name': partner.name}
            for partner in event.attendee_ids.mapped('partner_id')
            if partner.id_zalo
        ]

    def _send_zalo_template_message(self, event, user_id, access_token, alarm_id, name_user):
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
                "content": f"Nhắc sự kiện: {event.name}" + (" (sửa đổi)" if event.modify else ""),
                "align": "left"
            },
            {
                "type": "table",
                "content": [
                    {"key": "Mã Cuộc Họp", "value": str(event.id)},
                    {"key": "Đồng chí", "value": name_user or "Không rõ"},
                    {"key": "Thời gian bắt đầu",
                     "value": (event.start + timedelta(hours=7)).strftime('%H:%M %d-%m-%Y')},
                    {"key": "Địa điểm", "value": event.location or ""},
                    {"key": "Tóm tắt nội dung", "value": event.description or ""},
                ]
            },
            {
                "type": "text",
                "align": "center",
                "content": "📢 Vui lòng có mặt đúng giờ!"
            }
        ]

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        event_url = f"{base_url}/web#id={event.id}&model=calendar.event&view_type=form"
        url_controller = f"{base_url}/zalo/send_file?event_id={event.id}&user_id={user_id}&alarm_id={alarm_id}"

        payload = {
            "recipient": {"user_id": user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "transaction_booking",
                        "language": "VI",
                        "elements": elements,
                        # "buttons": [
                        #     {
                        #         "title": "Chi tiết sự kiện",
                        #         "type": "oa.open.url",
                        #         "payload": {"url": event_url}
                        #     }
                        # ]
                    }
                }
            }
        }

        if event.zalo_file_id:
            payload["message"]["attachment"]["payload"]["buttons"].append({
                "title": "Lấy tệp đính kèm",
                "type": "oa.open.url",
                "payload": {"url": url_controller}
            })

        try:
            import requests
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
                return False
            else:
                _logger.info("Đã gửi template Zalo thành công cho user_id %s", user_id)
                return True
        except requests.exceptions.RequestException as e:
            _logger.error("Lỗi kết nối khi gửi template Zalo đến user_id %s: %s", user_id, str(e))
            return False

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

    def unlink(self):
        cron_model = self.env['ir.cron']
        model = self.env['ir.model']._get('calendar.event')

        for event in self:
            if event.sent:
                zalo_alarms = event.alarm_ids.filtered(lambda a: a.alarm_type == 'zalo')
                if not zalo_alarms:
                    _logger.info(f"Sự kiện ID {event.id} không có alarm zalo, bỏ qua gửi thông báo hủy.")
                else:
                    zalo_users = self._get_zalo_user_ids(event)
                    user_ids = [u['id_zalo'] for u in zalo_users]
                    name_users = [u['name'] for u in zalo_users]

                    if not user_ids:
                        _logger.warning(f"Không có Zalo user_id trong attendee cho sự kiện ID {event.id}")
                    else:
                        for alarm in zalo_alarms:
                            access_token = alarm.zalo_id.access_token
                            if not access_token:
                                _logger.warning(f"Alarm ID {alarm.id} không có access_token.")
                                continue

                            for user_id, name_user in zip(user_ids, name_users):
                                success = self._send_zalo_template_message_cancel(event, user_id, access_token,
                                                                                  name_user)
                                if success:
                                    _logger.info(f"Đã gửi thông báo hủy sự kiện ID {event.id} đến user_id {user_id}")
                                else:
                                    _logger.warning(
                                        f"Lỗi khi gửi thông báo hủy sự kiện ID {event.id} đến user_id {user_id}")
            else:
                # Xoá cron nếu chưa gửi
                zalo_alarms = event.alarm_ids.filtered(lambda a: a.alarm_type == 'zalo')
                for alarm in zalo_alarms:
                    code_str = f"model.action_push_zalo({event.id}, {alarm.id}) or None"
                    existing_cron = cron_model.search([
                        ('model_id', '=', model.id),
                        ('code', '=', code_str)
                    ])
                    if existing_cron:
                        _logger.info(f"🗑️ Xoá {len(existing_cron)} cron của sự kiện ID {event.id}, alarm ID {alarm.id}")
                        existing_cron.unlink()

        return super().unlink()

    def _send_zalo_template_message_cancel(self, event, user_id, access_token, name_user):
        """Gửi tin nhắn template thông báo hủy sự kiện khi event sắp bị xóa"""
        elements = [
            {
                "type": "header",
                "content": f"Hủy sự kiện: {event.name}",
                "align": "left"
            },
            {
                "type": "table",
                "content": [
                    {"key": "Mã Cuộc Họp", "value": str(event.id)},
                    {"key": "Người nhận", "value": name_user or "Không rõ"},
                    {"key": "Thông báo", "value": "Sự kiện đã bị hủy"},
                ]
            }
        ]

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        payload = {
            "recipient": {"user_id": user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "transaction_booking",
                        "language": "VI",
                        "elements": elements,
                    }
                }
            }
        }

        import requests
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
            if res_json.get("error") != 0:
                _logger.warning("Zalo API lỗi khi gửi template hủy cho user_id %s: %s", user_id, res_json)
                return False
            else:
                return True
        except requests.exceptions.RequestException as e:
            _logger.error("Lỗi kết nối khi gửi template hủy Zalo đến user_id %s: %s", user_id, str(e))
            return False





