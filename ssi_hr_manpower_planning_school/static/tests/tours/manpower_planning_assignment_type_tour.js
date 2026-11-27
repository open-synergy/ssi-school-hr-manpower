odoo.define(
    "ssi_hr_manpower_planning_school.manpower_planning_assignment_type_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/manpower_planning_assignment_type/01-create.md
        tour.register(
            "ssi_hr_manpower_planning_school_manpower_planning_assignment_type_create",
            {
                test: true,
                url: "/web",
            },
            [
                // -- Flow 1 -- Open the Human Resource > Configuration > Manpower
                // Planning > Assignment Types menu.
                tour.stepUtils.showAppsMenuItem(),
                {
                    content: "Open the Human Resource app",
                    trigger:
                        '.o_app[data-menu-xmlid="ssi_hr.menu_root_human_resource"]',
                },
                {
                    content: "Open the Configuration menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_hr.menu_human_resource_configuration"]',
                },
                {
                    // "Manpower Planning" is a grouping header without action;
                    // no step for it. Go straight to the leaf.
                    content: "Open the Assignment Types menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_hr_manpower_planning_school.manpower_planning_assignment_type_menu"]',
                },
                {
                    content: "Assignment Types list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Assignment Types)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // -- Flow 2 -- Click the New button (14.0: "Create").
                {
                    content: "Click Create",
                    trigger: ".o_list_button_add",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open in edit mode",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only.
                    },
                },

                // -- Flow 3 -- Fill in the fields (Name, Code).
                {
                    content: "Enter the name",
                    trigger: ".o_form_view .o_field_widget[name='name']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR-MPPS-TYPE-CREATE",
                },
                {
                    content: "Enter the code",
                    trigger: ".o_form_view .o_field_widget[name='code']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR-MPPS-TYPE-CREATE",
                },

                // -- Flow 4 -- Open the Assignment tab.
                {
                    content: "Open the Assignment tab",
                    trigger: ".o_notebook .nav-link:contains(Assignment)",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                {
                    content: "Assignment tab is active",
                    trigger: ".o_notebook .nav-link.active:contains(Assignment)",
                    run: function () {
                        // Assertion only.
                    },
                },

                // -- Flow 5 -- Fill in the assignment details: Category, Hour
                // Basis, Default Hours. Job Position is optional and skipped.
                {
                    content: "Select the Category",
                    trigger: "select.o_field_widget[name='category']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text Picket",
                },
                {
                    content: "Select the Hour Basis",
                    trigger: "select.o_field_widget[name='hour_basis']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text Per Day",
                },
                {
                    content: "Enter the Default Hours",
                    trigger: ".o_form_view .o_field_widget[name='default_hours']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text 2",
                },

                // -- Flow 6 -- Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },

                // -- Post-Condition -- the new record is created and listed.
                {
                    content: "Back to the list",
                    trigger: ".o_control_panel .breadcrumb-item:not(.active) a",
                },
                {
                    content: "The new record is listed",
                    trigger: ".o_list_view .o_data_row:contains(TOUR-MPPS-TYPE-CREATE)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        );
    }
);
