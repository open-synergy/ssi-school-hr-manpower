// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_hr_manpower_planning_school.manpower_planning_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // Navigation of the base work instruction (Flow 1 of
    // ssi_hr_manpower_planning docs/manpower_planning/01-create.md): "Open the
    // Human Resource > Manpower Planning > Manpower Plannings menu."
    function openPlanningList() {
        return [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Human Resource app",
                trigger: '.o_app[data-menu-xmlid="ssi_hr.menu_root_human_resource"]',
            },
            {
                content: "Open the Manpower Planning menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_hr_manpower_planning.manpower_planning_menu"]',
            },
            {
                content: "Open the Manpower Plannings menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_hr_manpower_planning.manpower_planning_menu_item"]',
            },
            {
                // Gate on the TARGET action, not on "some list view".
                content: "Manpower Plannings list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Manpower Plannings)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ];
    }

    // IK: docs/manpower_planning/01-create.md
    tour.register(
        "ssi_hr_manpower_planning_school_manpower_planning_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Base Flow 1 -- Open the Manpower Plannings menu.
            openPlanningList(),
            [
                // Base Flow 2 -- Click the New button (14.0: "Create").
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

                // Base Flow 3 -- Department (required). Date Start and Date
                // End are filled by the academic year below.
                {
                    content: "Fill in the Department",
                    trigger: ".o_field_many2one[name='department_id'] input",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text Tour MPPS Dept",
                },
                {
                    content: "Pick the Department from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Dept)",
                    in_modal: false,
                },

                // Additional Fields -- School tab.
                {
                    content: "Open the School tab",
                    trigger: ".o_notebook .nav-link:contains(School)",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                {
                    content: "School tab is active",
                    trigger: ".o_notebook .nav-link.active:contains(School)",
                    extra_trigger: ".o_field_widget[name='school_id']",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Fill in the School",
                    trigger: ".o_field_many2one[name='school_id'] input",
                    run: "text Tour MPPS School",
                },
                {
                    content: "Pick the School from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS School)",
                    in_modal: false,
                },
                // The Curriculum is not filled by hand: it follows the
                // School, and it is checked once the record is saved.
                {
                    // Picked last on this tab: it triggers the onchange that
                    // fills Date Start and Date End.
                    content: "Fill in the Academic Year",
                    trigger: ".o_field_many2one[name='academic_year_id'] input",
                    run: "text Tour MPPS Year",
                },
                {
                    content: "Pick the Academic Year from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Year)",
                    in_modal: false,
                },

                // Additional Fields -- Teaching tab, one line.
                {
                    content: "Open the Teaching tab",
                    trigger: ".o_notebook .nav-link:contains(Teaching)",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                {
                    content: "Add a teaching line",
                    trigger:
                        ".o_field_x2many[name='teaching_ids'] .o_field_x2many_list_row_add a",
                },
                {
                    content: "Fill in the Subject",
                    trigger:
                        ".o_selected_row .o_field_many2one[name='subject_id'] input",
                    run: "text Tour MPPS Subject",
                },
                {
                    content: "Pick the Subject from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Subject)",
                    in_modal: false,
                },
                {
                    content: "Fill in the Grade",
                    trigger: ".o_selected_row .o_field_many2one[name='grade_id'] input",
                    run: "text Tour MPPS Grade",
                },
                {
                    content: "Pick the Grade from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Grade)",
                    in_modal: false,
                },
                {
                    // The teaching line counts as one needed position, so
                    // the header answers the onchange of the line with 1.
                    // That answer re-renders the list and would close the
                    // dropdown of the next input, so it gates it.
                    content: "Fill in the Classes",
                    trigger:
                        ".o_selected_row .o_field_many2manytags[name='grade_class_ids'] input",
                    extra_trigger:
                        ".o_form_view .o_field_widget[name='quantity_needed']:contains(1)",
                    run: "text Tour MPPS Class",
                },
                {
                    content: "Pick the Class from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Class)",
                    in_modal: false,
                },
                {
                    content: "Fill in the Weekly Hours per Class",
                    trigger: ".o_selected_row .o_field_widget[name='weekly_hours']",
                    extra_trigger:
                        ".o_selected_row .o_field_many2manytags[name='grade_class_ids'] .o_badge_text:contains(Tour MPPS Class)",
                    run: "text 3",
                },
                {
                    content: "Fill in the Teacher",
                    trigger:
                        ".o_selected_row .o_field_many2one[name='employee_id'] input",
                    run: "text Tour MPPS Teacher",
                },
                {
                    content: "Pick the Teacher from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Teacher)",
                    in_modal: false,
                },
                {
                    // The teacher fills the line: the header answers the
                    // onchange with 1 filled before the tab is left.
                    content: "Header counts the teaching line as filled",
                    trigger:
                        ".o_form_view .o_field_widget[name='quantity_filled']:contains(1)",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Additional Fields -- Additional Assignments tab, one line.
                {
                    // Leaving the row commits its last cell.
                    content: "Open the Additional Assignments tab",
                    trigger: ".o_notebook .nav-link:contains(Additional Assignments)",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                {
                    content: "Add an assignment line",
                    trigger:
                        ".o_field_x2many[name='assignment_ids'] .o_field_x2many_list_row_add a",
                },
                {
                    content: "Fill in the Assignment Type",
                    trigger: ".o_selected_row .o_field_many2one[name='type_id'] input",
                    run: "text Tour MPPS Type",
                },
                {
                    content: "Pick the Assignment Type from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Type)",
                    in_modal: false,
                },
                {
                    // The Category cell is only filled once the onchange of
                    // the type has answered, so it gates the next input.
                    content: "Category is filled from the Assignment Type",
                    trigger:
                        ".o_selected_row .o_field_widget[name='category']:contains(Structural)",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    // The header counts the assignment line too, so it
                    // answers the onchange of the line with 2 needed and 1
                    // filled before the next dropdown can stay open.
                    content: "Fill in the Employee",
                    trigger:
                        ".o_selected_row .o_field_many2one[name='employee_id'] input",
                    extra_trigger:
                        ".o_form_view .o_field_widget[name='quantity_needed']:contains(2)",
                    run: "text Tour MPPS Teacher",
                },
                {
                    content: "Pick the Employee from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPS Teacher)",
                    in_modal: false,
                },

                // Additional Fields -- Workload tab is read-only. Opening it
                // also commits the assignment line.
                {
                    content: "Open the Workload tab",
                    trigger: ".o_notebook .nav-link:contains(Workload)",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                {
                    content: "Workload tab is active",
                    trigger: ".o_notebook .nav-link.active:contains(Workload)",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Base Flow 6 -- Click Save.
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

                // Post-Condition -- the planning is created in Draft.
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Post-Condition -- the Curriculum was filled from the
                // School on the School tab.
                {
                    content: "Open the School tab",
                    trigger: ".o_notebook .nav-link:contains(School)",
                    extra_trigger: ".o_form_view.o_form_readonly",
                },
                {
                    content: "The Curriculum is filled from the School",
                    // The m2o shows the document number of the curriculum
                    // (name_get of the transaction mixin), not its title, and
                    // the sequence is not rolled back between tests. So the
                    // gate is "filled and pointing at a school curriculum".
                    trigger:
                        ".o_field_widget[name='curriculum_id'][href*='model=school_curriculum']:not(.o_field_empty)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/manpower_planning/17-import-teaching-assignment.md
    tour.register(
        "ssi_hr_manpower_planning_school_manpower_planning_import_teaching_assignment",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Human Resource > Manpower Planning >
            // Manpower Plannings menu.
            openPlanningList(),
            [
                // Flow 2 -- Open the draft planning, told apart by the
                // unique department name.
                {
                    content: "Open the manpower planning",
                    trigger: ".o_data_row:contains(Tour MPPI Dept) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- Click the Import from Teaching Assignment button.
                {
                    content: "Click the Import from Teaching Assignment button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_import_teaching_assignment']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Select the Academic Term. In 14.0 an in-modal
                // trigger must NOT be prefixed with ".modal"; the term field
                // only exists in the wizard.
                {
                    content: "Fill in the Academic Term",
                    trigger: ".o_field_many2one[name='academic_term_id'] input",
                    run: "text Tour MPPI Term",
                },
                {
                    content: "Pick the Academic Term from the dropdown",
                    trigger:
                        ".ui-autocomplete:visible .ui-menu-item a:contains(Tour MPPI Term)",
                    in_modal: false,
                },

                // Flow 5 -- Click Import.
                {
                    content: "Click Import",
                    trigger: ".modal-footer button[name='action_confirm']",
                },

                // Post-Condition -- the wizard closes and the Teaching tab
                // lists the imported line with its source tags.
                {
                    content: "Open the Teaching tab",
                    trigger: ".o_notebook .nav-link:contains(Teaching)",
                    extra_trigger: "body:not(:has(.modal)) .o_form_view",
                },
                {
                    content: "The imported teaching line is listed",
                    trigger:
                        ".o_field_x2many[name='teaching_ids'] .o_data_row:contains(Tour MPPI Subject)",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "The line is linked to its teaching assignment line",
                    trigger:
                        ".o_field_x2many[name='teaching_ids'] .o_data_row:contains(Tour MPPI Subject) .o_field_many2manytags[name='teaching_assignment_line_ids'] .badge:contains(Tour MPPI Class)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/manpower_planning/18-generate-teaching-from-curriculum.md
    tour.register(
        "ssi_hr_manpower_planning_school_manpower_planning_generate_curriculum",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Human Resource > Manpower Planning >
            // Manpower Plannings menu.
            openPlanningList(),
            [
                // Flow 2 -- Open the draft planning, told apart by the
                // unique department name.
                {
                    content: "Open the manpower planning",
                    trigger: ".o_data_row:contains(Tour MPPG Dept) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 3 -- Click the Generate from Curriculum button.
                {
                    content: "Click the Generate from Curriculum button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_generate_teaching_from_curriculum']",
                    extra_trigger: ".o_form_view",
                },

                // Post-Condition -- the Teaching tab lists the generated line
                // with its classes, and the line has no teacher.
                {
                    content: "Open the Teaching tab",
                    trigger: ".o_notebook .nav-link:contains(Teaching)",
                    extra_trigger: "body:not(:has(.modal)) .o_form_view",
                },
                {
                    content: "The generated teaching line is listed",
                    trigger:
                        ".o_field_x2many[name='teaching_ids'] .o_data_row:contains(Tour MPPG Subject)",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "The line has the classes of the school for the grade",
                    trigger:
                        ".o_field_x2many[name='teaching_ids'] .o_data_row:contains(Tour MPPG Subject) .o_field_many2manytags[name='grade_class_ids'] .badge:contains(Tour MPPG Class)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );
});
