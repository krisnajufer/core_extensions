import os

import frappe
from frappe import _, get_module_path, scrub
from frappe.utils import cint

from frappe.custom.doctype.customize_form.customize_form import CustomizeForm
from frappe.modules.utils import export_customizations

class CustomizeForm(CustomizeForm):

    @frappe.whitelist()
    def save_customization(self):
        super().save_customization()
        if not self.module:
            return
        export_customizations(self.module, self.doc_type, sync_on_migrate=True)
        
@frappe.whitelist()
def export_customizations(
	module: str,
	doctype: str,
	sync_on_migrate: bool = False,
	with_permissions: bool = False,
	apply_module_export_filter: bool = False,
):
	"""Export Custom Field and Property Setter for the current document to the app folder.
	This will be synced with bench migrate"""

	sync_on_migrate = cint(sync_on_migrate)
	with_permissions = cint(with_permissions)
	apply_module_export_filter = cint(apply_module_export_filter)

	cf_filters = {"dt": doctype}
	ps_filters = {"doc_type": doctype}

	if apply_module_export_filter:
		cf_filters["module"] = module
		ps_filters["module"] = module

	if not frappe.conf.developer_mode:
		frappe.throw(_("Only allowed to export customizations in developer mode"))

	custom = {
		"custom_fields": frappe.get_all(
			"Custom Field",
			fields="*",
			filters=cf_filters,
			order_by="name",
		),
		"property_setters": frappe.get_all(
			"Property Setter",
			fields="*",
			filters=ps_filters,
			order_by="name",
		),
		"custom_perms": [],
		"links": frappe.get_all("DocType Link", fields="*", filters={"parent": doctype}, order_by="name"),
		"doctype": doctype,
		"sync_on_migrate": sync_on_migrate,
	}

	if with_permissions:
		custom["custom_perms"] = frappe.get_all(
			"Custom DocPerm", fields="*", filters={"parent": doctype}, order_by="name"
		)

	# also update the custom fields and property setters for all child tables
	for d in frappe.get_meta(doctype).get_table_fields():
		export_customizations(
			module, d.options, sync_on_migrate, with_permissions, apply_module_export_filter
		)

	if custom["custom_fields"] or custom["property_setters"] or custom["custom_perms"]:
		folder_path = os.path.join(get_module_path(module), "custom")
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)

		path = os.path.join(folder_path, scrub(doctype) + ".json")
		with open(path, "w") as f:
			f.write(frappe.as_json(custom))

		frappe.msgprint(_("Customizations for <b>{0}</b> exported to:<br>{1}").format(doctype, path))
		return path
	else:
		folder_path = os.path.join(get_module_path(module), "custom")
		path = os.path.join(folder_path, scrub(doctype) + ".json")

		# cek jika file ada lalu hapus
		if os.path.exists(path):
			os.remove(path)
			frappe.msgprint(_("Customizations for <b>{0}</b> removed from:<br>{1}").format(doctype, path))
			return path