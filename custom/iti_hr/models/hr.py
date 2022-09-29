from odoo import fields,models

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    military_certificate = fields.Binary()
    phone2=fields.Char()

