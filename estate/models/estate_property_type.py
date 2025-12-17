from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type de Alejandro López"
    _order = "sequence, name"

    name = fields.Char("Property type", required=True, copy=False)

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    offer_count = fields.Integer(compute="_compute_offer_count", string="Offer Count")

    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )

    sequence = fields.Integer(
        string="Sequence",
        default=1,
        help="Used to order property types. Lower is better.",
    )

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)