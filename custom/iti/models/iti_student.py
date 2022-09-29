from odoo import models,fields,api
from odoo.exceptions import UserError

class ItiStudent(models.Model):
    _name = 'iti.student'

    name=fields.Char(required=True)
    email=fields.Char()
    birth_date=fields.Date()
    salary=fields.Float()
    tax = fields.Float(compute='calc_tax', store=True)
    address=fields.Text()
    gender=fields.Selection([
        ('m','Male'),
        ('f','Female'),
    ])
    accepted=fields.Boolean()
    level=fields.Integer()
    image=fields.Binary()
    cv=fields.Html()
    track_id=fields.Many2one("iti.track")
    track_capacity=fields.Integer(related="track_id.capacity")
    skill_ids=fields.Many2many("iti.skill")
    grade_ids=fields.One2many('student.course','student_id')
    state=fields.Selection([
        ('applied','Applied'),
        ('first','First Interview'),
        ('second','Second Interview'),
        ('passed','Passed'),
        ('rejected','Rejected'),
    ], default='applied')

    @api.onchange("gender")
    def _onchnge_gender(self):
        domain={'track_id':[]}
        if self.gender=='m':
            domain={'track_id':[('is_open','=',True)]}
            self.salary=10000
        else:
            self.salary=5000
        return {
            'warning':{
                'title':'Note That',
                'message':'you have changed the gender',
            },
            'domain':domain
        }
    def change_state(self):
        if self.state=='applied':
            self.state='first'
        elif self.state=='first':
            self.state='second'
        elif self.state in ['passed','rejected']:
            self.state='applied'

    def set_passed(self):
        self.state='passed'

    def set_rejected(self):
        self.state='rejected'

    @api.depends('salary')
    def calc_tax(self):
        for student in self:
            student.tax = student.salary * 0.20

    @api.constrains('salary')
    def check_salary(self):
        if self.salary>10000:
            raise UserError('salary is higher than 10000')

    _sql_constraints = [
        ("Unique_Name","unique(name)","name already exist"),
    ]

    @api.constrains('track_id')
    def check_capacity(self):
        # number of student in the track
        track_count=len(self.track_id.student_ids)
        track_capacity=self.track_id.capacity
        if track_count > track_capacity:
            raise UserError('track is full')



    @api.model
    def create(self, vals_list):
        name_split=vals_list['name'].split()
        vals_list['email']=f"{name_split[0][0]}{name_split[1]}@gmail.com"
        # if this email already exist for any previous student raise error
        search_students=self.search([('email','=',vals_list['email'])])
        track=self.env['iti.track'].browse(vals_list['track_id'])
        if track.is_open is False:
            raise UserError("selected track is closed")
        return super().create(vals_list)

    def write(self, vals):
        if 'name' in vals:
            name_split = vals['name'].split()
            vals['email'] = f"{name_split[0][0]}{name_split[1]}@gmail.com"
        super().write(vals)


    def unlink(self):
        for record in self:
            if record.state in ['passed', 'rejected']:
                raise UserError('you cant delete passed or rejected students')
        super(ItiStudent, self).unlink()

class ItiCourse(models.Model):
    _name = 'iti.course'

    name=fields.Char()

class StudentCourseGrade(models.Model):
    _name = 'student.course'

    student_id=fields.Many2one("iti.student")
    course_id=fields.Many2one("iti.course")
    grade=fields.Selection([
        ('g','Good'),
        ('vg','Very Good'),
    ])


