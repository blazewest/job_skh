# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Calendar - SMS",
    'version': "1.1",
    'summary': 'Send text messages as event reminders',
    'description': "Send text messages as event reminders",
    'category': 'Hidden',
    'depends': ['calendar', 'odoo_integrate_zalo','hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'views/calendar_event_views.xml',
        'views/calendar_alarm_views.xml',
        'views/zalo_image_views.xml',
        'views/zalo_file_view.xml',
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
    ],
    'auto_install': True,
    'license': 'LGPL-3',
}
