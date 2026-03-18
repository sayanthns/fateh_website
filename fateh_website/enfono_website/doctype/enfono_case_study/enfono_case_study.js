frappe.ui.form.on("Enfono Case Study", {
    setup: function (frm) {
        frappe.call({
            method: "fateh_website.enfono_website.doctype.enfono_case_study.enfono_case_study.get_category_options",
            callback: function (r) {
                if (r.message) {
                    var options = [""].concat(r.message);
                    frm.set_df_property("category", "options", options.join("\n"));
                }
            },
        });
    },
});
