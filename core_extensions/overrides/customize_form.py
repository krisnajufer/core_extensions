import frappe
from frappe.custom.doctype.customize_form.customize_form import CustomizeForm
from frappe.modules.utils import export_customizations

class CustomizeForm(CustomizeForm):

    @frappe.whitelist()
    def save_customization(self):
        super().save_customization()
        export_customizations(self.module, self.doc_type, sync_on_migrate=True)
