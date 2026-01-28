# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # AI Configuration
    ai_enabled = fields.Boolean(
        string='Bật AI Đánh giá',
        config_parameter='project_ai_analytics.ai_enabled',
        default=True
    )
    
    ai_api_key = fields.Char(
        string='Google Gemini API Key',
        config_parameter='google.gemini.api_key',
        help='Lấy API key tại: https://aistudio.google.com/app/apikey'
    )
    
    ai_base_url = fields.Char(
        string='Base URL',
        config_parameter='project_ai_analytics.ai_base_url',
        default='https://generativelanguage.googleapis.com/v1beta',
    )
    
    ai_model = fields.Char(
        string='Model Name',
        config_parameter='project_ai_analytics.ai_model',
        default='gemini-2.5-flash',
        help='Ví dụ: gemini-2.5-flash, gemini-1.5-flash, gemini-1.5-pro'
    )
    
    ai_timeout = fields.Integer(
        string='Timeout (giây)',
        config_parameter='project_ai_analytics.ai_timeout',
        default=30,
    )

    ai_completion_threshold = fields.Integer(
        string='Ngưỡng điểm hoàn thành AI (%)',
        config_parameter='project_ai_analytics.ai_completion_threshold',
        default=80,
        help='Điểm số tối thiểu từ AI để có thể hoàn thành dự án'
    )
