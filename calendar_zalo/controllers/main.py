from odoo import http
import logging
from odoo.http import request
import requests
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
class ZaloController(http.Controller):

    @http.route('/zalo/send_file', type='http', auth='public', methods=['GET'])
    def send_file(self, event_id=None, user_id=None, alarm_id=None):
        _logger.info(f"Received request with params: event_id={event_id}, user_id={user_id}, alarm_id={alarm_id}")

        if not event_id or not user_id or not alarm_id:
            _logger.warning("Missing required parameters")
            return request.make_response("Thiếu thông tin event_id, user_id hoặc alarm_id",
                                         headers=[('Content-Type', 'text/plain; charset=utf-8')], status=400)

        event_id = int(event_id)
        user_id = str(user_id)
        alarm_id = int(alarm_id)

        alarm = request.env['calendar.alarm'].sudo().browse(alarm_id)
        if not alarm or not alarm.zalo_id or not alarm.zalo_id.access_token:
            _logger.warning("Invalid alarm or missing access_token")
            return request.make_response("Alarm không tồn tại hoặc thiếu access_token",
                                         headers=[('Content-Type', 'text/plain; charset=utf-8')], status=400)

        access_token = alarm.zalo_id.access_token
        event = request.env['calendar.event'].sudo().browse(event_id)
        if event:
            self._send_zalo_file_if_available(event, user_id, access_token)
            _logger.info("File sent successfully")
            return request.make_response("Đã gửi tệp đính kèm thành công",
                                         headers=[('Content-Type', 'text/html; charset=utf-8')], status=200)
        else:
            _logger.warning("Event not found")
            return request.make_response("Sự kiện không tồn tại",
                                         headers=[('Content-Type', 'text/html; charset=utf-8')], status=404)

    def _send_zalo_file_if_available(self, event, user_id, access_token):
        """Gửi tệp tin nếu event có zalo_file_id"""
        if not event.zalo_file_id or not event.zalo_file_id.file_token:
            _logger.warning("Không có tệp đính kèm cho sự kiện ID %s", event.id)
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
            self._log_zalo_result(event, user_id, "-1", zalo_type="file")  # Mã lỗi tùy chỉnh cho ngoại lệ

    def _log_zalo_result(self, event, user_id, error_code, zalo_type):
        """Ghi log kết quả gửi Zalo vào bảng zalo.log"""
        message = _LOG_API_ZALO.get(str(error_code), "Không rõ lỗi")

        request.env['zalo.log'].create({
            'messenger': message,
            'user_id': user_id,
            'error_code': str(error_code),
            'event_id': event.id,
            'zalo_type': zalo_type
        })