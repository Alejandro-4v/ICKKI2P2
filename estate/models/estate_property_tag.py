from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag de Alejandro López"
    _order = "name"

    _check_unique_name = models.Constraint(
        'UNIQUE(name)',
        'The name must be unique'
    )

    name = fields.Char("Property Tag", required=True, copy=False)
    color = fields.Integer("Color Index")

    properties = fields.Many2many("estate.property", "property_type_id", string="Properties", )