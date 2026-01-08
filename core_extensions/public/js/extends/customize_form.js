frappe.ui.form.on("Customize Form", {
    onload_post_render(frm) {
        addFieldModule(frm)
    }
});

frappe.customize_form.set_primary_action = function (frm) {
	frm.page.set_primary_action(__("Update"), () => {
		this.update_fields_from_form_builder(frm);
		this.save_customization(frm);
	});
};

frappe.customize_form.save_customization = function (frm) {
	if (frm.doc.doc_type) {
        frm.doc.module = frm.page.get_form_values().module;
		return frm.call({
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Saving Customization..."),
			btn: frm.page.btn_primary,
			method: "save_customization",
			callback: function (r) {
				if (!r.exc) {
					frappe.customize_form.clear_locals_and_refresh(frm);
					frm.script_manager.trigger("doc_type");
				}
			},
		});
	}
};

function addFieldModule(frm){
    const $actions = frm.page.page_actions;

    const field_module = frm.page.add_field({
        label: "Module",
        fieldtype: "Link",
        fieldname: "module",
        options: "Module Def"
    }, $actions);

    $(field_module.wrapper).removeClass("col-md-2").addClass("col-md-4").addClass("pt-3");

    const $custom_actions = $actions.find('.custom-actions');
    
    if ($custom_actions.length) {
        $(field_module.wrapper).insertBefore($custom_actions);
    }
}